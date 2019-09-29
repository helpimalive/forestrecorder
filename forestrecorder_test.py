#!/usr/bin/python3
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
# spec = spec_from_loader("forestrecorder", SourceFileLoader("forestrecorder", str(os.path.dirname(os.path.abspath(__file__)))))
# forestrecorder = module_from_spec(spec)
# spec.loader.exec_module(forestrecorder)

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

            # with self.subTest(args=args):
            subprocess.run([x for x in args], check = True)
            # shutil.rmtree(tempdir)

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
        """Test help on the main parser."""
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

            subprocess.run([x for x in args], check = True)

            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )

            subprocess.run([x for x in args], check = True)

            with self.subTest(args=args):
                result = _run('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)
                self.assertEqual(result.returncode,0)
                self.assertRegex(result.stdout,r'{"DRAMA": {}}')
                self.assertEqual(result.stderr,'')

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

            subprocess.run([x for x in args], check = True)

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

            subprocess.run([x for x in args], check = True)


            with self.subTest(args=args):
                result = _run('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)
                self.assertEqual(result.returncode,0)
                self.assertRegex(result.stdout,r'{"DRAMA": {"COURTROOM_DRAMA": {"PERIOD_DRAMA": {}}}}')
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

            subprocess.run([x for x in args], check = True)

            with self.subTest(args=args):
                result = _run('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)
                self.assertEqual(result.returncode,0)
                self.assertRegex(result.stdout,r', "COMEDY": {}')
                self.assertEqual(result.stderr,'')

                    
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
        """Test help on the main parser."""
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

            subprocess.run([x for x in args], check = True)

            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run([x for x in args], check = True)

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
            subprocess.run([x for x in args], check = True)

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
            subprocess.run([x for x in args], check = True)

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
            '--parent',
            'DRAMA',
            '--child',
            'COURTROOM_DRAMA',
            '--non-interactive',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run([x for x in args], check = True)

            with self.subTest(args=args):
                result = _run('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)
                self.assertEqual(result.returncode,0)
                self.assertRegex(result.stdout,r' {"PERIOD_DRAMA": {"COURTROOM_DRAMA":')
                self.assertEqual(result.stderr,'')

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
            subprocess.run([x for x in args], check = True)

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
            subprocess.run([x for x in args], check = True)

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

                subprocess.run([x for x in args], check = True)

                args = (
                'python',
                _EXECUTABLE,
                'add',
                '--node',
                'DRAMA',
                '-c',
                str(pathlib.Path(tempdir)/'.forestrecorder')
                )
                subprocess.run([x for x in args], check = True)

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
                subprocess.run([x for x in args], check = True)

                args = (
                'python',
                _EXECUTABLE,
                'remove',
                '--node',
                'COURTROOM_DRAMA',
                '-c',
                str(pathlib.Path(tempdir)/'.forestrecorder')
                )
                subprocess.run([x for x in args], check = True)

                with self.subTest(args=args):
                    result = _run('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)
                    self.assertEqual(result.returncode,0)
                    self.assertRegex(result.stdout,r'{"DRAMA": {}}')
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
                subprocess.run([x for x in args], check = True)
                args = (
                'python',
                _EXECUTABLE,
                'add',
                '--node',
                'COURTROOM_DRAMA',
                '--parent',
                'COMEDY',
                '-c',
                str(pathlib.Path(tempdir)/'.forestrecorder')

                )
                subprocess.run([x for x in args], check = True)
                result = _run('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)
             
                args = (
                'python',
                _EXECUTABLE,
                'remove',
                '--node',
                'COMEDY',
                '--non-interactive',
                '-c',
                str(pathlib.Path(tempdir)/'.forestrecorder')
                )
                subprocess.run([x for x in args], check = True)
                result = _run('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)

                with self.subTest(args=args):
                    result = _run('dump','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)
                    self.assertEqual(result.returncode,0)
                    self.assertTrue("COMEDY" not in result.stdout)
                    self.assertEqual(result.stderr,'')


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
                # self.assertRegex(result.stdout, r'(?m)^interactive or required arguments:')
                self.assertEqual(result.stderr, '')    
    def test_history(self):
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

            subprocess.run([x for x in args], check = True)

            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )

            subprocess.run([x for x in args], check = True)

            args = (
            'python',
            _EXECUTABLE,
            'remove',
            '--node',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )

            subprocess.run([x for x in args], check = True)

            with self.subTest():
                result = _run('history','-c',str(pathlib.Path(tempdir)/'.forestrecorder'),)
                self.assertEqual(result.returncode, 0)
                self.assertRegex(result.stdout, r'Time\tadd\tDRAMA')
                self.assertRegex(result.stdout, r'Time\tremove\tDRAMA')
                self.assertEqual(result.stderr, '')  

###
#'TODO: how to add one child to more than one parent
###

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

            subprocess.run([x for x in args], check = True)

            args = (
            'python',
            _EXECUTABLE,
            'add',
            '--node',
            'DRAMA',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run([x for x in args], check = True)

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
            subprocess.run([x for x in args], check = True)

            args = (
            'python',
            _EXECUTABLE,
            'dump',
            '-c',
            str(pathlib.Path(tempdir)/'.forestrecorder')
            )
            subprocess.run([x for x in args], check = True)

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

class NonExposedFunctions(unittest.TestCase):
    """Test the exit abnormally function."""
    def test_exit_abnormally(self):
        with self.subTest():
            with self.assertRaises(SystemExit) as cm:
                forestrecorder._exit_abnormally('add_existing','exit_error_14')
                out,err = self.capfd.readouterr()
                self.assertEqual('exit_error_14',out)
                self.assertEqual(cm.exception.code, 14)
            subprocess.run((
                sys.executable, '-m', 'coverage', 'run',
                '--append', '--include', _EXECUTABLE, _EXECUTABLE) ,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True)
        
    def test_exit_on_error(self):
        with self.subTest():
            forestrecorder._exit_on_error('input_error','exit_here')
            self.assertEqual(1,1)

    def prompt(self):
            forestrecorder._prompt('value','message')
            out,err = self.capfd.readouterr()
            self.assertEqual(out,'value')

    @pytest.fixture(autouse=True)
    def capfd(self, capfd):
        self.capfd = capfd



    # def newline(self):        
    #         forestrecorder._newline_input('message')



if __name__ == '__main__':
    unittest.main()
    