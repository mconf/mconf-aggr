# Mconf-Aggregator

* **Current version**: `1.9.2`

## Python version

> Note: You only have to do this once.

This project is meant to work with version 3.9.10 of Python. Before we even start,
we have to make sure that the right version is set. We highly suggest you to use
a version manager such as `pyenv`. For instructions on how to
install `pyenv`, check
[pyenv's official documentation](https://github.com/pyenv/pyenv#installation).

> Note: Don't forget to run `source ~/.bashrc` after installing `pyenv`.

Once `pyenv` is installed, do the following (considering you're in the
project's root directory):

```
$ pyenv install 3.9.10
$ pyenv local 3.9.10
$ pyenv rehash
```

There should be now a file called `.python-version` with the content '_3.9.10_'.
It is always good to check if the Python version has switched correctly:

```
$ python --version
```

You should see an output like this:

```
Python 3.9.10
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
* `sphinx` version 1.6.3 or later ([official site](http://www.sphinx-doc.org/en/stable/))
* `sqlalchemy` version 1.2.0b2 or later ([official site](https://www.sqlalchemy.org/))

They can be easily installed with:

```
$ pip3 install psycopg2
$ pip3 install sphinx
$ pip3 install sqlalchemy
```

To check if the installation ran successfuly, try to import them
(in the project's root directoy):

```
$ python -c "import psycopg2"
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

To run the suite _integration_ of integration tests, do:

```
$ python tests.py integration
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

Note that this does not run the integration tests. To run them, you have to run
the `integration` suite specifically.

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

We also provide a bunch of Dockerfiles to build images of the applications. They are built
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

For instance, if the webhook app is at version 0.0.2-pre-alpha and current commit hash is 36fba5,
local tags we be built as:

* `webhook-0.0.2-pre-alpha-36fba5`

The stable release will have tags:

* `webhook-0.0.2`
* `webhook-0`
* `webhook-36fba5`
* `webhook-latest`

And the unstable release will have tags:

* `webhook-0.0.2-pre-alpha`
* `webhook-36fba5`

There is also a `staging` tag that is intended for pre-release images.

> The version is obtained from the `.version` file.

### Developing with Docker

You can also develop using a single Docker image.
The actual code run is replaced by the code residing in the current directory
of the project.

#### Manually

To build the development image manually, run:

```
$ docker build -f Dockerfile.dev -t mconf/mconf-aggr:dev .
```

It is also nice to tag it as _latest_:

```
$ docker tag mconf/mconf-aggr:dev mconf/mconf-aggr:dev-latest
```

#### Makefike

The easiest way however is to use the Makefile provided.

To build the development image using Docker, run:

```
$ make docker-build-dev
```

To run this image passing some other options to `docker run` use the`EXTRA_OPTS`
(for instance, for publishing ports), run:

```
$ make docker-run-dev EXTRA_OPTS="-p 8000:8000"
```

### Dockerize

In order to shorten build time, we recommend using images based on a "dockerized" base image.

We use [dockerize](https://github.com/jwilder/dockerize) to generate configuration files
from template files and environment variables in Docker containers. To do this, we need
to install dockerize in the Docker image, a process that is time-consuming.

To make build time faster, you can build new base images with dockerize already included.
In the `dockerize/` directory, there are two Dockerfiles:

* `Dockerfile.alpine.dockerize`: builds `alpine:latest-dockerize` that is `alpine:latest` with Dockerize installed.
* `Dockerfile.python3.dockerize`: builds `python:3.6-alpine-dockerize` that is `python:3.6-alpine` with Dockerize installed.

To make things easier, we provide a Makefile with the command `docker-build`. To build these
two dockerized images, you only need to run (from `dockerize/`):

```
$ make docker-build
```

> You actually have to this to use the Makefile commands below since it is configured to
build the final images from the dockerized base images.

## Debugging with VSCode

To debug with vscode you must set launch.json which is the config file for debugging in vscode.

To debug aggregator, for example:


```
"version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Tests",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/tests.py",
            "console": "integratedTerminal"
        },
        {
            "name": "Python: Anexar",
            "type": "python",
            "request": "attach",
            "port": 5678,
            "host": "localhost",
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "."
                }
            ]
        }
    ]
```

When it's done, make sure the image is built and run the container with makefile. After the container is up, the debugger will wait the attach to start running the service. Just click on "Start debugging" and a debug console should appears on your panel.

## Makefile

Some tasks can be done using the `make` utility. The most important ones are
shown below:

* To run mconf-aggr (without Docker): `$ make run CONFIG_PATH=path/to/app-config.json`
* To run mconf-aggr with Docker Compose: `$ make up [IMAGE_VERSION=latest]`
* To start, restart or stop a single service: `$ make [start|restart|stop] SERVICE=[mconf-aggr-webhook]`
* To build the Docker image: `$ make docker-build`
* To build the development Docker image: `$ make docker-build-dev`
* To run the Docker image: `$ make docker-run  [CONFIG_PATH=path/to/app-config.json] [LOGGING_PATH=path/to/logging.json] [IMAGE_VERSION=latest]`
* To run the Docker image of development: `$ make docker-run-dev [CONFIG_PATH=path/to/webhook-config.json] [LOGGING_PATH=path/to/logging.json] [EXTRA_OPTS=""]`
* To tag stable Docker images: `$ make docker-tag`
* To tag unstable Docker images: `$ make docker-tag-unstable`
* To tag latest Docker images: `$ make docker-tag-latest`
* To tag staging Docker images: `$ make docker-tag-staging`
* To push stable Docker images to registry: `$ make docker-push`
* To push unstable Docker images to registry: `$ make docker-push-unstable`
* To push latest Docker images to registry: `$ make docker-push-latest`
* To push staging Docker images to registry: `$ make docker-push-staging`
* To show the stable tags that will be generated: `$ make tags`
* To show the unstable tags that will be generated: `$ make tags-unstable`
* To show the latest tags that will be generated: `$ make tags-latest`
* To show the staging tags that will be generated: `$ make tags-staging`
* To show all project-related Docker images: `$ make docker-image`
* To remove all containers (related to the project or not): `$ make docker-container-rm`
* To remove all project-related Docker images: `$ make docker-rm`
* To remove all dangling project-related Docker images: `$ make docker-rm-dangling`
* To prune Docker system: `$ make docker-prune`
* To remove all dangling project-related Docker images and prune Docker syste: `$ make docker-clean`
* To run the tests: `$ make test`
* To install dependecies: `$ make dep`
* To build the HTML documentation: `$ make html`
* To run the linter: `$ make lint`
* To clean the project: `$ make clean`

You can also overwrite some parameters used in Makefile. For instance, if you
want to run a different revision, you can run:

`$ make docker-run REVISION=<revision>`

The `Makefile` also provides sensitive defaults:

```
AGGR_PATH=<current_directory>
CONFIG_PATH=<current_directory>/config/config.json
LOGGING_PATH=<current_directory/config/logging.json
DOCKER_USERNAME=mconf
REPOSITORY=mconf-aggr
```
