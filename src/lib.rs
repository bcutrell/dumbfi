use pyo3::prelude::*;
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

#[pyclass]
struct Market {
    prices: Arc<Mutex<HashMap<String, HashMap<String, f64>>>>
}

#[pymethods]
impl Market {
    #[new]
    fn new() -> Self {
        let mut prices = HashMap::new();
        let mut prices_20240101 = HashMap::new();
        prices_20240101.insert("AAPL".to_string(), 187.35);
        prices_20240101.insert("MSFT".to_string(), 412.67);
        prices_20240101.insert("GOOGL".to_string(), 178.42);
        prices_20240101.insert("AMZN".to_string(), 196.75);
        prices.insert("2024-01-01".to_string(), prices_20240101);

        Market {
            prices: Arc::new(Mutex::new(prices))
        }
    }

    fn get_price(&self, date: &str, ticker: &str) -> Option<f64> {
         let prices_lock = self.prices.lock().ok()?;
        prices_lock.get(date)?.get(ticker).copied()
    }
}

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Market>()?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_get_price() {
        let market = Market::new();
        // valid prices
        assert_eq!(market.get_price("2024-01-01", "AAPL"), Some(187.35));
        assert_eq!(market.get_price("2024-01-01", "MSFT"), Some(412.67));
        assert_eq!(market.get_price("2024-01-01", "GOOGL"), Some(178.42));
        assert_eq!(market.get_price("2024-01-01", "AMZN"), Some(196.75));

        // invalid prices
        assert_eq!(market.get_price("2024-01-02", "AAPL"), None);
        assert_eq!(market.get_price("2024-01-01", "META"), None);
    }
}
