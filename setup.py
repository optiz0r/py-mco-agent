import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

version_info = {}
with open(os.path.join(os.path.dirname(__file__), "mco_agent", "version.py")) as fp:
    exec(fp.read(), version_info)
pkg_version = version_info['__version__']

setuptools.setup(
    name="py-mco-agent",
    version=pkg_version,
    author="Ben Roberts",
    author_email="me@benroberts.net",
    description="A library for implementing Mcollecting agents in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/optiz0r/py-mco-agent",
    packages=setuptools.find_packages(exclude=['tests*']),
    package_data = {
        'mco_agent': ['mco_agent/schemas/*.json'],
    },
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.6',
)
