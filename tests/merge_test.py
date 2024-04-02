import subprocess as sp
import os

def get_diff_filenames(from_branch=None, into_branch=None):
    # Make sure that at least branch merging into is defined
    assert(into_branch)
    # Base command to run as arg list
    command = ['git', '--no-pager', 'diff', '--name-only']
    
    # Append branch(es) to diff
    if not from_branch: command += [into_branch]
    else:               command += [from_branch, into_branch]

    # Get directory of this file, and change to it to run git diff
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    aa = sp.run(command, stdout=sp.PIPE)
    return aa.stdout.decode('utf-8')

if __name__ == '__main__':
    print(get_diff_filenames(into_branch='2.0.x'))