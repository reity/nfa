from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read().replace(".. include:: toc.rst\n\n", "")

# The lines below can be parsed by `docs/conf.py`.
name = "nfa"
version = "3.1.0"

setup(
    name=name,
    version=version,
    packages=[name,],
    install_requires=["reiter~=0.5",],
    license="MIT",
    url="https://github.com/reity/nfa",
    author="Andrei Lapets",
    author_email="a@lapets.io",
    description="Library for defining and working with native "+\
                "Python implementations of NFAs.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
)
