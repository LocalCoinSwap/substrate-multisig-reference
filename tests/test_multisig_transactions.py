import unittest

from helpers.keys import get_addr_from_seed
from helpers.keys import get_escrow_address


class TestStandardTrade(unittest.TestCase):
    def test_standard_trade(self):
        # Everything else can be created from this
        buyer_seed = "64c29cbfc0cec793d1c62a5d80261aa8a1c03535379cedbb0601c1f89ad2271e"
        seller_seed = "8b3585743475df08238ff09c401ff8639171c9ad2584045f4b23a5e4f5e326f8"
        admin_seed = "2cf02efa64eb4ba75fa2f42f69dcf5548e821f1e852e2b26aa1b09d5eda0065a"

        buyer_addr = get_addr_from_seed(buyer_seed)
        seller_addr = get_addr_from_seed(seller_seed)
        admin_addr = get_addr_from_seed(admin_seed)

        escrow_addr = get_escrow_address([buyer_addr, seller_addr, admin_addr])
        print(escrow_addr)
        """
        Reference transaction for funding escrow:
          'https://polkascan.io/pre/kusama/transaction/'
          '0xe2ba04076bf2e533ec9554e10251fd911d3a7135aa82e35921131a445b82eb60'
        """
        """
        [{
          'valueRaw': '840400',
          'extrinsic_length': 142,
          'version_info': '84',
          'account_length': 'ff',
          'account_id': 'f68a66c0cd540d7e6ba34d3fa67b40e5eea07ea891265a39e064d39a2375aa33',
          'account_index': None,
          'account_idx': None,
          'signature': '9804257c35c4cbeb286c8e5313e8da9dca3b8744bddfdfcbff028137ec6f0e6dcbba9a0662ccacd5a72c48290226df99b0ab798be50c0049a80e830828fc2e83',
          'extrinsic_hash': 'e2ba04076bf2e533ec9554e10251fd911d3a7135aa82e35921131a445b82eb60',
          'call_code': '0400',
          'call_function': 'transfer',
          'call_module': 'balances',
          'nonce': 0,
          'era': '1502',
          'tip': 0,
          'params': [{
            'name': 'dest',
            'type': 'Address',
            'value': '0xced7f08d300980bb3a6bf633b97c49b9b2c517bf8a0d4f5a8c831c46294351fc',
            'valueRaw': ''
          },
          {
            'name': 'value',
            'type': 'Compact<Balance>',
            'value': 90000000000,
            'valueRaw': '0700046bf414'
          }]
        }]
        """

        """
        Reference transaction for first approve multi:
          'https://polkascan.io/pre/kusama/transaction/'
          '0x59f93e72fb486d45b3f983a1eb9feb21952bd7f47338a278edde62cb55870c7f'
        """
        """
        [{
          'valueRaw': '841802',
          'extrinsic_length': 282,
          'version_info': '84',
          'account_length': 'ff',
          'account_id': 'ecd3f5b7c4bb4671f9b645b73561a0894550d30d13e85a39e6cafb097448404d',
          'account_index': None,
          'account_idx': None,
          'signature': '04d05493d2d4c10d4437f206e0286745162077f2d985416166c37d1df576d405903ee43c9442dd34dfa5a3e4e7a302b2f96ca605dcb01f4572af14624e7b6287',
          'extrinsic_hash': '59f93e72fb486d45b3f983a1eb9feb21952bd7f47338a278edde62cb55870c7f',
          'call_code': '1802',
          'call_function': 'as_multi',
          'call_module': 'utility',
          'nonce': 4,
          'era': 'd501',
          'tip': 0,
          'params': [
            {
              'name': 'threshold',
              'type': 'u16',
              'value': 2,
              'valueRaw': '0200'
            },
            {
              'name': 'other_signatories',
              'type': 'Vec<AccountId>',
              'value': [
                '0x026cb1657e60212226cc8001b9c7eece72e58c5a218138ee93797a8ce38a1317',
                '0xf68a66c0cd540d7e6ba34d3fa67b40e5eea07ea891265a39e064d39a2375aa33'
              ],
              'valueRaw': ''
            },
            {
              'name': 'maybe_timepoint',
              'type': 'Option<Timepoint<BlockNumber>>',
              'value': None,
              'valueRaw': '00'
            },
            {
              'name': 'call',
              'type': 'Box<Call>',
              'value': {
                'call_index': '1802',
                'call_function': 'as_multi',
                'call_module': 'Utility',
                'call_args': [
                  {
                    'name': 'threshold',
                    'type': 'u16',
                    'value': 2,
                    'valueRaw': '0200'
                  },
                  {
                    'name': 'other_signatories',
                    'type': 'Vec<AccountId>',
                    'value': [
                      '0x026cb1657e60212226cc8001b9c7eece72e58c5a218138ee93797a8ce38a1317',
                      '0xf68a66c0cd540d7e6ba34d3fa67b40e5eea07ea891265a39e064d39a2375aa33'
                    ],
                    'valueRaw': ''
                  },
                  {
                    'name': 'maybe_timepoint',
                    'type': 'Option<Timepoint<BlockNumber>>',
                    'value': None,
                    'valueRaw': '00'
                  },
                  {
                    'name': 'call',
                    'type': 'Box<Call>',
                    'value': {
                      'call_index': '0400',
                      'call_function': 'transfer',
                      'call_module': 'Balances',
                      'call_args': [
                        {
                          'name': 'dest',
                          'type': 'Address',
                          'value': '0x026cb1657e60212226cc8001b9c7eece72e58c5a218138ee93797a8ce38a1317',
                          'valueRaw': ''
                        },
                        {
                          'name': 'value',
                          'type': 'Compact<Balance>',
                          'value': 20000000000,
                          'valueRaw': '0700c817a804'
                        }
                      ]
                    },
                    'valueRaw': '0400'
                  }
                ]
              },
              'valueRaw': '1802'
            }
          ]
        }]
        """

        """
        Reference transaction for second approve multi:
          'https://polkascan.io/pre/kusama/transaction/'
          '0x7926df35017923ff78ac4002a03cfa963c4ad8e8fba0b4fdfaacc16bcde9001f'
        """
        """
        [{
          'valueRaw': '841802',
          'extrinsic_length': 282,
          'version_info': '84',
          'account_length': 'ff',
          'account_id': 'ecd3f5b7c4bb4671f9b645b73561a0894550d30d13e85a39e6cafb097448404d',
          'account_index': None,
          'account_idx': None,
          'signature': '04d05493d2d4c10d4437f206e0286745162077f2d985416166c37d1df576d405903ee43c9442dd34dfa5a3e4e7a302b2f96ca605dcb01f4572af14624e7b6287',
          'extrinsic_hash': '59f93e72fb486d45b3f983a1eb9feb21952bd7f47338a278edde62cb55870c7f',
          'call_code': '1802',
          'call_function': 'as_multi',
          'call_module': 'utility',
          'nonce': 4,
          'era': 'd501',
          'tip': 0,
          'params': [
            {
              'name': 'threshold',
              'type': 'u16',
              'value': 2,
              'valueRaw': '0200'
            },
            {
              'name': 'other_signatories',
              'type': 'Vec<AccountId>',
              'value': [
                '0x026cb1657e60212226cc8001b9c7eece72e58c5a218138ee93797a8ce38a1317',
                '0xf68a66c0cd540d7e6ba34d3fa67b40e5eea07ea891265a39e064d39a2375aa33'
              ],
              'valueRaw': ''
            },
            {
              'name': 'maybe_timepoint',
              'type': 'Option<Timepoint<BlockNumber>>',
              'value': None,
              'valueRaw': '00'
            },
            {
              'name': 'call',
              'type': 'Box<Call>',
              'value': {
                'call_index': '1802',
                'call_function': 'as_multi',
                'call_module': 'Utility',
                'call_args': [
                  {
                    'name': 'threshold',
                    'type': 'u16',
                    'value': 2,
                    'valueRaw': '0200'
                  },
                  {
                    'name': 'other_signatories',
                    'type': 'Vec<AccountId>',
                    'value': [
                      '0x026cb1657e60212226cc8001b9c7eece72e58c5a218138ee93797a8ce38a1317',
                      '0xf68a66c0cd540d7e6ba34d3fa67b40e5eea07ea891265a39e064d39a2375aa33'
                    ],
                    'valueRaw': ''
                  },
                  {
                    'name': 'maybe_timepoint',
                    'type': 'Option<Timepoint<BlockNumber>>',
                    'value': None,
                    'valueRaw': '00'
                  },
                  {
                    'name': 'call',
                    'type': 'Box<Call>',
                    'value': {
                      'call_index': '0400',
                      'call_function': 'transfer',
                      'call_module': 'Balances',
                      'call_args': [
                        {
                          'name': 'dest',
                          'type': 'Address',
                          'value': '0x026cb1657e60212226cc8001b9c7eece72e58c5a218138ee93797a8ce38a1317',
                          'valueRaw': ''
                        },
                        {
                          'name': 'value',
                          'type': 'Compact<Balance>',
                          'value': 20000000000,
                          'valueRaw': '0700c817a804'
                        }
                      ]
                    },
                    'valueRaw': '0400'
                  }
                ]
              },
              'valueRaw': '1802'
            }
          ]
        }]
        """

        """
        Reference transaction for buyer claiming escrow:
          'https://polkascan.io/pre/kusama/transaction/'
          '0xa94b3180ef3f23d2206fc1954961b1bb5fa1f718c0399668ffbcecfa221a335d'
        """
        """
        [{
          'valueRaw': '841802',
          'extrinsic_length': 220,
          'version_info': '84',
          'account_length': 'ff',
          'account_id': '026cb1657e60212226cc8001b9c7eece72e58c5a218138ee93797a8ce38a1317',
          'account_index': None,
          'account_idx': None,
          'signature': '709804955bcbed7452a20cbc67ac5ccea136aab1c33491d5d898461d7258c909317db8775ba5314983d4e5971fcbbd29d1937ea5768bfd0129dcc86aee233d85',
          'extrinsic_hash': 'a94b3180ef3f23d2206fc1954961b1bb5fa1f718c0399668ffbcecfa221a335d',
          'call_code': '1802',
          'call_function': 'as_multi',
          'call_module': 'utility',
          'nonce': 17,
          'era': '5503',
          'tip': 0,
          'params': [
            {
              'name': 'threshold',
              'type': 'u16',
              'value': 2,
              'valueRaw': '0200'
            },
            {
              'name': 'other_signatories',
              'type': 'Vec<AccountId>',
              'value': [
                '0xecd3f5b7c4bb4671f9b645b73561a0894550d30d13e85a39e6cafb097448404d',
                '0xf68a66c0cd540d7e6ba34d3fa67b40e5eea07ea891265a39e064d39a2375aa33'
              ],
              'valueRaw': ''
            },
            {
              'name': 'maybe_timepoint',
              'type': 'Option<Timepoint<BlockNumber>>',
              'value': {
                'height': 2205071,
                'index': 3
              },
              'valueRaw': '01'
            },
            {
              'name': 'call',
              'type': 'Box<Call>',
              'value': {
                'call_index': '0400',
                'call_function': 'transfer',
                'call_module': 'Balances',
                'call_args': [
                  {
                    'name': 'dest',
                    'type': 'Address',
                    'value': '0x026cb1657e60212226cc8001b9c7eece72e58c5a218138ee93797a8ce38a1317',
                    'valueRaw': ''
                  },
                  {
                    'name': 'value',
                    'type': 'Compact<Balance>',
                    'value': 20000000000,
                    'valueRaw': '0700c817a804'
                  }
                ]
              },
              'valueRaw': '0400'
            }
          ]
        }]
        """
