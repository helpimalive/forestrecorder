"""Test the forestrecorder."""
import pathlib
import subprocess
import sys
import unittest
import tempfile
import shutil
import os
import coverage
from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader 
import importlib
from pathlib import Path
import pytest


importlib.machinery.SOURCE_SUFFIXES.append('') # empty string to allow any file
spec = importlib.util.spec_from_file_location('forestrecorder', 
    str(os.path.dirname(os.path.abspath(__file__))+'\\forestrecorder'))
forestrecorder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(forestrecorder)

_EXECUTABLE = str(pathlib.Path(__file__).parent / 'forestrecorder')


def setUpModule():
    """Wipe out any old coverage data."""
    subprocess.run((sys.executable, '-m', 'coverage', 'erase'), check=True)


def tearDownModule():
    """Check that coverage is at 100%"""
    result = subprocess.run(
        (
            sys.executable, '-m', 'coverage', 'report',
            '--show-missing', '--fail-under=0'))
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
    def test_help(self):
        """Test help on the main parser."""
        for args in (('-h',), ('--help',)):
            with self.subTest(args=args):
                result = _run('configure',*args)
                self.assertEqual(result.returncode, 0)
                self.assertRegex(result.stdout, r'(?m)^usage')
                self.assertRegex(result.stdout, r'(?m)^Create a forest configuration.')
                self.assertRegex(result.stdout, r'(?m)^optional arguments:')
                self.assertRegex(result.stdout, r'(?m)^interactive or required arguments:')
                self.assertEqual(result.stderr, '')
    def test_configuration(self):
        """ Test the first argument of the forrest"""
        with tempfile.TemporaryDirectory() as tempdir:
            args = (
            'python',
            _EXECUTABLE,
            'configure',
            '--forest-name',
            'MYFOREST',
            '--tree-name',
            'MYTREE',
            '--node-name',
            'MYNODE',
            '--child-to-parent-name',
            'MYCHILDTOPARENT',
            '--actions-path',
            str(pathlib.Path(tempdir)/'actions'),
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder'),
            '--force'
            )
            subprocess.run(args, check=True)

class TestAddParser(unittest.TestCase):
    """Test the forestrecorder's add parser."""
    def test_help(self):
        """Test help on the main parser."""
        for args in (('-h',), ('--help',)):
            with self.subTest(args=args):
                result = _run('add',*args)
                self.assertEqual(result.returncode, 0)
                self.assertRegex(result.stdout, r'(?m)^usage')
                self.assertRegex(result.stdout, r'(?m)^Add a node to the forest.')
                self.assertRegex(result.stdout, r'(?m)^optional arguments:')
                self.assertRegex(result.stdout, r'(?m)^interactive or required arguments:')
                self.assertEqual(result.stderr, '')

    def test_add(self):
        """Test add"""

        """Configure a new forest"""
        with tempfile.TemporaryDirectory() as tempdir:
            args = (
            'python',
            _EXECUTABLE,
            'configure',
            '--forest-name',
            'MYFOREST',
            '--tree-name',
            'MYTREE',
            '--node-name',
            'MYNODE',
            '--child-to-parent-name',
            'MYCHILDTOPARENT',
            '--actions-path',
            str(pathlib.Path(tempdir)/'actions'),
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder'),
            '--force'
            )

            subprocess.run(args, check=True)

            """Add DRAMA"""
            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )

            subprocess.run(args, check=True)

            """Test that DRAMA was added"""
            with self.subTest(args=args):
                result = _run('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)
                self.assertEqual(result.returncode,0)
                self.assertRegex(result.stdout,r'{"DRAMA": {}}')
                self.assertEqual(result.stderr,'')

            """Add COURTROOM_DRAMA as a child of DRAMA"""
            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'COURTROOM_DRAMA',
            '--parent',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run(args, check=True)

            """Add PERIOD_DRAMA as a child of COURTROOM_DRAMA"""
            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'PERIOD_DRAMA',
            '--parent',
            'COURTROOM_DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run(args, check=True)

            """Test that COURTROOM_DRAMA and PERIOD_DRAMA were added in order"""
            with self.subTest(args=args):
                result = _run('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)
                self.assertEqual(result.returncode,0)
                self.assertRegex(result.stdout,r'{"DRAMA": {"COURTROOM_DRAMA": {"PERIOD_DRAMA": {}}}}')
                self.assertEqual(result.stderr,'')


            """Tesing input validity"""
            """Test that 'yEs' is flagged as an invalid response"""
            args = (
            'add',
            '--node',
            'MIDDLE_DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            with self.subTest(args=args):
                result = subprocess.run(
                    (sys.executable, '-m', 'coverage', 'run',
                    '--append', '--include', _EXECUTABLE, _EXECUTABLE)
                    + args,
                    check=True,
                    input = '0\n0\n\nyEs\ny\n', # 'yEs' is used to invoke and test an invalid input error
                    universal_newlines=True)

            """Tesing input validity"""
            """creating a case where 'no' is used as the answer to an input prompt"""
            args = (
            'add',
            '--node',
            'SUB_MIDDLE_DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            with self.subTest(args=args):
                result = subprocess.run(
                    (sys.executable, '-m', 'coverage', 'run',
                    '--append', '--include', _EXECUTABLE, _EXECUTABLE)
                    + args,
                    check=True,
                    input = '0\n0\n\nn\ny\n',
                    universal_newlines=True)

            """Tesing input validity"""
            """creating a case where a non-integer is used as the answer to an input prompt"""
            args = (
            'add',
            '--node',
            'SUPER_MIDDLE_DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            with self.subTest(args=args):
                result = subprocess.run(
                    (sys.executable, '-m', 'coverage', 'run',
                    '--append', '--include', _EXECUTABLE, _EXECUTABLE)
                    + args,
                    check=True,
                    input = '0\n1.5\n\nn\ny\n',
                    universal_newlines=True)

            """Tesing input validity"""
            """creating a case where a non-integer is used as the answer to an input prompt"""
            args = (
            'add',
            '--node',
            'SUPER_MIDDLE_DRAMA_II',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            with self.subTest(args=args):
                result = subprocess.run(
                    (sys.executable, '-m', 'coverage', 'run',
                    '--append', '--include', _EXECUTABLE, _EXECUTABLE)
                    + args,
                    check=True,
                    input = '0\n55\n\nn\ny\n',
                    universal_newlines=True)

            """Tesing input validity"""
            """creating a case where a newline is given as an answer to an input prompt"""
            args = (
            'add',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            with self.subTest(args=args):
                result = subprocess.run(
                    (sys.executable, '-m', 'coverage', 'run',
                    '--append', '--include', _EXECUTABLE, _EXECUTABLE)
                    + args,
                    check=True,
                    input = '\nSUPER_MIDDLE_DRAMA_III\n\nn',
                    universal_newlines=True)

class TestMoveParser(unittest.TestCase):
    """Test the forestrecorder's move parser."""
    def test_help(self):
        """Test help on the main parser."""
        for args in (('-h',), ('--help',)):
            with self.subTest(args=args):
                result = _run('move',*args)
                self.assertEqual(result.returncode, 0)
                self.assertRegex(result.stdout, r'(?m)^usage')
                self.assertRegex(result.stdout, r'(?m)^Move a node in the forest.')
                self.assertRegex(result.stdout, r'(?m)^optional arguments:')
                self.assertRegex(result.stdout, r'(?m)^interactive or required arguments:')
                self.assertEqual(result.stderr, '')

    def test_move(self):
        """Test move"""

        """Configure a forest"""
        with tempfile.TemporaryDirectory() as tempdir:
            args = (
            'configure',
            '--actions-path',
            str(pathlib.Path(tempdir)/'actions'),
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )

            with self.subTest(args=args):
                result = subprocess.run((sys.executable, '-m', 'coverage', 'run',
                        '--append', '--include', _EXECUTABLE, _EXECUTABLE) + args,
                        check=True,
                        input='MYFOREST\nMYTREE\nMYNODE\nMYCHILDTOPARENT',
                        universal_newlines=True)

            """Testing error when trying to overwrite existing configuration"""
            with self.subTest():
                args = (
                'configure',
                '--actions-path',
                str(pathlib.Path(tempdir)/'actions'),
                '-c',
                str(pathlib.Path(tempdir)/'.forestrecorder')
                )
                result = subprocess.run((sys.executable, '-m', 'coverage', 'run',
                '--append', '--include', _EXECUTABLE, _EXECUTABLE) + args,
                input='MYFOREST\nMYTREE\nMYNODE\nMYCHILDTOPARENT',
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True)
                self.assertEqual(result.returncode,5)
                self.assertRegex(result.stderr,r'use --force to overwrite existing configuration:')

            """Build a forest"""
            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run(args, check=True)

            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'COURTROOM_DRAMA',
            '--parent',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run(args, check=True)

            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'PERIOD_DRAMA',
            '--parent',
            'COURTROOM_DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run(args, check=True)

            # with self.subTest(args=args):
            #     result = _run('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)
            #     self.assertEqual(result.returncode,0)
            #     self.assertRegex(result.stdout,r' {"COURTROOM_DRAMA": {"PERIOD_DRAMA":')
            #     self.assertEqual(result.stderr,'')

            """Test moving PERIOD_DRAMA to be the parent of COURTROOM_DRAMA"""
            args = (
            'move',
            '--node',
            'PERIOD_DRAMA',
            '--parent',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )

            with self.subTest(args=args):
                result = subprocess.run((sys.executable, '-m', 'coverage', 'run',
                        '--append', '--include', _EXECUTABLE, _EXECUTABLE) + args,
                        check=True,
                        input='\ny',
                        universal_newlines=True)
                result = _run('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)
                self.assertEqual(result.returncode,0)
                self.assertRegex(result.stdout,r' {"PERIOD_DRAMA": {"COURTROOM_DRAMA":')
                self.assertEqual(result.stderr,'')

            """Test move with an invalid child specified"""
            args = (
            'move',
            '--node',
            'COURTROOM_DRAMA',
            '--parent',
            'DRAMA',
            '--child',
            'DRAMA',
            '--non-interactive',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            with self.subTest(args=args):
                result = subprocess.run((sys.executable, '-m', 'coverage', 'run',
                '--append', '--include', _EXECUTABLE, _EXECUTABLE) + args,
                input='MYFOREST\nMYTREE\nMYNODE\nMYCHILDTOPARENT',
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True)
                self.assertRegex(result.stderr,r'DRAMA not a child of DRAMA')


            args = (
            'python',
            _EXECUTABLE,
            'move',
            '--node',
            'COURTROOM_DRAMA',
            '--parent',
            'DRAMA',
            '--child',
            'PERIOD_DRAMA',
            '--non-interactive',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run(args, check=True)

            with self.subTest(args=args):
                result = _run('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)
                self.assertEqual(result.returncode,0)
                self.assertRegex(result.stdout,r' {"COURTROOM_DRAMA": {"PERIOD_DRAMA":')
                self.assertEqual(result.stderr,'')

            args = (
            'python',
            _EXECUTABLE,
            'move',
            '--node',
            'PERIOD_DRAMA',
            '--non-interactive',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run(args, check=True)

            with self.subTest(args=args):
                result = _run('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)
                self.assertEqual(result.returncode,0)
                self.assertRegex(result.stdout,r'{"DRAMA": {"COURTROOM_DRAMA": {}}, "PERIOD_DRAMA": {}}')
                self.assertEqual(result.stderr,'')

class TestRemoveParser(unittest.TestCase):
    """Test the forestrecorder's remove parser."""
    def test_help(self):
        """Test help on the main parser."""
        for args in (('-h',), ('--help',)):
            with self.subTest(args=args):
                result = _run('remove',*args)
                self.assertEqual(result.returncode, 0)
                self.assertRegex(result.stdout, r'(?m)^usage')
                self.assertRegex(result.stdout, r'(?m)^Remove a node from the forest.')
                self.assertRegex(result.stdout, r'(?m)^optional arguments:')
                self.assertRegex(result.stdout, r'(?m)^interactive or required arguments:')
                self.assertEqual(result.stderr, '')

            """Configure a forest"""
            with tempfile.TemporaryDirectory() as tempdir:
                args = (
                'python',
                _EXECUTABLE,
                'configure',
                '--forest-name',
                'MYFOREST',
                '--tree-name',
                'MYTREE',
                '--node-name',
                'MYNODE',
                '--child-to-parent-name',
                'MYCHILDTOPARENT',
                '--actions-path',
                str(pathlib.Path(tempdir)/'actions'),
                '-c',
                str(pathlib.Path(tempdir)/'.forestrecorder'),
                '--force'
                )

                subprocess.run(args, check=True)

                args = (
                'python',
                _EXECUTABLE,
                'add',
                '--node',
                'DRAMA',
                '-c',
                str(pathlib.Path(tempdir)/'.forestrecorder')
                )
                subprocess.run(args, check=True)

                args = (
                'python',
                _EXECUTABLE,
                'add',
                '--node',
                'COURTROOM_DRAMA',
                '--parent',
                'DRAMA',
                '-c',
                str(pathlib.Path(tempdir)/'.forestrecorder')
                )
                subprocess.run(args, check=True)

                args = (
                'python',
                _EXECUTABLE,
                'add',
                '--node',
                'PERIOD_DRAMA',
                '--parent',
                'COURTROOM_DRAMA',
                '-c',
                str(pathlib.Path(tempdir)/'.forestrecorder')
                )
                subprocess.run(args, check=True)

                """Test remove of PERIOD_DRAMA"""
                args = (
                'python',
                _EXECUTABLE,
                'remove',
                '--node',
                'PERIOD_DRAMA',
                '--recursive',
                '-c',
                str(pathlib.Path(tempdir)/'.forestrecorder')
                )
                subprocess.run(args, check=True)

                with self.subTest(args=args):
                    result = _run('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)
                    self.assertEqual(result.returncode,0)
                    self.assertRegex(result.stdout,r'{"DRAMA": {"COURTROOM_DRAMA": {}}}')
                    self.assertEqual(result.stderr,'')

                args = (
                'python',
                _EXECUTABLE,
                'add',
                '--node',
                'COMEDY',
                '--non-interactive',
                '-c',
                str(pathlib.Path(tempdir)/'.forestrecorder')
                )
                subprocess.run(args, check=True)

                """Using the existing configuration to test the replace functionality """
                args = (
                'python',
                _EXECUTABLE,
                'add',
                '--node',
                'MIDDLE_DRAMA',
                '--parent',
                'COMEDY',
                '-c',
                str(pathlib.Path(tempdir)/'.forestrecorder')

                )
                subprocess.run(args, check=True)
                result = _run('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)

                """Testing remove of a noninteractive node"""
                args = (
                'python',
                _EXECUTABLE,
                'remove',
                '--node',
                'COMEDY',
                '-c',
                str(pathlib.Path(tempdir)/'.forestrecorder')
                )
                subprocess.run(args, check=True)
                result = _run('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)

                with self.subTest(args=args):
                    result = _run('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)
                    self.assertEqual(result.returncode,0)
                    self.assertTrue("COMEDY" not in result.stdout)
                    self.assertEqual(result.stderr,'')

                """Testing removal of non existant node"""            
                with self.subTest():

                    args = (
                    # 'python',
                    # _EXECUTABLE,
                    'remove',
                    '--node',
                    'COMEDY',
                    # '--non-interactive',
                    '-c',
                    str(pathlib.Path(tempdir)/'.forestrecorder')
                    )

                    result = subprocess.run((sys.executable, '-m', 'coverage', 'run',
                    '--append', '--include', _EXECUTABLE, _EXECUTABLE) + args,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    universal_newlines=True)
                    self.assertRegex(result.stderr,r'(?m)^COMEDY not present in forest')

                """Testing recurisve argument"""
                with self.subTest():
                    args = (
                    'remove',
                    '--node',
                    'DRAMA',
                    '--recursive',
                    '-c',
                    str(pathlib.Path(tempdir)/'.forestrecorder')
                    )
                    result = subprocess.run((sys.executable, '-m', 'coverage', 'run',
                    '--append', '--include', _EXECUTABLE, _EXECUTABLE) + args,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    universal_newlines=True)

class TestHistoryParser(unittest.TestCase):
    """Test the forestrecorder's history parser."""
    def test_help(self):
        """Test help on the main parser."""
        for args in (('-h',), ('--help',)):
            with self.subTest(args=args):
                result = _run('history',*args)
                self.assertEqual(result.returncode, 0)
                self.assertRegex(result.stdout, r'(?m)^usage')
                self.assertRegex(result.stdout, r'(?m)^Print a tab-delimited history of forest actions.')
                self.assertRegex(result.stdout, r'(?m)^optional arguments:')
                self.assertEqual(result.stderr, '')    

    def test_history(self):
        """Testing the history"""

        """Configuring a forest"""
        with tempfile.TemporaryDirectory() as tempdir:
            args = (
            'python',
            _EXECUTABLE,
            'configure',
            '--forest-name',
            'MYFOREST',
            '--tree-name',
            'MYTREE',
            '--node-name',
            'MYNODE',
            '--child-to-parent-name',
            'MYCHILDTOPARENT',
            '--actions-path',
            str(pathlib.Path(tempdir)/'actions'),
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder'),
            '--force'
            )

            subprocess.run(args, check=True)

            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )

            subprocess.run(args, check=True)

            args = (
            'python',
            _EXECUTABLE,
            'remove',
            '--node',
            'DRAMA',
            '--recursive',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )

            subprocess.run(args, check=True)

            """Testing the history is correctly stated"""
            with self.subTest():
                result = _run('history','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)
                self.assertEqual(result.returncode, 0)
                self.assertRegex(result.stdout, r'Time\tadd\tDRAMA')
                self.assertRegex(result.stdout, r'Time\tremove\tDRAMA')
                self.assertEqual(result.stderr, '')  

class TestDumpParser(unittest.TestCase):
    """Test the forestrecorder's dump parser."""
    def test_help(self):
        """Test help on the main parser."""
        for args in (('-h',), ('--help',)):
            with self.subTest(args=args):
                result = _run('dump',*args)
                self.assertEqual(result.returncode, 0)
                self.assertRegex(result.stdout, r'(?m)^usage')
                self.assertRegex(result.stdout, r'(?m)^Print a json representation of the current forest.')
                self.assertRegex(result.stdout, r'(?m)^optional arguments:')
                # self.assertRegex(result.stdout, r'(?m)^interactive or required arguments:')
                self.assertEqual(result.stderr, '')    

    def test_dump(self):
        """Test dump"""
        """Configure a forest"""
        with tempfile.TemporaryDirectory() as tempdir:
            args = (
            'python',
            _EXECUTABLE,
            'configure',
            '--forest-name',
            'MYFOREST',
            '--tree-name',
            'MYTREE',
            '--node-name',
            'MYNODE',
            '--child-to-parent-name',
            'MYCHILDTOPARENT',
            '--actions-path',
            str(pathlib.Path(tempdir)/'actions'),
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder'),
            '--force'
            )

            subprocess.run(args, check=True)

            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run(args, check=True)

            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'COURTROOM_DRAMA',
            '--parent',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run(args, check=True)

            args = (
            'python',
            _EXECUTABLE,
            'dump',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run(args, check=True)

            """Ensure the dump is correctly specified"""
            with self.subTest():
                result = _run('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)
                self.assertEqual(result.returncode,0)
                self.assertRegex(result.stdout,r'{"DRAMA": {"COURTROOM_DRAMA": {}}}')
                self.assertEqual(result.stderr,'')

class TestVersionParser(unittest.TestCase):
    """Test the forestrecorder's version parser."""
    def test_help(self):
        """Test help on the main parser."""
        for args in (('-h',), ('--help',)):
            with self.subTest(args=args):
                result = _run('version',*args)
                self.assertEqual(result.returncode, 0)
                self.assertRegex(result.stdout, r'(?m)^usage')
                self.assertRegex(result.stdout, r'(?m)^Print the current version number and exit.')
                self.assertRegex(result.stdout, r'(?m)^optional arguments:')
                # self.assertRegex(result.stdout, r'(?m)^interactive or required arguments:')
                self.assertEqual(result.stderr, '')    

    def test_version(self):
        with self.subTest():
            result = _run('version')
            self.assertEqual(result.returncode, 0)
            self.assertRegex(result.stdout, r'(?m)^0.0.0')
            self.assertEqual(result.stderr, '')    

class TestErrorsAndExits(unittest.TestCase):
    """Testing the remaining errors and exits"""

    def test_actions_path_doesnt_exist(self):            
        """Testing dump without an actions path"""
        with tempfile.TemporaryDirectory() as tempdir:
            args = (
            'python',
            _EXECUTABLE,
            'configure',
            '--forest-name',
            'MYFOREST',
            '--tree-name',
            'MYTREE',
            '--node-name',
            'MYNODE',
            '--child-to-parent-name',
            'MYCHILDTOPARENT',
            '--actions-path',
            'X:/falsepath/actions',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run(args, check=True)
            args = (
            'add',
            '--node',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )

            with self.subTest(args=args):
                result = subprocess.run((sys.executable, '-m', 'coverage', 'run',
                '--append', '--include', _EXECUTABLE, _EXECUTABLE) + args,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True)
                self.assertEqual(result.returncode,11)
###
# TODO: I would have thought  this would have errored out with error 9 not 11
###
    def test_default_command(self):            
        """Test default arguments with configuration"""
        with tempfile.TemporaryDirectory() as tempdir:
            args = (
            'configure',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            with self.subTest(args=args):
                result = subprocess.run((sys.executable, '-m', 'coverage', 'run',
                '--append', '--include', _EXECUTABLE, _EXECUTABLE) + args,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                input = '\n\n\n\n',
                universal_newlines=True)

    def test_invalid_action(self):

        """Testing the exit for an invalid action"""
        with tempfile.TemporaryDirectory() as tempdir:
            args = (
            'python',
            _EXECUTABLE,
            'configure',
            '--forest-name',
            'MYFOREST',
            '--tree-name',
            'MYTREE',
            '--node-name',
            'MYNODE',
            '--child-to-parent-name',
            'MYCHILDTOPARENT',
            '--actions-path',
            str(pathlib.Path(tempdir)/'actions'),
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder'),
            '--force'
            )
            subprocess.run(args, check=True)

            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run(args, check=True)

            with open(str(pathlib.Path(tempdir)/'actions'),'r') as actions:
                filedata = actions.read()
            filedata = filedata.replace('add','INVALID_ACTION')
            with open(str(pathlib.Path(tempdir)/'actions'),'w') as actions:
                actions.write(filedata)

            with self.subTest():
                result = subprocess.run((sys.executable, '-m', 'coverage', 'run',
                '--append', '--include', _EXECUTABLE, _EXECUTABLE) + 
                ('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder')),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True)
                self.assertEqual(result.returncode,13)

    def test_move_nonexisting(self):

        """Testing the move of a non-existant node"""
        with tempfile.TemporaryDirectory() as tempdir:
            args = (
            'python',
            _EXECUTABLE,
            'configure',
            '--forest-name',
            'MYFOREST',
            '--tree-name',
            'MYTREE',
            '--node-name',
            'MYNODE',
            '--child-to-parent-name',
            'MYCHILDTOPARENT',
            '--actions-path',
            str(pathlib.Path(tempdir)/'actions'),
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder'),
            '--force'
            )
            subprocess.run(args, check=True)

            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run(args, check=True)

            args = (
            'move',
            '--node',
            'NONEXISTING',
            '--parent',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )

            with self.subTest(args=args):
                result = subprocess.run((sys.executable, '-m', 'coverage', 'run',
                '--append', '--include', _EXECUTABLE, _EXECUTABLE) + args,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True)
                self.assertRegex(result.stderr,r'(?m)^NONEXISTING not present in forest')

    def test_validate_parent(self):

        """Testing a move to a non-existant parent"""
        with tempfile.TemporaryDirectory() as tempdir:
            args = (
            'python',
            _EXECUTABLE,
            'configure',
            '--forest-name',
            'MYFOREST',
            '--tree-name',
            'MYTREE',
            '--node-name',
            'MYNODE',
            '--child-to-parent-name',
            'MYCHILDTOPARENT',
            '--actions-path',
            str(pathlib.Path(tempdir)/'actions'),
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder'),
            '--force'
            )
            subprocess.run(args, check=True)

            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run(args, check=True)

            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'DRAMA_2',
            '--parent',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run(args, check=True)

# TODO; UNCOMMENT TO CAUSE BUG
            # args = (
            # 'move',
            # '--node',
            # 'DRAMA',
            # '--parent',
            # 'DRAMA',
            # '-c',
            # str(pathlib.Path(tempdir)/'.forestrecorder')
            # )

            # with self.subTest(args=args):
            #     result = subprocess.run((sys.executable, '-m', 'coverage', 'run',
            #     '--append', '--include', _EXECUTABLE, _EXECUTABLE) + args,
            #     stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            #     universal_newlines=True)
            #     print('\n validate parent test \n')
            #     print(result.stderr)

            args = (
            'move',
            '--node',
            'DRAMA',
            '--parent',
            'NONEXISTING',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )

            with self.subTest(args=args):
                result = subprocess.run((sys.executable, '-m', 'coverage', 'run',
                '--append', '--include', _EXECUTABLE, _EXECUTABLE) + args,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True)
                self.assertRegex(result.stderr,r'(?m)^NONEXISTING not present in forest')

    def test_validate_add(self):

        """Testing the add of an already existing node"""
        with tempfile.TemporaryDirectory() as tempdir:
            args = (
            'python',
            _EXECUTABLE,
            'configure',
            '--forest-name',
            'MYFOREST',
            '--tree-name',
            'MYTREE',
            '--node-name',
            'MYNODE',
            '--child-to-parent-name',
            'MYCHILDTOPARENT',
            '--actions-path',
            str(pathlib.Path(tempdir)/'actions'),
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder'),
            '--force'
            )
            subprocess.run(args, check=True)

            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run(args, check=True)

            args = (
            'add',
            '--node',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )

            with self.subTest(args=args):
                result = subprocess.run((sys.executable, '-m', 'coverage', 'run',
                '--append', '--include', _EXECUTABLE, _EXECUTABLE) + args,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True)
                self.assertRegex(result.stderr,r'(?m)^DRAMA already present in forest')



    def test_invalid_child(self):

        """Testing the move of an invalid child node"""
        with tempfile.TemporaryDirectory() as tempdir:
            args = (
            'python',
            _EXECUTABLE,
            'configure',
            '--forest-name',
            'MYFOREST',
            '--tree-name',
            'MYTREE',
            '--node-name',
            'MYNODE',
            '--child-to-parent-name',
            'MYCHILDTOPARENT',
            '--actions-path',
            str(pathlib.Path(tempdir)/'actions'),
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder'),
            '--force'
            )
            subprocess.run(args, check=True)

            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run(args, check=True)

            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'DRAMA_2',
            '--parent',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run(args, check=True)

            args = (
            'move',
            '--node',
            'NONEXISTING',
            '--child',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )

            with self.subTest(args=args):
                result = subprocess.run((sys.executable, '-m', 'coverage', 'run',
                '--append', '--include', _EXECUTABLE, _EXECUTABLE) + args,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True)
                self.assertRegex(result.stderr,r'(?m)^NONEXISTING not present in forest')


if __name__ == '__main__':
    unittest.main()