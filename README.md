# kusama-reference-implementation

## Local Setup

### Pre-requisites

 - Python 3.8.1 (preferred)

It is suggested to use a [`pyenv`](https://github.com/pyenv/pyenv-virtualenv) to easily manage python versions. Some of the following commands use `pyenv`.

### Configure local development setup

 - Install and activate python 3.8.1 in the root directory
   - `pyenv install 3.8.1`
   - `pyenv virtualenv 3.8.1 ksmref`
   - `pyenv local ksmref`
 - Install precommit hook
   - `pre-commit install`
 - Install project requirements
   - `pip install -r requirements.txt`

You're all set to hack!

Before making changes, let's ensure tests run successfully on local.

### Running Tests

 - Run all tests with coverage
   - `coverage run -m pytest -v`
 - Show report in terminal
   - `coverage report -m`

### Compiling Rust bindings (and auto-run tests afterwards)
```
./build.sh
```

# Note: don't use any of the addresses in this repo with funds you care about, as the private keys are public knowledge
