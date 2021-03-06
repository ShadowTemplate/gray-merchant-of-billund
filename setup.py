#!/usr/bin/env python3
import os
from pathlib import Path

from setuptools import setup, find_packages
from setuptools.command.install import install

from gray_merchant_of_billund.constants.gmob import (
    CACHE_DIR,
    RESOURCES_DIR,
    APPLICATION_DIR,
)

here = os.path.abspath(os.path.dirname(__file__))


def read_requirements(file_name):
    reqs = []
    with open(os.path.join(here, file_name)) as in_f:
        for line in in_f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            reqs.append(line)
    return reqs


with open(os.path.join(here, 'README.md')) as f:
    readme = f.read()


class PostInstallCommand(install):
    def run(self):
        install.run(self)
        for required_directory in [APPLICATION_DIR, RESOURCES_DIR, CACHE_DIR]:
            Path(required_directory).mkdir(exist_ok=True)


setup(
    name='gray-merchant-of-billund',
    version='1.0.0',
    url='https://github.com/ShadowTemplate/gray-merchant-of-billund',
    author="Gianvito Taneburgo",
    author_email="taneburgo+shadowtemplate@gmail.com",
    license='GNU General Public License v3.0',
    description='A set of building blocks for LEGO applications.',
    long_description=readme,
    long_description_content_type="text/markdown",
    python_requires='>=3.7',
    packages=find_packages(exclude=['tests']),
    install_requires=read_requirements('requirements.txt'),
    extras_require={
        "dev": read_requirements('requirements-dev.txt'),
    },
    include_package_data=True,
    package_data={
        '': ['*.yaml', '*.repo']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    cmdclass={
        'install': PostInstallCommand,
    },
)
