use pyo3::prelude::*;
use std::collections::HashMap;

pub struct Market {
    prices: HashMap<String, HashMap<String, f64>>,
}

impl Market {
    pub fn new() -> Self {
        Market {
            prices: HashMap::new(),
        }
    }

    pub fn read_prices(&mut self, csv_path: &str) -> Result<(), String> {
        let mut rdr = csv::Reader::from_path(csv_path)
            .map_err(|e| format!("Failed to read CSV file '{}': {}", csv_path, e))?;

        let headers = rdr.headers()
            .map_err(|e| format!("Failed to read CSV headers: {}", e))?;

        let tickers: Vec<String> = headers.iter()
            .skip(1)
            .map(|s| s.to_string())
            .collect();

        let mut new_prices = HashMap::new();

        for (row_num, result) in rdr.records().enumerate() {
            let record = result
                .map_err(|e| format!("Failed to read CSV row {}: {}", row_num + 2, e))?;

            if record.is_empty() {
                return Err(format!("Row {} is empty", row_num + 2));
            }

            let date = record[0].to_string();
            let mut day_prices = HashMap::new();

            for (i, ticker) in tickers.iter().enumerate() {
                let field_index = i + 1;
                if field_index < record.len() {
                    if let Ok(price) = record[field_index].parse::<f64>() {
                        day_prices.insert(ticker.clone(), price);
                    }
                }
            }

            if !day_prices.is_empty() {
                new_prices.insert(date, day_prices);
            }
        }

        self.prices = new_prices;
        Ok(())
    }

    pub fn get_price(&self, date: &str, ticker: &str) -> Option<f64> {
        self.prices.get(date)?.get(ticker).copied()
    }

    pub fn get_all_dates(&self) -> Vec<String> {
        let mut dates: Vec<String> = self.prices.keys().cloned().collect();
        dates.sort();
        dates
    }

    pub fn get_tickers_for_date(&self, date: &str) -> Vec<String> {
        if let Some(day_prices) = self.prices.get(date) {
            let mut tickers: Vec<String> = day_prices.keys().cloned().collect();
            tickers.sort();
            tickers
        } else {
            Vec::new()
        }
    }
}

// Python wrapper - handles PyO3 integration
#[pyclass]
pub struct PyMarket {
    inner: Market,
}

#[pymethods]
impl PyMarket {
    #[new]
    fn new() -> Self {
        PyMarket {
            inner: Market::new(),
        }
    }

    fn read_prices(&mut self, csv_path: String) -> PyResult<()> {
        self.inner.read_prices(&csv_path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e))
    }

    fn get_price(&self, date: String, ticker: String) -> Option<f64> {
        self.inner.get_price(&date, &ticker)
    }

    fn get_all_dates(&self) -> Vec<String> {
        self.inner.get_all_dates()
    }

    fn get_tickers_for_date(&self, date: String) -> Vec<String> {
        self.inner.get_tickers_for_date(&date)
    }
}

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyMarket>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;
    use std::io::Write;
    use tempfile::TempDir;

    // Helper function to create a test CSV file
    fn create_test_csv(content: &str) -> (TempDir, String) {
        let temp_dir = TempDir::new().unwrap();
        let file_path = temp_dir.path().join("test_prices.csv");
        let mut file = File::create(&file_path).unwrap();
        writeln!(file, "{}", content).unwrap();
        (temp_dir, file_path.to_string_lossy().to_string())
    }

    #[test]
    fn test_new_market_is_empty() {
        let market = Market::new();
        assert_eq!(market.get_price("2024-01-01", "AAPL"), None);
        assert_eq!(market.get_price("2024-01-01", "MSFT"), None);
    }

    #[test]
    fn test_read_prices_valid_csv() {
        let csv_content = "Date,AAPL,MSFT,GOOGL\n2024-01-01,187.35,412.67,178.42\n2024-01-02,185.50,410.25,180.10";
        let (_temp_dir, file_path) = create_test_csv(csv_content);
        let mut market = Market::new();
        let result = market.read_prices(&file_path);
        assert!(result.is_ok());

        assert_eq!(market.get_price("2024-01-01", "AAPL"), Some(187.35));
        assert_eq!(market.get_price("2024-01-01", "MSFT"), Some(412.67));
        assert_eq!(market.get_price("2024-01-01", "GOOGL"), Some(178.42));
        assert_eq!(market.get_price("2024-01-02", "AAPL"), Some(185.50));
        assert_eq!(market.get_price("2024-01-02", "MSFT"), Some(410.25));
        assert_eq!(market.get_price("2024-01-02", "GOOGL"), Some(180.10));
    }

    #[test]
    fn test_read_prices_with_missing_data() {
        // Missing MSFT 2024-01-01 and GOOGL 2024-01-02
        let csv_content = "Date,AAPL,MSFT,GOOGL\n2024-01-01,187.35,,178.42\n2024-01-02,185.50,410.25,"; 
        let (_temp_dir, file_path) = create_test_csv(csv_content);
        let mut market = Market::new();
        let result = market.read_prices(&file_path);
        assert!(result.is_ok());

        // Valid prices should be loaded
        assert_eq!(market.get_price("2024-01-01", "AAPL"), Some(187.35));
        assert_eq!(market.get_price("2024-01-01", "GOOGL"), Some(178.42));
        assert_eq!(market.get_price("2024-01-02", "AAPL"), Some(185.50));
        assert_eq!(market.get_price("2024-01-02", "MSFT"), Some(410.25));

        // Missing prices should return None
        assert_eq!(market.get_price("2024-01-01", "MSFT"), None);
        assert_eq!(market.get_price("2024-01-02", "GOOGL"), None);
    }

    #[test]
    fn test_read_prices_replaces_existing_data() {
        let csv_content1 = "Date,AAPL,MSFT\n2024-01-01,100.0,200.0";
        let (_temp_dir1, file_path1) = create_test_csv(csv_content1);
        let csv_content2 = "Date,AAPL,GOOGL\n2024-01-02,150.0,250.0";
        let (_temp_dir2, file_path2) = create_test_csv(csv_content2);
        let mut market = Market::new();

        market.read_prices(&file_path1).unwrap();
        assert_eq!(market.get_price("2024-01-01", "AAPL"), Some(100.0));
        assert_eq!(market.get_price("2024-01-01", "MSFT"), Some(200.0));

        // Load second CSV - should replace all data
        market.read_prices(&file_path2).unwrap();
        assert_eq!(market.get_price("2024-01-01", "AAPL"), None); // Old data gone
        assert_eq!(market.get_price("2024-01-01", "MSFT"), None); // Old data gone
        assert_eq!(market.get_price("2024-01-02", "AAPL"), Some(150.0)); // New data
        assert_eq!(market.get_price("2024-01-02", "GOOGL"), Some(250.0)); // New data
    }

    #[test]
    fn test_read_prices_nonexistent_file() {
        let mut market = Market::new();
        let result = market.read_prices("nonexistent_file.csv");
        assert!(result.is_err());
        // still can use the market (it remains empty)
        assert_eq!(market.get_price("2024-01-01", "AAPL"), None);
    }

    #[test]
    fn test_read_prices_invalid_csv_format() {
        let csv_content = "Not,A,Valid,CSV\nFormat"; // Missing proper structure
        let (_temp_dir, file_path) = create_test_csv(csv_content);
        let mut market = Market::new();
        let result = market.read_prices(&file_path);

        match result {
            Ok(_) => {
                // If it succeeds, there should be no valid price data
                assert_eq!(market.get_price("Not", "A"), None);
            }
            Err(_) => {
                // If it fails, that's also acceptable
            }
        }
    }

}
