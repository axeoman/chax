from setuptools import setup, find_packages
from chax import __version__, __author__

setup(
    name="chax",
    version=__version__,
    url="https://github.com/axeoman/chax",
    author=__author__,
    install_requires=[

    ],
    keywords="chax chat",
    packages=find_packages(exclude=["tests"])
)