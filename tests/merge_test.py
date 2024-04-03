import subprocess as sp
import os
import logging
import pytest

import logging


class TestAutomater:

    regression_test_dict = {
        'mesh_builder.py':      ['test_mesh.py'],
        'mesh.py':              ['test_mesh.py'],
        'neighbour_graph.py':   ['test_mesh.py'],
        'metadata.py':          ['test_mesh.py'],
        'aggregated_cellbox.py':['test_mesh.py'],
        'boundary.py':          ['test_mesh.py'],
        'cellbox.py':           ['test_mesh.py'],
        'direction.py':         ['test_mesh.py'],
        'environment_mesh.py':  ['test_mesh.py']
    }

    unit_test_dict = {
        'mesh_builder.py':      ['test_mesh_builder.py'],
        'mesh.py':              [],
        'neighbour_graph.py':   ['test_neighbour_graph.py'],
        'metadata.py':          [],
        'aggregated_cellbox.py':[],
        'boundary.py':          ['test_boundary.py'],
        'cellbox.py':           ['test_cellbox.py'],
        'direction.py':         [],
        'environment_mesh.py':  ['test_env_mesh.py']
    }

    def __init__(self, from_branch=None, into_branch=None, regression=True, unit=True):
        """
        Runs through test suite only taking into account relevant tests for the 
        modified files

        Args:
            from_branch (str): 
                Git branch that you want to test. 
                Defaults to currently active branch.
            into_branch (str): 
                Git branch that 'from_branch' is being compared to. 
                Defaults to main.
            regression (bool, optional): 
                Flag for running regression tests. 
                Defaults to True.
            unit (bool, optional): 
                Flag for running unit tests. 
                Defaults to True.
        """
        # Set working directory
        self.repo_dir = self.get_base_dir()
        os.chdir(self.repo_dir)
        logging.debug(f'Set base directory to {os.getcwd()}')
        
        # Set default branch to compare to if not user set
        if not into_branch:
            into_branch = "main"

        # Get files that are different between branches
        diff_files = self.get_diff_filenames(from_branch=from_branch, 
                                             into_branch=into_branch)

        # Run relevant tests
        if regression:  self.run_regression_tests(diff_files)
        if unit:        self.run_unit_tests(diff_files)

    def _run_tests(self, diff_files, test_dir, test_dict):
        """
        Runs relevant regression or unit tests within 'test_dir'

        Args:
            diff_files (list): 
                List of files that are different from comparison branch
            test_dir (str): 
                Directory where relevant tests are located
            test_dict (dict): 
                Mapping between diff file and relevant test
        """
        relevant_tests = []
        # Change to reg test folder
        os.chdir(test_dir)
        
        # For each file with a diff
        for file in diff_files:
            # Get relevant regression tests
            relevant_tests += self.get_relevant_tests(file, 
                                                      test_dict)
        # Get list of unique reg tests to run
        relevant_tests = list(set(relevant_tests))

        # If there are tests to run
        if relevant_tests:
            logging.info('Running the following tests:')
            # Run each test
            for test in relevant_tests:
                test_file_path = os.path.join(test_dir, test)
                logging.info(f'\t- {test_file_path}')
                pytest.main(['-x', test_file_path, '-v'])

        # Otherwise provide a message
        else:
            logging.info(" --- No relevant tests found --- ")
        
        # Change back to repo base directory
        os.chdir(self.repo_dir)

    def run_regression_tests(self, diff_files):
        """
        Runs relevant regression tests for files within 'diff_files' 

        Args:
            diff_files (list): 
                List of files that are different from comparison branch
        """
        # Get base directory for regression tests
        reg_test_dir = os.path.join(self.repo_dir, 
                                    'tests', 
                                    'regression_tests')
        logging.info("Attempting regression tests...")
        self._run_tests(diff_files, reg_test_dir, self.regression_test_dict)

    def run_unit_tests(self, diff_files):
        """
        Runs relevant unit tests for files within 'diff_files' 

        Args:
            diff_files (list): 
                List of files that are different from comparison branch
        """
        # Get base directory for unit tests
        unit_test_dir = os.path.join(self.repo_dir, 
                                    'tests', 
                                    'unit_tests')
        logging.info("Attempting unit tests...")
        self._run_tests(diff_files, unit_test_dir, self.unit_test_dict)

    @staticmethod
    def get_base_dir():
        """
        Get base folder for repo.
        """
        # Get parent directory of this file, and change to it to run git diff
        dir_path = os.path.dirname(os.path.realpath(__file__))
        par_path = os.path.join(dir_path, os.pardir)

        return os.path.abspath(par_path)

    @staticmethod
    def get_diff_filenames(from_branch=None, into_branch=None):
        """
        Gets a list of files that have changed between 'from_branch' and 'into_branch'
        """
        # Make sure that at least branch merging into is defined
        assert(into_branch), "Must specify branch being 'diff'ed with"
        # Base command to run as arg list
        command = ['git', '--no-pager', 'diff', '--name-only']
        
        # Append branch(es) to diff
        if not from_branch: command += [into_branch]
        else:               command += ['--merge-base', from_branch, into_branch]

        # Run git diff
        git_diff = sp.run(command, stdout=sp.PIPE)
        git_diff = git_diff.stdout.decode('utf-8')
        # Extract list of files that have been modified
        raw_filenames = git_diff.split('\n')

        # Sanitise raw list to avoid empty lines
        diff_files = []
        if from_branch:
            logging.info( 'Following files different between ' + \
                         f'"{from_branch}" and "{into_branch}"')
        else:
            logging.info( 'Following files different between ' + \
                         f'current branch and "{into_branch}"')
            
        for filename in raw_filenames:
            if filename != '':
                logging.info(f'\t- {filename}')
                diff_files += [filename]

        return diff_files

    def get_relevant_tests(self, diff_file, test_dict):
        """
        Determines the relevant tests to run from filename
        """
        relevant_tests = []
        # For each available mapping of files to tests
        for package_file, package_tests in test_dict.items():
            # If found a match 
            if package_file in diff_file:
                relevant_tests += package_tests

        return relevant_tests
