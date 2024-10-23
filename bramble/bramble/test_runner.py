from django.test.runner import DiscoverRunner
from colorama import init, Fore, Style
import unittest

init(autoreset=True)  # Initialize colorama for color handling

class ColoredTextTestResult(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        print(f"{test._testMethodName} ... {Fore.GREEN}PASSED{Style.RESET_ALL}")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        print(f"{test._testMethodName} ... {Fore.RED}FAILED{Style.RESET_ALL}")

    def addError(self, test, err):
        super().addError(test, err)
        print(f"{test._testMethodName} ... {Fore.RED}ERROR{Style.RESET_ALL}")

class ColoredTextTestRunner(DiscoverRunner):
    """Custom test runner that uses colored text output."""
    def get_resultclass(self):
        """Override to provide custom result class."""
        return ColoredTextTestResult

    def run_suite(self, suite, **kwargs):
        """Override run_suite to pass the custom result class."""
        runner = unittest.TextTestRunner(resultclass=self.get_resultclass())
        return runner.run(suite)