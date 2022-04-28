import argparse
import importlib
import json
import logging
import os
import re
import sys
import unittest

import coverage


class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        """Print help when error occurs and exit"""
        self.print_help()
        sys.stderr.write("\nError: %s\n" % message)
        sys.exit(1)


CONFIG_DIR = "tests"
TESTS_DIR = "tests"
TEST_FILE_RE = re.compile(r"\w+\_test\.py$")
INTEGRATION_TEST_FILE_RE = re.compile(r"integration\_\w+\_test\.py$")


def is_test_file(file):
    return os.path.isfile(file) and TEST_FILE_RE.match(file)


def is_integration_test_file(file):
    return os.path.isfile(file) and INTEGRATION_TEST_FILE_RE.match(file)


def remove_ext(file):
    return os.path.splitext(file)[0]


def get_cmd_args_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "suite",
        type=str,
        help="A suite in 'test_suites' of config_tests.json. If no suite is supplied, "
        "all is implied.",
        nargs="?",
    )
    parser.add_argument(
        "--coverage",
        dest="enable_coverage",
        action="store_true",
        default=False,
        help="Enable test coverage",
    )

    return parser


if __name__ == "__main__":
    config_file = os.path.join(CONFIG_DIR, "tests.json")
    with open(config_file, "r") as f:
        config = json.load(f)

    verbosity = config["verbosity"]
    should_log = config["logging"]
    test_suites = config["test_suites"]

    if not should_log:
        logging.disable(logging.CRITICAL)

    suite = unittest.TestSuite()

    os.chdir(TESTS_DIR)

    parser = get_cmd_args_parser()
    args = parser.parse_args()

    if args.suite is None:
        modules = [
            remove_ext(name)
            for name in os.listdir(os.getcwd())
            if is_test_file(name) and not is_integration_test_file(name)
        ]
    else:
        if is_test_file(args.suite):
            modules = [remove_ext(args.suite)]
        else:
            test_suite = str(args.suite)
            try:
                modules = test_suites[test_suite]
            except KeyError:
                print("Invalid suite '{}'.".format(test_suite))
                sys.exit(1)

    for module in modules:
        module = TESTS_DIR + "." + module
        try:
            importlib.import_module(module)
        except ModuleNotFoundError:
            print("Invalid test module '{}'.".format(module))
            sys.exit(1)

        module_obj = sys.modules[module]
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module_obj))

    runner = unittest.TextTestRunner(verbosity=verbosity)

    if args.enable_coverage:
        cov = coverage.Coverage(branch=True)
        cov.start()

    runner.run(suite)

    if args.enable_coverage:
        cov.stop()
        cov.save()
        cov.xml_report()
