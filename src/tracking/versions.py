"""Attempt to resolve library version conflict."""
import json
import subprocess
import sys
from typing import Union, List, re
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


def install(package_name, next_version) -> ResolvedVersion:
    """."""
    if next_version in ['6.2.1', '6.2.2']:
        return 1
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', f'{package_name}=={next_version}'])
    except subprocess.CalledProcessError as error:
        raise InvalidVersion(error)
    return 0


def list_package_releases(package_name) -> list:
    """."""
    url = f'https://pypi.python.org/pypi/{package_name}/json'
    releases = json.loads(request.urlopen(url).read())['releases']
    return releases


def _get_release_versions(package_name):
    """."""
    output = subprocess.run(
        [sys.executable, '-m', 'pip', 'index', 'versions', f'{package_name}'], stdout=subprocess.PIPE)
    return output


def get_latest_version(package_name) -> Version:
    """."""
    output = _get_release_versions(package_name)
    version = str(output.stdout).split(r'\r\n')[3].strip().split(':')[1].split()[0]
    pattern = re.compile(r'\d.\d.\d')
    format_expected = pattern.match(version)
    assert format_expected, ValueError(f'{version} has unexpected version format, <major.minor.micro> is expected.')

    return Version(version)


def get_installed_version(package_name):
    """."""
    output = _get_release_versions(package_name)
    version = str(output.stdout).split(r'\r\n')[2].strip().split(':')[1].split()[0]
    return Version(version)


def get_next_micro_version(release):
    """."""
    return release.micro + 1


def get_micro_version(release):
    """."""
    return release.micro


def get_minor_version(release: Version) -> int:
    """."""
    return release.minor


def get_major_version(release: Version) -> int:
    """."""
    return release.major


def get_latest_releases(release_versions, releases_diff) -> list:
    """."""
    return release_versions[:releases_diff + 2]


def attemp_resolve(package_name, installed_version: Version, candidate_version: Version) -> ResolvedVersion:
    """."""
    assert package_name is not None, f'Invalid package name {package_name}'
    assert isinstance(package_name, str), f'Invalid package name type {package_name}'
    assert len(package_name) > 2, f'Invalid package name {package_name}'
    assert isinstance(installed_version, Version), \
        f'Invalid installed_version type {type(installed_version)}, expected packaging.version.Version'
    assert isinstance(candidate_version, Version), \
        f'Invalid candidate_version type {type(candidate_version)}, expected packaging.version.Version'

    # collect all version for this package
    releases = list_package_releases(package_name)
    assert installed_version.base_version in releases, f'{installed_version} is not in {releases}'
    assert candidate_version.base_version in releases, f'{candidate_version} is not in {releases}'

    # only dealing with candidate version greater than installed
    # retrieve the latest version fo the package
    latest_release_version = get_latest_version(package_name)

    if candidate_version.base_version == installed_version.base_version:
        raise RuntimeWarning(
            f'No resolution required: {candidate_version.base_version} {installed_version.base_version}')

    assert get_micro_version(installed_version) < get_micro_version(
        latest_release_version), 'Installed version should be less than latest release version.'
    assert get_micro_version(candidate_version) < get_micro_version(
        latest_release_version), 'Candidate release version should be less that latest release version.'
    assert get_micro_version(candidate_version) > get_micro_version(
        installed_version), 'Only dealing with candidate versions greater than installed.'

    # order release version in descending order,
    # TODO is it really necessary to sort?
    release_versions = sorted(releases, reverse=True)

    # deal with only the latest release versions, installed version + 1 .. latest version
    releases_diff = get_micro_version(latest_release_version) - get_micro_version(candidate_version)
    latest_releases: List[str] = get_latest_releases(release_versions, releases_diff)
    latest_releases = sorted(latest_releases, reverse=False)
    for next_release in latest_releases:
        result = install(package_name, next_release)
        if not result:  # resolution needed, install next version
            continue
        else:
            installed_version = next_release
            break

    return Version(installed_version)


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
    print('try resolve')
    attemp_resolve('pytest', Version('6.2.1'), Version('6.2.5'))
