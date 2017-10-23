from setuptools import setup, find_packages

from chax import __version__, __author__

setup(
    name="chax",
    version=__version__,
    url="https://github.com/axeoman/chax",
    author=__author__,
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
)