"""Attempt to resolve library version conflict."""
import json
import subprocess
import sys
from typing import Union, List
from urllib import request

# import pytest
# from _pytest.config import ExitCode
from packaging.version import InvalidVersion, Version

ResolvedVersion = Union[Version, InvalidVersion, RuntimeWarning]

"""
def run_tests(package_name, failed_version):
    
    retcode = pytest.main()
    if ExitCode.TESTS_FAILED:
        attemp_resolve(package_name, failed_version)
        retcode = pytest.main()
    return retcode
"""


def install(package_name, next_version) -> int:
    """."""
    if next_version in ['6.2.4', '6.2.2']:
        return 1
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', f'{package_name}=={next_version}'])
    except subprocess.CalledProcessError as error:
        raise InvalidVersion(error)
    return 0


def __list_package_releases(package_name) -> list:
    """."""
    url = f'https://pypi.python.org/pypi/{package_name}/json'
    releases = json.loads(request.urlopen(url).read())['releases']
    return releases


def get_installed_version(package_name):
    """."""
    output = subprocess.run(
        [sys.executable, '-m', 'pip', 'show', f'{package_name}'], stdout=subprocess.PIPE)
    version = str(output.stdout).split(r'\r\n')[2].strip().split(':')[1].split()[0]
    return Version(version)


def attempt_resolve(package_name, installed_version: str, candidate_version: str) -> ResolvedVersion:
    """."""
    installed_version = Version(installed_version)
    candidate_version = Version(candidate_version)

    print('installed_version:', installed_version, ' candidate_version:', candidate_version)

    assert package_name is not None, f'Invalid package name {package_name}'
    assert isinstance(package_name, str), f'Invalid package name type {package_name}'
    assert len(package_name) > 2, f'Invalid package name {package_name}'
    assert isinstance(installed_version, Version), \
        f'Invalid installed_version type {type(installed_version)}, expected packaging.version.Version'
    assert isinstance(candidate_version, Version), \
        f'Invalid candidate_version type {type(candidate_version)}, expected packaging.version.Version'

    # collect all version for this package
    releases = __list_package_releases(package_name)
    assert installed_version.base_version in releases, f'{installed_version} is not in {releases}'
    assert candidate_version.base_version in releases, f'{candidate_version} is not in {releases}'

    # only dealing with candidate version greater than installed
    # retrieve the latest version fo the package
    latest_release_version = Version(max(releases))  # get_latest_version(releases)

    if candidate_version == installed_version:
        raise RuntimeWarning(
            f'No resolution required: {candidate_version.base_version} {installed_version.base_version}')

    assert installed_version < latest_release_version, 'Installed version should be less than latest release version.'
    assert candidate_version < latest_release_version, 'Candidate version should be less that latest release version.'
    assert candidate_version > installed_version, 'Only dealing with candidate versions greater than installed.'

    # order release version in descending order,
    release_versions = sorted(releases, reverse=True)

    # deal with only the latest release versions, installed version + 1 .. latest version

    top = top_releases(installed_version, release_versions)

    latest_releases: List[str] = release_versions[:top]
    for next_release in sorted(latest_releases):
        result = install(package_name, next_release)
        if result > 0:  # resolution needed, install next version
            continue
        else:
            installed_version = next_release
            break

    return Version(installed_version)


def top_releases(installed_version, release_versions):
    top: int = 0
    for count, item in enumerate(release_versions):
        if Version(item) == installed_version:
            top = count
            break
    return top


"""
import re
from pathlib import Path
from pprint import pprint

from typing import List

requirement_txt_path = Path('C:\\Users\\Andrii_Kokhan\\PycharmProjects\\ds-cf-azureml-api-v2\\requirements.txt')
requirement_devel_txt_path = Path(
    'C:\\Users\\Andrii_Kokhan\\PycharmProjects\\ds-cf-azureml-api-v2\\requirements-devel.txt')
all_requirement_txt_path = Path(
    'C:\\Users\\Andrii_Kokhan\\PycharmProjects\\ds-cf-azureml-api-v2\\all_requirements.txt')


def merge_requirements(requirement_txt_path: Path,
                       requirement_devel_txt_path: Path,
                       result_file_path: Path) -> List[str]:
    with open(requirement_txt_path) as prod, \
            open(requirement_devel_txt_path) as dev, \
            open(result_file_path, 'w', encoding='utf8') as all_reqs:
        all_requirements = prod.readlines() + dev.readlines()
        only_reqs = []
        for line in all_requirements:
            if line:
                if not line.startswith('#'):
                    if line.strip():
                        only_reqs.append(line)
                        all_reqs.write(line)
    return only_reqs


def requirements_as_dict(result_file_path: Path) -> dict:
    all_versions = dict()
    with open(result_file_path, 'r', encoding='utf8') as requirements:
        all_requirements = requirements.readlines()
        print(all_requirements, len(all_requirements))
        for line in all_requirements:
            if line:
                if not line.startswith('#'):
                    delimiter = re.findall(pattern=r'==|>=|<=|>|<|$', string=line)[0]
                    if delimiter.strip() != '':
                        key, value = ''.join(line).split(delimiter)
                        all_versions[key] = value.rstrip('\n')
                    else:
                        key = ''.join(line).rstrip('\n')
                        all_versions[key] = 'latest'
    assert len(all_versions) == len(all_requirements), f'{len(all_versions)} != {len(all_requirements)}'
    return all_versions


all_reqs = merge_requirements(requirement_txt_path, requirement_devel_txt_path, all_requirement_txt_path)
reqs_as_dict = requirements_as_dict(all_requirement_txt_path)
pprint(reqs_as_dict)
print(len(reqs_as_dict))

"""

if __name__ == '__main__':
    print('Attempting resolve if necessary...')
    installed = '6.2.1'
    candidate = '7.0.0'
    resolved_version: ResolvedVersion = attempt_resolve('pytest', installed, candidate)
    print('resolved version', resolved_version, 'candidate_version', candidate, 'installed_version',
          installed)
