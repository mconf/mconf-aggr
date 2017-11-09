import json
import importlib
import logging
import re
import os
import sys
import unittest


def print_help():
    print("""usage: python test_suites.py [suite]\n
suite\tA suite in 'test_suites' of config_tests.json.
If no suite is supplied, all is implied.""")


CONFIG_DIR = "config"
TESTS_DIR = "tests"
TEST_FILE_RE = re.compile(r'\w+\_test\.py$')


def is_test_file(file):
    return os.path.isfile(file) and TEST_FILE_RE.match(file)


def remove_ext(file):
    return os.path.splitext(file)[0]


if __name__ == '__main__':
    config_file = os.path.join(CONFIG_DIR, "tests.json")
    with open(config_file, 'r') as f:
        config = json.load(f)

    verbosity = config['verbosity']
    should_log = config['logging']
    test_suites = config['test_suites']

    if not should_log:
        logging.disable(logging.CRITICAL)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    os.chdir(TESTS_DIR)

    if len(sys.argv) == 1:
        modules = [remove_ext(name) for name in os.listdir(os.getcwd())
                   if is_test_file(name)]
    elif len(sys.argv) == 2:
        if is_test_file(sys.argv[1]):
            modules = [remove_ext(sys.argv[1])]
        else:
            test_suite = str(sys.argv[1])
            try:
                modules = test_suites[test_suite]
            except KeyError as err:
                print("Invalid suite '{}'.".format(test_suite))
                sys.exit(1)
    else:
        print_help()
        sys.exit(1)

    for module in modules:
        module = TESTS_DIR + "." + module
        try:
            importlib.import_module(module)
        except ModuleNotFoundError as err:
            print("Invalid test module '{}'.".format(module))
            sys.exit(1)

        module_obj = sys.modules[module]
        suite.addTests(unittest
                       .defaultTestLoader
                       .loadTestsFromModule(module_obj))

    runner = unittest.TextTestRunner(verbosity=verbosity)

    runner.run(suite)
