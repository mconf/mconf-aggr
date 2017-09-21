# Mconf-Aggregator

## Setting environment

> Note: You only have to do this once.

Before we even start, we have to make sure that the Python environment is
properly set. We highly suggest you to use a virtual environment such as one
provided by `pyenv`. For instructions on how to install `pyenv`, check
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
provided by the virtual environment. For instance, the output for the
`which pip3` command should be similar to this:

```
/home/john_doe/.pyenv/shims/pip3
```

## Dependencies

> Note: It will be soon moved to a `setup.py` file.

We are currently using the following third-party packages:

* `psycopg2` version 2.7.3.1 or later ([official site](http://initd.org/psycopg/))
* `zabbix-api` ([GitHub repository](https://github.com/gescheit/scripts/tree/master/zabbix))

They can be easily installed with:

```
pip3 install psycopg2
pip3 install zabbix-api
```

To check if the installation ran successfuly, try to import them
(in the project's root directoy):

```
$ python -c "import psycopg2"
$ python -c "import zabbix_api"
```

It should run successfuly.

## Testing

To run the unit tests, we simply call `unittest` on a test file in the `tests/`
directory.

For instance, if you want to test `aggregator_test.py`, run
(from the project's root directory):

```
$ python -m unittest tests/aggregator_test.py
```

After making any modifications in the package, please, run the corresponding
(all would be still better) tests.

For further information about `unittest`, check
[unittest's official documentation](https://docs.python.org/3/library/unittest.html).

## Documenting

We are currently using Sphinx to document our project.

Documentation is in the `docs/` directory, but it is generated mostly from the
docstrings in the Python code. The docstring format in use is the _numpydoc_.
The documentation is in _reStructuredText_ format.

_**Please, keep the docstrings always up-to-date.**_

To generate the HTML files of documentation, run (in the `docs/` directory):

```
$ make html
```

The generated code will be in the `docs/_build/html/` directory.

One simple way to navigate through these files is creating an ephemeral server
with the `SimpleHTTPServer` Python built-in module:

```
$ python -m SimpleHTTPServer
```

It will create a server on _localhost:4000_. You can check it out in
your browser.
