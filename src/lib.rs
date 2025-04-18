use pyo3::prelude::*;

#[pyfunction]
fn get_prices(symbols: Vec<String>, start_date: String, end_date: String) -> PyResult<()> {
    println!(
        "Called get_prices for {} symbols from {} to {}",
        symbols.len(),
        start_date,
        end_date
    );

    Ok(())
}

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_prices, m)?)?;
    Ok(())
}
