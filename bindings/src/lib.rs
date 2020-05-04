use pyo3::exceptions;
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyBytes, PyTuple};
use pyo3::{wrap_pyfunction, FromPyObject, IntoPy, PyObject};
use schnorrkel::{MiniSecretKey, ExpansionMode};

pub struct Seed([u8; 32]);
pub struct Keypair([u8; 32], [u8; 64]);

#[pyfunction]
fn pair_from_seed(seed: Seed) -> PyResult<Keypair> {
    let k = MiniSecretKey::from_bytes(&seed.0).expect("32 bytes can always build a key; qed");
    let kp = k.expand_to_keypair(ExpansionMode::Ed25519);

    Ok(Keypair(kp.public.to_bytes(), kp.secret.to_bytes()))
}

/// This module is a python module implemented in Rust.
#[pymodule]
fn wasm_crypto(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(pair_from_seed))?;

    Ok(())
}

impl<'a> FromPyObject<'a> for Seed {
    fn extract(obj: &'a PyAny) -> PyResult<Self> {
        let seed = obj
            .downcast::<PyBytes>()
            .map_err(|_| PyErr::new::<exceptions::TypeError, _>("Expected a bytestring"))?;

        if seed.as_bytes().len() != 32 {
            return Err(PyErr::new::<exceptions::IndexError, _>(
                "Expected seed with length: 32",
            ));
        }

        // Convert bytes to fixed width array
        let mut fixed: [u8; 32] = Default::default();
        fixed.copy_from_slice(seed.as_bytes());
        Ok(Seed(fixed))
    }
}

impl IntoPy<PyObject> for Keypair {
    fn into_py(self, py: Python) -> PyObject {
        let secret = PyBytes::new(py, &self.0);
        let public = PyBytes::new(py, &self.1);

        PyTuple::new(py, vec![secret, public]).into_py(py)
    }
}
