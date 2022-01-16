import subprocess

import sys

print(f'Running with Python {sys.version_info}.')

subprocess.run('pytest --cov=src -vvv '
               '--cov-report=term-missing  '
               '-p no:cacheprovider '
               '--html=./reports/pytest_report/index.html test')

subprocess.run('flake8 --tee . --output-file=./reports/flake8-report.txt')

import contextlib

path = './reports/mypy-report.txt'
with open(path, 'w') as f:
    with contextlib.redirect_stdout(f):
        subprocess.run('mypy .')
