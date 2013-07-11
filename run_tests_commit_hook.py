#!/usr/bin/env python

import subprocess
import re

TESTS_DIR = './tests'
FILE_EXTENSION = '.php'
TEST_RUNNER = '/usr/local/zend/bin/phpunit --stderr -c ./phpunit.xml'


def test_modified_files():
    """
    Pre-commit hook to run the tests matching the modified php files.
    To install the hook, edit .hg/hgrc and add the following lines:

    [hooks]
    pretxncommit.unittests = python ./run_tests_commit_hook.py
    """

    out, err = subprocess.Popen('hg st -ma', shell=True, stdout=subprocess.PIPE).communicate()
    files = out.splitlines()
    modified_files = filter(lambda y: y.endswith(FILE_EXTENSION), map(lambda x: x[2:].split('/')[-1], files))
    test_files = map(lambda x: re.sub(FILE_EXTENSION + '$', 'Test' + FILE_EXTENSION, x), modified_files)

    exit_status = 0
    for test_file in test_files:
        out, err = subprocess.Popen('find . -name "%s" 2>/dev/null' % test_file, shell=True, stdout=subprocess.PIPE, cwd=TESTS_DIR).communicate()
        for found_test_file in out.splitlines():
            print "running %s" % found_test_file
            status = subprocess.call('%s %s' % (TEST_RUNNER, found_test_file), shell=True, cwd=TESTS_DIR)
            if status > 0:
                exit_status = status

    return exit_status

if __name__ == '__main__':
    import sys

    SKIP_HOOK = 'skiptests'
    commit_message, err = subprocess.Popen('hg tip --template "{desc}"', shell=True, stdout=subprocess.PIPE).communicate()
    if SKIP_HOOK in commit_message:
        print "Pre-commit hook was skipped!"
        sys.exit(0)

    exit_status = test_modified_files()
    if exit_status > 0:
        # save the commit message so we don't need to retype it
        subprocess.call('hg tip --template "{desc}" > .hg/commit.save', shell=True)
        print >> sys.stderr, '\ncommit message saved to .hg/commit.save'

    sys.exit(exit_status)
