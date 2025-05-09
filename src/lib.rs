use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::collections::HashMap;
use std::fs::File;
use std::io::{self, BufRead, BufReader};
use std::path::Path;
use chrono::NaiveDate;

#[pyclass]
struct Market {
    prices: HashMap<String, HashMap<String, f64>>
}

#[pymethods]
impl Market {
    #[new]
    fn new() -> PyResult<Self> {
        let csv_path = "data/sample_prices.csv";
        match read_prices_from_csv(csv_path) {
            Ok(prices) => Ok(Market { prices }),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyIOError, _>(
                format!("Failed to load market data: {}", e)
            ))
        }
    }

    /// Create a market instance from a specific CSV file
    #[staticmethod]
    fn from_csv(path: &str) -> PyResult<Self> {
        match read_prices_from_csv(path) {
            Ok(prices) => Ok(Market { prices }),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyIOError, _>(
                format!("Failed to load market data from {}: {}", path, e)
            ))
        }
    }

    /// Get price for a single ticker on a specific date
    fn get_price(&self, py: Python, ticker: &str, date: &str) -> PyResult<Option<f64>> {
        Ok(self.prices.get(date)
            .and_then(|prices| prices.get(ticker).copied()))
    }

    /// Get prices for a single ticker over a date range
    fn get_ticker_prices(&self, py: Python, ticker: &str, start_date: &str, end_date: &str) -> PyResult<Py<PyDict>> {
        let result = PyDict::new(py);
        for (date, prices) in &self.prices {
            if date >= start_date && date <= end_date {
                if let Some(price) = prices.get(ticker) {
                    result.set_item(date, *price)?;
                }
            }
        }
        Ok(result.into())
    }

    /// Get prices for multiple tickers on a specific date
    fn get_prices_on_date(&self, py: Python, tickers: Vec<String>, date: &str) -> PyResult<Py<PyDict>> {
        let result = PyDict::new(py);
        if let Some(prices) = self.prices.get(date) {
            for ticker in tickers {
                if let Some(price) = prices.get(&ticker) {
                    result.set_item(ticker, *price)?;
                }
            }
        }
        Ok(result.into())
    }

    /// Get prices for multiple tickers over a date range
    fn get_prices(&self, py: Python, tickers: Vec<String>, start_date: &str, end_date: &str) -> PyResult<Py<PyDict>> {
        let result = PyDict::new(py);
        for (date, prices) in &self.prices {
            if date >= start_date && date <= end_date {
                let date_prices = PyDict::new(py);
                let mut has_prices = false;

                for ticker in &tickers {
                    if let Some(price) = prices.get(ticker) {
                        date_prices.set_item(ticker, *price)?;
                        has_prices = true;
                    }
                }

                if has_prices {
                    result.set_item(date, date_prices)?;
                }
            }
        }
        Ok(result.into())
    }

    /// Get available ticker symbols
    fn get_tickers(&self, py: Python) -> PyResult<Py<PyList>> {
        let tickers = if let Some((_, first_day)) = self.prices.iter().next() {
            first_day.keys().cloned().collect::<Vec<_>>()
        } else {
            Vec::new()
        };
        Ok(PyList::new(py, tickers).into())
    }

    /// Get available dates
    fn get_dates(&self, py: Python) -> PyResult<Py<PyList>> {
        let mut dates = self.prices.keys().cloned().collect::<Vec<_>>();
        dates.sort();
        Ok(PyList::new(py, dates).into())
    }
}

/// Read price data from a CSV file
fn read_prices_from_csv(path: &str) -> Result<HashMap<String, HashMap<String, f64>>, io::Error> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);
    let mut lines = reader.lines();

    // Parse header to get symbol names
    let header = match lines.next() {
        Some(Ok(line)) => line,
        Some(Err(e)) => return Err(e),
        None => return Err(io::Error::new(io::ErrorKind::InvalidData, "CSV file is empty")),
    };

    let symbols: Vec<&str> = header.split(',').collect();
    if symbols.is_empty() || symbols[0] != "Date" {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "CSV header must start with 'Date' followed by symbols"
        ));
    }

    // Create map for date -> symbol -> price
    let mut price_data = HashMap::new();

    // Process each line
    for line in lines {
        let line = line?;
        let values: Vec<&str> = line.split(',').collect();

        if values.len() != symbols.len() {
            return Err(io::Error::new(
                io::ErrorKind::InvalidData,
                format!("Line has {} values, expected {}", values.len(), symbols.len())
            ));
        }

        let date = values[0].to_string();
        let mut prices = HashMap::new();

        for i in 1..symbols.len() {
            let symbol = symbols[i].to_string();
            let price = match values[i].parse::<f64>() {
                Ok(p) => p,
                Err(e) => return Err(io::Error::new(
                    io::ErrorKind::InvalidData,
                    format!("Failed to parse price for {}: {}", symbol, e)
                )),
            };

            prices.insert(symbol, price);
        }

        price_data.insert(date, prices);
    }

    Ok(price_data)
}

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Market>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;
    use std::io::Write;
    use tempfile::tempdir;

    #[test]
    fn test_read_prices_from_csv() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("test_prices.csv");

        let mut file = File::create(&file_path).unwrap();
        write!(file, "Date,AAPL,XOM\n2024-01-02,184.53,98.11\n2024-01-03,183.15,98.93\n").unwrap();

        let result = read_prices_from_csv(file_path.to_str().unwrap());
        assert!(result.is_ok());

        let prices = result.unwrap();
        assert_eq!(prices.len(), 2); // Two dates

        // Check first date
        let day1 = prices.get("2024-01-02").unwrap();
        assert_eq!(day1.get("AAPL").unwrap(), &184.53);
        assert_eq!(day1.get("XOM").unwrap(), &98.11);

        // Check second date
        let day2 = prices.get("2024-01-03").unwrap();
        assert_eq!(day2.get("AAPL").unwrap(), &183.15);
        assert_eq!(day2.get("XOM").unwrap(), &98.93);
    }

    #[test]
    fn test_market_get_price() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("test_prices.csv");

        let mut file = File::create(&file_path).unwrap();
        write!(file, "Date,AAPL,XOM\n2024-01-02,184.53,98.11\n2024-01-03,183.15,98.93\n").unwrap();

        let prices = read_prices_from_csv(file_path.to_str().unwrap()).unwrap();
        let market = Market { prices };

        // Test with Python GIL
        Python::with_gil(|py| {
            // Test get_price
            let aapl_price = market.get_price(py, "AAPL", "2024-01-02").unwrap();
            assert_eq!(aapl_price, Some(184.53));

            // Test get_ticker_prices
            let aapl_prices = market.get_ticker_prices(py, "AAPL", "2024-01-01", "2024-01-31").unwrap();
            let dict = aapl_prices.as_ref(py).downcast::<PyDict>().unwrap();
            assert_eq!(dict.len(), 2);

            // Test get_prices
            let prices = market.get_prices(py, vec!["AAPL".to_string(), "XOM".to_string()],
                                          "2024-01-02", "2024-01-03").unwrap();
            let dict = prices.as_ref(py).downcast::<PyDict>().unwrap();
            assert_eq!(dict.len(), 2);
        });
    }
}
