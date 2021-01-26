from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="nfa",
    version="3.0.0",
    packages=["nfa",],
    install_requires=["reiter",],
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
