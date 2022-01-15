import subprocess

subprocess.run('pytest --cov=../src -vvv '
               '--cov-report=term-missing -n4 '
               '--force-sugar -p no:cacheprovider '
               '--html=pytest_report/index.html .')