import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="mconf-aggr",
    version="0.0.1",
    description="Mconf Aggregator",
    long_description=read("README.md"),
    author="Kazuki Yokoyama",
    author_email="kmyokoyama@inf.ufrgs.br",
    url="https://github.com/mconftec/mconf-aggr",
    packages=["mconf_aggr"],
    install_requires=["psycopg2",
                      "zabbix-api",
                      "sphinx",
                      "sqlalchemy",
                      "cachetools"],
    test_suite="tests"
)
