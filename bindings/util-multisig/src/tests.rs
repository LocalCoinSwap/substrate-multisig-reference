// Tests for the multi-sig utilities

#![cfg(test)]
use super::*;

#[test]
fn basic_use_of_blake_hashing() {
    let id = multi_account_id(&[1, 2, 3][..], 2);
    assert_eq!(id, 8876541760889984835)
}

// #[test]
// fn basic_use_of_gen_multi_account() {
//     let id = gen_multi_account(AccountID{&[1, 2, 3]}, 2);
//     assert_eq!(id, 8876541760889984835)
// }
