""" Setup file """
import os
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, "README.rst")) as f:
    README = f.read()


def get_version():
    with open("proximity/__init__.py") as f:
        for line in f:
            if line.startswith("__version__"):
                return eval(line.split("=")[-1])

REQUIREMENTS = [
    "arrow"
]

if __name__ == "__main__":
    setup(
        name="proximity",
        version=get_version(),
        description="approximations for equality testing",
        long_description=README,
        classifiers=[
            "Development Status :: 2 - Pre-Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.5",
            "Topic :: Software Development :: Libraries"
        ],
        author="Joe Cross",
        author_email="joe.mcross@gmail.com",
        url="https://github.com/numberoverzero/proximity",
        license="MIT",
        keywords="fuzz fuzzy approx approximate equality",
        platforms="any",
        include_package_data=True,
        packages=find_packages(exclude=("tests", "docs", "examples")),
        install_requires=REQUIREMENTS
    )
