use pyo3::prelude::*;
use pyo3::{wrap_pyfunction};
// use pyo3::types::PyBytes;

use bip39::{Mnemonic, Language};
use hmac::Hmac;
use pbkdf2::pbkdf2;
use sha2::Sha512;

#[pyfunction]
pub fn bip39_to_mini_secret(phrase: &str, password: &str) -> PyResult<Vec<u8>> {
	let salt = format!("mnemonic{}", password);
	let mnemonic = Mnemonic::from_phrase(phrase, Language::English).unwrap();
	let mut result = [0u8; 64];

	pbkdf2::<Hmac<Sha512>>(mnemonic.entropy(), salt.as_bytes(), 2048, &mut result);

	Ok(result[..32].to_vec())
}

#[pymodule]
fn bip39(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(bip39_to_mini_secret))?;

    Ok(())
}
