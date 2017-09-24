# Mconf-Aggregator

## Python version

> Note: You only have to do this once.

This project is meant to work with version 3.6.0 of Python. Before we even start,
we have to make sure that the right version is set. We highly suggest you to use
a version manager such as `pyenv`. For instructions on how to
install `pyenv`, check
[pyenv's official documentation](https://github.com/pyenv/pyenv#installation).

> Note: Don't forget to run `source ~/.bashrc` after installing `pyenv`.

Once `pyenv` is installed, do the following (considering you're in the
project's root directory):

```
$ pyenv install 3.6.0
$ pyenv local 3.6.0
```

There should be now a file called `.python-version` with the content '_3.6.0_'.
It is always good to check if the Python version has switched correctly:

```
$ python --version
```

You should see an output like this:

```
Python 3.6.0
```

From now on, every Python-related command you use in this project should be
provided by `pyenv`. For instance, the output for the `which pip3` command should be similar to this:

```
/home/john_doe/.pyenv/shims/pip3
```

When running a script in the project, call Python explicitly as in `python main.py`.
**Do not** make the script executable and then call it directly. The reason for
this is that calling it explicitly will use the Python version as defined by `pyenv` as expected.
If you run the script as an executable, it will check for system's Python
(possibly with the wrong version).

## Setup.py

Although this package is not distributed by _Distutils_ (or available on _PyPI_),
it does come with a `setup.py` script. It makes developing, testing, and
(maybe in future) distributing easier.

To install the package for development:

```
$ python setup.py develop
```

To really install the package:

```
$ python setup.py install
```

To run all tests in the `tests/` directory:

```
$ python setup.py test
```

Other commands are also available. Check this
[Getting Started With setuptools and setup.py](https://pythonhosted.org/an_example_pypi_project/setuptools.html).

## Dependencies

We are currently using the following third-party packages:

* `psycopg2` version 2.7.3.1 or later ([official site](http://initd.org/psycopg/))
* `zabbix-api` ([GitHub repository](https://github.com/gescheit/scripts/tree/master/zabbix))
* `sphinx` version 1.6.3 or later ([official site](http://www.sphinx-doc.org/en/stable/))

They can be easily installed with:

```
$ pip3 install psycopg2
$ pip3 install zabbix-api
$ pip3 install sphinx
```

To check if the installation ran successfuly, try to import them
(in the project's root directoy):

```
$ python -c "import psycopg2"
$ python -c "import zabbix_api"
$ python -c "import sphinx"
```

It should run successfuly.

> Note: _Sphinx_ is actually used to generate documentation. It makes little
sense to import it.

## Testing

We use the standard `unittest` package to run tests. All tests go in the
`tests/` directory.

For further information about `unittest`, check
[unittest's official documentation](https://docs.python.org/3/library/unittest.html).

### Running individual tests

To run the unit tests, we simply call `unittest` on a test file in the
`tests/` directory.

For instance, if you want to test `aggregator_test.py`, run
(from the project's root directory):

```
$ python -m unittest tests/aggregator_test.py
```

After making any modifications in the package, please, run the
corresponding (all would be still better) tests.

### Running test suites

You can run multiple test modules, known as _test suite_, through
the `test_suites.py` script. Test suites are intended to group together tests
that are related to each other, for instance, by functionality.

In order to create a new test suite, add the test
suite name and a list of existing modules (from `tests/`) in the `test_suites`
field of `config_tests.json`.

For example, to run the test suite _aggregator_, do (from `tests/` directory):

```
$ python test_suites.py aggregator
```

To run all test suites in `config_tests.json`, just suppress the test suite:

```
$ python test_suites.py
```

### Running all tests with `setup.py`

As said in [Setup.py](#setup.py), you can run all tests in the `tests/` directory
by running:

```
$ python setup.py test
```

## Documenting

We are currently using _Sphinx_ to document our project.

Documentation is in the `docs/` directory, but it is generated mostly from the
docstrings in the Python code. The docstring format in use is the _numpydoc_.
The documentation is in _reStructuredText_ format.

_**Please, keep the docstrings always up-to-date.**_

To generate the HTML files of documentation, run (in the `docs/` directory):

```
$ make html
```

The generated code will be in the `docs/_build/html/` directory.

One simple way to navigate through these files is creating an ephemeral server with
the `SimpleHTTPServer` Python built-in module. From the `docs/_build/html/` directory, run:

```
$ python -m SimpleHTTPServer
```

It will create a server on _localhost:4000_. You can check it out in
your browser.
