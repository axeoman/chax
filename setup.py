import os
import re
import site

from setuptools import setup, find_packages

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'chax', '__init__.py'),
          'r') as init_file:
    try:
        version = \
        re.findall(r"^__version__ ?= ?['\"]([^'\"]+)['\"]$", init_file.read(), re.MULTILINE)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')

setup(
    name="chax",
    version=version,
    url="https://github.com/axeoman/chax",
    author="Atavin Alexey",
    install_requires=[
        "aiohttp",
        "pyyaml",
        "aioredis"
    ],
    keywords="chax",
    packages=find_packages(exclude=["tests"]),
    entry_points={
                       'console_scripts': [
                           'chax=chax:main',
                       ]
    },
    python_requires=">=3.6",
    data_files=[(f"{site.getsitepackages()[0]}/chax", ["chax/defaults.yaml"])],
)
