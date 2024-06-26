from setuptools import setup, find_packages
import os

def read(fname):
    return open(fname).read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name = "GoodWinRM",
    version = "0.1",
    description="Python WinRM Remote Shell",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url = "https://github.com/h3x0c4t/goodwinrm",
    author = "nu11z",
    packages=find_packages(),
    install_requires=requirements,
    entry_points = {
        "console_scripts": ["goodwinrm=goodwinrm.goodwinrm:main"],
    }
)
