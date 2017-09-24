import json
import importlib
import logging
import sys
import unittest


def print_help():
    print("""usage: python test_suites.py [suite]\n
suite\tA suite in 'test_suites' of config_tests.json.
If no suite is supplied, all is implied.""")


if __name__ == '__main__':
    with open("config_tests.json", 'r') as f:
        config = json.load(f)

    verbosity = config['verbosity']
    should_log = config['logging']
    test_suites = config['test_suites']

    if not should_log:
        logging.disable(logging.CRITICAL)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    if len(sys.argv) == 1:
        modules = {module for modules in test_suites.values() for module in modules}
    elif len(sys.argv) == 2:
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
        try:
            importlib.import_module(module)
        except ModuleNotFoundError as err:
            print("Invalid test module '{}'.".format(module))
            sys.exit(1)

        module_obj = sys.modules[module]
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module_obj))

    runner = unittest.TextTestRunner(verbosity=verbosity)

    runner.run(suite)
