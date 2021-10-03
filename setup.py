from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read().replace(".. include:: toc.rst\n\n", "")

# The line below is parsed by `docs/conf.py`.
version = "3.0.0"

setup(
    name="nfa",
    version=version,
    packages=["nfa",],
    install_requires=["reiter~=0.2",],
    license="MIT",
    url="https://github.com/reity/nfa",
    author="Andrei Lapets",
    author_email="a@lapets.io",
    description="Library for defining and working with native "+\
                "Python implementations of NFAs.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    test_suite="nose.collector",
    tests_require=["nose"],
)
