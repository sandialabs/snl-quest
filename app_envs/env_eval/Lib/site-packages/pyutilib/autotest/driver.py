#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
#

__all__ = ['run', 'main', 'create_test_suites']

import sys
import optparse
import re
import os
from os.path import dirname, abspath

import pyutilib.th as unittest
from pyutilib.misc import Options
from pyutilib.component.core import ExtensionPoint
from pyutilib.autotest import plugins

# GAH: Inside create_test_suite all options are (were) being cast to
#      str(). Although I'm not sure, I assume this is to wash out
#      unicode coming from json files in Python 2.x. However, we don't
#      want to cast numeric options in either case (which was
#      happening, e.g., tolerance). This is my quick hack to fix
#      things. Please fix if you have a better understanding of what
#      should be happening.
try:
    unicode
except:
    basestring = str


def _str(x):
    if isinstance(x, basestring):
        return str(x)
    return x


def validate_test_config(suite):
    if suite is None:
        raise IOError(
            "Empty suite indicates problem processing suite configuration")
    #
    tmp = set(suite.keys())
    if not tmp.issubset(
            set(['python', 'solvers', 'problems', 'suites', 'driver'])):
        raise IOError("Unexpected test sections: " + str(suite.keys()))
    #
    if 'python' in suite:
        if not type(suite['python']) is list:
            raise IOError("Expected list of Python expressions")
    #
    if 'solvers' in suite:
        if not type(suite['solvers']) is dict:
            raise IOError("Expected dictionary of solvers")
        for key in suite['solvers']:
            if suite['solvers'][key] is None:
                suite['solvers'][key] = {}
            elif not type(suite['solvers'][key]) is dict:
                raise IOError(
                    "Expected solvers to have a dictionary of options: %s" %
                    str(suite))
    #
    if 'problems' in suite:
        if not type(suite['problems']) is dict:
            raise IOError("Expected dictionary of problems")
        for key in suite['problems']:
            if suite['problems'][key] is None:
                suite['problems'][key] = {}
            elif not type(suite['problems'][key]) is dict:
                raise IOError(
                    "Expected problems to have a dictionary of options")
    #
    if 'suites' in suite:
        if not type(suite['suites']) is dict:
            raise IOError("Expected dictionary of suites")
        for key in suite['suites']:
            if suite['suites'][key] is None:
                suite['suites'][key] = {}
            elif not type(suite['suites'][key]) is dict:
                raise IOError("Expected suites to have a dictionary of options")


@unittest.nottest
def create_test_suites(filename=None, config=None, _globals=None, options=None):
    if options is None:  #pragma:nocover
        options = Options()
    #
    # Add categories specified by the PYUTILIB_AUTOTEST_CATEGORIES
    # or PYUTILIB_UNITTEST_CATEGORIES environments
    #
    if options is None or options.categories is None or len(
            options.categories) == 0:
        options.categories = set()
        if 'PYUTILIB_AUTOTEST_CATEGORIES' in os.environ:
            for cat in re.split(',',
                                os.environ['PYUTILIB_AUTOTEST_CATEGORIES']):
                if cat != '':
                    options.categories.add(cat.strip())
        elif 'PYUTILIB_UNITTEST_CATEGORIES' in os.environ:
            for cat in re.split(',',
                                os.environ['PYUTILIB_UNITTEST_CATEGORIES']):
                if cat != '':
                    options.categories.add(cat.strip())
    #
    if not filename is None:
        if options.currdir is None:
            options.currdir = dirname(abspath(filename)) + os.sep
        #
        ep = ExtensionPoint(plugins.ITestParser)
        ftype = os.path.splitext(filename)[1]
        if not ftype == '':
            ftype = ftype[1:]
        service = ep.service(ftype)
        if service is None:
            raise IOError(
                "Unknown file type.  Cannot load test configuration from file '%s'"
                % filename)
        config = service.load_test_config(filename)
    #service.print_test_config(config)
    validate_test_config(config)
    #
    # Evaluate Python expressions
    #
    for item in config.get('python', []):
        try:
            exec(item, _globals)
        except Exception:
            err = sys.exc_info()[1]
            print("ERROR executing '%s'" % item)
            print("  Exception: %s" % str(err))
    #
    # Create test driver, which is put in the global namespace
    #
    driver = plugins.TestDriverFactory(config['driver'])
    if driver is None:
        raise IOError("Unexpected test driver '%s'" % config['driver'])
    _globals["test_driver"] = driver
    #
    # Generate suite
    #
    for suite in config.get('suites', {}):
        create_test_suite(suite, config, _globals, options)


@unittest.nottest
def create_test_suite(suite, config, _globals, options):
    #
    # Skip suite creation if the options categores do not intersect with the list of test suite categories
    #
    if len(options.categories) > 0:
        flag = False
        for cat in options.categories:
            if cat in config['suites'][suite].get('categories', []):
                flag = True
                break
        if not flag:
            return
    #
    # Create test driver
    #
    if suite in _globals:
        raise IOError(
            "Cannot create suite '%s' since there is another symbol with that name in the global namespace!"
            % suite)

    def setUpClassFn(cls):
        options = cls._options[None]
        cls._test_driver.setUpClass(cls, options)

    _globals[suite] = type(
        str(suite),
        (unittest.TestCase,), {'setUpClass': classmethod(setUpClassFn)})
    _globals[suite]._options[None] = options
    setattr(_globals[suite], '_test_driver', _globals['test_driver'])
    setattr(_globals[suite], 'suite_categories', config['suites'][suite].get(
        'categories', []))
    #
    # Create test functions
    #
    tests = []
    if 'tests' in config['suites'][suite]:
        for item in config['suites'][suite]['tests']:
            tests.append((item['solver'], item['problem'], item))
    else:
        for solver in config['suites'][suite]['solvers']:
            for problem in config['suites'][suite]['problems']:
                tests.append((solver, problem, {}))
    #
    for solver, problem, item in tests:
        ##sname = solver
        if options.testname_format is None:
            test_name = solver + "_" + problem
        else:
            test_name = options.testname_format % (solver, problem)
        #
        def fn(testcase, name, suite):
            options = testcase._options[suite, name]
            fn.test_driver.setUp(testcase, options)
            ans = fn.test_driver.run_test(testcase, name, options)
            fn.test_driver.tearDown(testcase, options)
            return ans

        fn.test_driver = _globals['test_driver']
        #
        _options = Options()
        #
        problem_options = config['suites'][suite]['problems'][problem]
        if not problem_options is None and 'problem' in problem_options:
            _problem = problem_options['problem']
        else:
            _problem = problem
        for attr, value in config['problems'].get(_problem, {}).items():
            _options[attr] = _str(value)
        if not problem_options is None:
            for attr, value in problem_options.items():
                _options[attr] = _str(value)
        #
        solver_options = config['suites'][suite]['solvers'][solver]
        if not solver_options is None and 'solver' in solver_options:
            _solver = solver_options['solver']
        else:
            _solver = solver
        _name = _solver
        for attr, value in config['solvers'].get(_solver, {}).items():
            _options[attr] = _str(value)
            if attr == 'name':
                _name = value
        if not solver_options is None:
            for attr, value in solver_options.items():
                _options[attr] = _str(value)
        #
        for key in item:
            if key not in ['problem', 'solver']:
                _options[key] = _str(item[key])
        #
        _options.solver = _str(_name)
        _options.problem = _str(_problem)
        _options.suite = _str(suite)
        _options.currdir = _str(options.currdir)
        #
        _globals[suite].add_fn_test(
            name=test_name, fn=fn, suite=suite, options=_options)


def cleanup(_globals, suites):
    for suite in suites:
        del _globals[suite]


def run(argv, _globals=None):
    #
    # Set sys.argv to the value specified by the user
    #
    sys.argv = argv
    #
    # Create the option parser
    #
    parser = optparse.OptionParser()
    parser.remove_option('-h')
    #
    parser.add_option(
        '-h',
        '--help',
        action='store_true',
        dest='help',
        default=False,
        help='Print command options')
    #
    parser.add_option(
        '-d',
        '--debug',
        action='store_true',
        dest='debug',
        default=False,
        help='Set debugging flag')
    #
    parser.add_option(
        '-v',
        '--verbose',
        action='store_true',
        dest='verbose',
        default=False,
        help='Verbose output')
    #
    parser.add_option(
        '-q',
        '--quiet',
        action='store_true',
        dest='quiet',
        default=False,
        help='Minimal output')
    #
    parser.add_option(
        '-f',
        '--failfast',
        action='store_true',
        dest='failfast',
        default=False,
        help='Stop on first failure')
    #
    parser.add_option(
        '-c',
        '--catch',
        action='store_true',
        dest='catch',
        default=False,
        help='Catch control-C and display results')
    #
    parser.add_option(
        '-b',
        '--buffer',
        action='store_true',
        dest='buffer',
        default=False,
        help='Buffer stdout and stderr durring test runs')
    #
    parser.add_option(
        '--cat',
        '--category',
        action='append',
        dest='categories',
        default=[],
        help='Define a list of categories that filter the execution of test suites')
    #
    parser.add_option(
        '--help-suites',
        action='store_true',
        dest='help_suites',
        default=False,
        help='Print the test suites that can be executed')
    #
    parser.add_option(
        '--help-tests',
        action='store',
        dest='help_tests',
        default=None,
        help='Print the tests in the specified test suite')
    #
    parser.add_option(
        '--help-categories',
        action='store_true',
        dest='help_categories',
        default=False,
        help='Print the test suite categories that can be specified')
    #
    # Parse the argument list and print help info if needed
    #
    _options, args = parser.parse_args(sys.argv)
    if _options.help:
        parser.print_help()

        print("""
Examples:
  %s                               - run all test suites
  %s MyTestCase.testSomething      - run MyTestCase.testSomething
  %s MyTestCase                    - run all 'test*' test methods
                                               in MyTestCase
""" % (args[0], args[0], args[0]))
        return
    #
    # If no value for _globals is specified, then we use the current context.
    #
    if _globals is None:
        _globals = globals()
    #
    # Setup and Options object and create test suites from the specified
    # configuration files.
    #
    options = Options()
    options.debug = _options.debug
    options.verbose = _options.verbose
    options.quiet = _options.quiet
    options.categories = _options.categories
    _argv = []
    for arg in args[1:]:
        if os.path.exists(arg):
            create_test_suites(filename=arg, _globals=_globals, options=options)
        else:
            _argv.append(arg)
    #
    # Collect information about the test suites:  suite names and categories
    #
    suites = []
    categories = set()
    for key in _globals.keys():
        if type(_globals[key]) is type and issubclass(_globals[key],
                                                      unittest.TestCase):
            suites.append(key)
            for c in _globals[key].suite_categories:
                categories.add(c)
    #
    # Process the --help-tests option
    #
    if _options.help_tests and not _globals is None:
        suite = _globals.get(_options.help_tests, None)
        if not type(suite) is type:
            print("Test suite '%s' not found!" % str(_options.help_tests))
            return cleanup(_globals, suites)
        tests = []
        for item in dir(suite):
            if item.startswith('test'):
                tests.append(item)
        print("")
        if len(tests) > 0:
            print("Tests defined in test suite '%s':" % _options.help_tests)
            for tmp in sorted(tests):
                print("    " + tmp)
        else:
            print("No tests defined in test suite '%s':" % _options.help_tests)
        print("")
        return cleanup(_globals, suites)
    #
    # Process the --help-suites and --help-categories options
    #
    if (_options.help_suites or
            _options.help_categories) and not _globals is None:
        if _options.help_suites:
            print("")
            if len(suites) > 0:
                print("Test suites defined in '%s':" %
                      os.path.basename(argv[0]))
                for suite in sorted(suites):
                    print("    " + suite)
            else:
                print("No test suites defined in '%s'!" %
                      os.path.basename(argv[0]))
            print("")
        if _options.help_categories:
            tmp = list(categories)
            print("")
            if len(tmp) > 0:
                print("Test suite categories defined in '%s':" %
                      os.path.basename(argv[0]))
                for c in sorted(tmp):
                    print("    " + c)
            else:
                print("No test suite categories defined in '%s':" %
                      os.path.basename(argv[0]))
            print("")
        return cleanup(_globals, suites)
    #
    # Reset the value of sys.argv per the expectations of the unittest module
    #
    tmp = [args[0]]
    if _options.quiet:
        tmp.append('-q')
    if _options.verbose or _options.debug:
        tmp.append('-v')
    if _options.failfast:
        tmp.append('-f')
    if _options.catch:
        tmp.append('-c')
    if _options.buffer:
        tmp.append('-b')
    tmp += _argv
    sys.argv = tmp
    #
    # Execute the unittest main function to run tests
    #
    unittest.main(module=_globals['__name__'])
    cleanup(_globals, suites)


def main(_globals=None):
    run(sys.argv, _globals=_globals)
