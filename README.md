# Mconf-Aggregator

* **Current version**: `0.0.2`

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
$ pyenv rehash
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

From now on, every Python-related command you use in this project (outside a virtual
environment, see below) should be provided by `pyenv`.
For instance, the output for the `which pip3` command should be similar to this:

```
/home/john_doe/.pyenv/shims/pip3
```

When running a script in the project, call Python explicitly as in `python main.py`.
**Do not** make the script executable and then call it directly. The reason for
this is that calling it explicitly will use the Python version as defined by `pyenv` as expected.
If you run the script as an executable, it will check for system's Python
(possibly with the wrong version).

> Troubleshooting: If you are having problems with pyenv, make sure you have the
following line towards the end of your `.bashrc` or `bash_profile` file: `eval "$(pyenv init -)"`

## Virtual environment

In order to keep Python's version and related libraries under control, we use
virtual environments as provided by `venv` (builtin module in Python since 3.4).
It is a pretty common pattern in development with Python.

If you don't have a virtual envoriment directory set yet, create one and
set `venv` to use it:

```
$ mkdir venv
$ python -m venv ./venv
```

> Note: Remember to add this new directory to `.gitignore`.

To activate the virtual environment, run:

```
$ source ./venv/bin/activate
```

It should now include a `(venv)` string at the beginning of your prompt. It
makes clear that you are running a virtual environment and so all your Python
commands will be provided by `venv`.

From now on, every Python-related command you use in this project should be
provided by `venv`. For instance, the output for the `which pip3` command should be similar to this:

```
/home/john_doe/myproject/venv/bin/pip3
```

When running a script in the project, call Python explicitly as in `python main.py`.
**Do not** make the script executable and then call it directly. The reason for
this is that calling it explicitly will use the Python version as defined by `venv` as expected.
If you run the script as an executable, it will check for system's Python
(possibly with the wrong version).

To deactivate the session, simply run:

```
$ deactivate
```

To save the current dependencies, run:

```
$ pip freeze > requirements.txt
```

To install the packages needed for development, run:

```
$ pip install -r requirements.txt
```

## Dependencies

We are currently using the following third-party packages:

* `psycopg2` version 2.7.3.1 or later ([official site](http://initd.org/psycopg/))
* `zabbix-api` ([GitHub repository](https://github.com/gescheit/scripts/tree/master/zabbix))
* `sphinx` version 1.6.3 or later ([official site](http://www.sphinx-doc.org/en/stable/))
* `sqlalchemy` version 1.2.0b2 or later ([official site](https://www.sqlalchemy.org/))

They can be easily installed with:

```
$ pip3 install psycopg2
$ pip3 install zabbix-api
$ pip3 install sphinx
$ pip3 install sqlalchemy
```

To check if the installation ran successfuly, try to import them
(in the project's root directoy):

```
$ python -c "import psycopg2"
$ python -c "import zabbix_api"
$ python -c "import sphinx"
$ python -c "import sqlalchemy"
```

It should run successfuly.

> Note: _Sphinx_ is actually used to generate documentation. It makes little
sense to import it.

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

> Note: Before proceeding, you may need to install it in develop mode with
the command shown above. Some commands below may not work correctly as they fail
to find the `mconf_aggr` package.

## Testing

We use the standard `unittest` package to run tests. All tests go in the
`tests/` directory with the filename pattern `*_test.py`. The main script for
tests is `tests.py` in the project's root directory and its configuration
file is `config/tests.json`.

> Note: After making any modifications in the package, please, run the
corresponding (all would be still better) tests.

For further information about `unittest`, check
[unittest's official documentation](https://docs.python.org/3/library/unittest.html).

### Running individual tests

If you want to test, say `aggregator_test.py`, you have two approaches:

* You can run individual tests by passing the test filename (_with_ extension) to
the `tests.py` script as follows:

```
$ python tests.py aggregator_test.py
```

* Alternatively, you can simply call `unittest` on the test file in the
`tests/` directory.

```
$ python -m unittest tests/aggregator_test.py
```

### Running test suites

You can also run multiple test modules, known as _test suite_, through
the `tests.py` script. Test suites are intended to group together tests
that are related to each other, for instance, by functionality.

In order to create a new test suite, add the test
suite name and a list of existing modules (from `tests/`) in the `test_suites`
field of `config/tests.json`.

For example, to run the test suite _aggregator_, do:

```
$ python tests.py aggregator
```

### Running all tests

To run all tests, you also have two approaches:

* The recommended way to run all test files in `tests/` is by calling the
`tests.py` script with no arguments:

```
$ python tests.py
```

* Alternatively, as said in [Setup.py](#setup.py), you can also run all tests in
the `tests/` directory by running:

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
$ python -m http.server
```

It will create a server on _localhost:8000_. You can check it out in
your browser.

## Docker

We also provide two Dockerfiles to build images of the applications. They are built
upon the [python:3.6-alpine](https://hub.docker.com/_/python/) image.

Refer to the Makefile section below to further details on the recommended way to run Docker.

### Docker tags

An important subject is how to tag Docker images. Here we use the following patterns:

Local development images receive tag:

* `<app>-<full_version>-<revision>`

Stable releases receive tags:

* `<app>-<number_version>`
* `<app>-<major_version>`
* `<app>-<revision>`
* `<app>-latest`

Unstable releases receive tags:

* `<app>-<full_version>`
* `<app>-<revision>`

For instance, if the zabbix app is at version 0.0.2-pre-alpha and current commit hash is 36fba5,
local tags we be built as:

* `zabbix-0.0.2-pre-alpha-36fba5`

The stable release will have tags:

* `zabbix-0.0.2`
* `zabbix-0`
* `zabbix-36fba5`
* `zabbix-latest`

And the unstable release will have tags:

* `zabbix-0.0.2-pre-alpha`
* `zabbix-36fba5`

> The version is obtained from the `.version` file.

### Developing with Docker

You can also develop using a single Docker image for both webhook and zabbix applications.
The easiest way is to use the Makefile provided. In this case, both `APP` and `AGGR_APP`
must be provided. The actual code run is replaced by the code residing in the current directory
of the project. If you need to pass some other options to `docker run` use the `EXTRA_OPTS`
(for instance, for publishing ports).

```
$ make docker-run-dev APP=dev AGGR_APP=webhook EXTRA_OPTS="-p 8000:8000"
```

## Makefile

Some tasks can be done using the `make` utility. The most important ones are
shown below:

* To run an application (without Docker): `$ make run APP=[zabbix|webhook] CONFIG_PATH=path/to/webhook-config.json`
* To build the Docker image: `$ make docker-build APP=[zabbix|webhook|dev]`
* To run the Docker image: `$ make docker-run APP=[zabbix|webhook] [CONFIG_PATH=path/to/webhook-config.json]`
* To run the Docker image of development: `$ make docker-run APP=dev AGGR_APP=[zabbix|webhook] [CONFIG_PATH=path/to/webhook-config.json] [EXTRA_OPTS=""]`
* To tag stable Docker images: `$ make docker-tag APP=[zabbix|webhook]`
* To tag unstable Docker images: `$ make docker-tag-unstable APP=[zabbix|webhook]`
* To push stable Docker images to registry: `$ make docker-push APP=[zabbix|webhook]`
* To push unstable Docker images to registry: `$ make docker-push-unstable APP=[zabbix|webhook]`
* To show the stable tags that will be generated: `$ make tags APP=[zabbix|webhook]`
* To show the unstable tags that will be generated: `$ make tags-unstable APP=[zabbix|webhook]`
* To run the tests: `$ make test APP=<anything>`
* To install dependecies: `$ make dep APP=<anything>`
* To build the HTML documentation: `$ make html APP=<anything>`
* To run the linther: `$ make lint APP=<anything>`
* To clean the project: `$ make clean APP=<anything>`

You can also overwrite some parameters used in Makefile. For instance, if you
want to run a different revision of the zabbix app, you can run:

`$ make docker-run APP=zabbix REVISION=<revision>`

The `Makefile` also provides sensitive defaults:

```
AGGR_PATH=<current_directory>
CONFIG_PATH=<current_directory>/config/config.json
DOCKER_USERNAME=mconftec
REPOSITORY=mconf-aggr
```

> The `APP` parameter is mandatory even if the command does not require it. Failing to supply it will cause the command to fail.
