# Backend for NLQX

To work on this create a virtual environment:

```sh
python -m venv .venv
```

Activate the virtual environment:

```sh
source .venv/bin/activate
```

Install the dependencies:

```sh
pip install -r requirements.txt
```

Change into the executor directory and install the executor package in editable mode:

```sh
cd executor
pip install -e .
```

To run the tests:

```sh
python -m unittest discover -s tests
```
