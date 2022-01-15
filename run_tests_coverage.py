import subprocess

subprocess.run('pytest --cov=../src -vvv '
               '--cov-report=term-missing -n4 '
               '--force-sugar -p no:cacheprovider '
               '--html=../reports/pytest_report/index.html .')

subprocess.run('flake8 --tee ../ --output-file=../reports/flake8-report.txt')