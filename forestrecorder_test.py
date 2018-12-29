#!/usr/bin/python3
"""Test the forestrecorder."""
import pathlib
import subprocess
import sys
import unittest

_EXECUTABLE = str(pathlib.Path(__file__).parent / 'forestrecorder')


def setUpModule():
    """Wipe out any old coverage data."""
    subprocess.run((sys.executable, '-m', 'coverage', 'erase'), check=True)


def tearDownModule():
    """Check that coverage is at 100%"""
    result = subprocess.run(
        (
            sys.executable, '-m', 'coverage', 'report',
            '--show-missing', '--fail-under=100'))
    if result.returncode:
        raise ValueError("Coverage did not reach 100%")


def _run(*args, **kwargs):
    """Run the forestrecorder with args.

    This appends coverage data and passes the kwargs to the subprocess.

    """
    return subprocess.run(
        (
            sys.executable, '-m', 'coverage', 'run',
            '--append', '--include', _EXECUTABLE, _EXECUTABLE) + args,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True, **kwargs)


class TestMainParser(unittest.TestCase):
    """Test the forestrecorder's main parser."""

    def test_invocation_error(self):
        """Test invocation errors on the main parser."""
        result = _run()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, '')
        self.assertRegex(result.stderr, '^usage:')

    def test_help(self):
        """Test help on the main parser."""
        for args in (('-h',), ('--help',)):
            with self.subTest(args=args):
                result = _run(*args)
                self.assertEqual(result.returncode, 0)
                self.assertRegex(result.stdout, r'(?m)^usage')
                self.assertRegex(result.stdout, r'(?m)^Record a forest')
                self.assertRegex(result.stdout, r'(?m)^optional_arguments:')
                self.assertRegex(result.stdout, r'(?m)^command:')
                self.assertEqual(result.stderr, '')


class TestConfigureParser(unittest.TestCase):
    """Test the forestrecorder's configure parser."""
    pass


class TestAddParser(unittest.TestCase):
    """Test the forestrecorder's add parser."""
    pass


class TestMoveParser(unittest.TestCase):
    """Test the forestrecorder's move parser."""
    pass


class TestRemoveParser(unittest.TestCase):
    """Test the forestrecorder's remove parser."""
    pass


class TestHistoryParser(unittest.TestCase):
    """Test the forestrecorder's history parser."""
    pass


class TestDumpParser(unittest.TestCase):
    """Test the forestrecorder's dump parser."""
    pass


class TestVersionParser(unittest.TestCase):
    """Test the forestrecorder's version parser."""
    pass


if __name__ == '__main__':
    unittest.main()
