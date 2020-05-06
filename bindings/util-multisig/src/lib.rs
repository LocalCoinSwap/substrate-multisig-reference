use pyo3::types::{PyAny, PyList, PyBytes};
use pyo3::prelude::*;
use pyo3::{wrap_pyfunction, FromPyObject};

use blake2_rfc;
use codec::{Encode};

pub struct AccountIDList([u8; 32], [u8; 32], [u8; 32]);

impl<'a> FromPyObject<'a> for AccountIDList {
    fn extract(obj: &'a PyAny) -> PyResult<Self> {
        let account_list = obj
            .downcast::<PyList>()
            .expect("Expected param to be list");

        let first = &account_list.get_item(0)
            .downcast::<PyBytes>()
            .expect("Expected a python Bytes object")
            .as_bytes();
        let mut first_address: [u8; 32] = [0u8; 32];
        first_address.clone_from_slice(first);

        let second = &account_list.get_item(1)
            .downcast::<PyBytes>()
            .expect("Expected a python Bytes object")
            .as_bytes();
        let mut second_address: [u8; 32] = [0u8; 32];
        second_address.clone_from_slice(second);

        let third = &account_list.get_item(2)
            .downcast::<PyBytes>()
            .expect("Expected a python Bytes object")
            .as_bytes();
        let mut third_address: [u8; 32] = [0u8; 32];
        third_address.clone_from_slice(third);

        Ok(AccountIDList(first_address, second_address, third_address))
    }
}


#[pyfunction]
pub fn multi_account_id(accounts: AccountIDList, threshold: u16) -> [u8; 32] {
    let magic_character: [u8; 1] = [12];
    let encoded = (b"modlpy/utilisuba", magic_character, [accounts.0, accounts.1, accounts.2], threshold).encode();
    blake2_256(&encoded)
}

/// Do a Blake2 256-bit hash and place result in `dest`.
pub fn blake2_256_into(data: &[u8], dest: &mut [u8; 32]) {
	dest.copy_from_slice(blake2_rfc::blake2b::blake2b(32, &[], data).as_bytes());
}

/// Do a Blake2 256-bit hash and return result.
pub fn blake2_256(data: &Vec<u8>) -> [u8; 32] {
	let mut r = [0; 32];
	blake2_256_into(data, &mut r);
	r
}

#[pymodule]
fn multisig(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(multi_account_id))?;
    Ok(())
}
