from setuptools import find_packages, setup

with open("README.md", "r") as fid:
    long_description = fid.read()

with open("simple_slurm/__about__.py", "r") as fid:
    __version__ = None
    exec(fid.read())  # loads __version__

setup(
    name="simple_slurm",
    version=__version__,
    author="Arturo Mendoza",
    description="A simple Python wrapper for Slurm with flexibility in mind.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amq92/simple_slurm",
    packages=find_packages(),
    package_data={"": ["*.txt"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
    ],
    python_requires=">=3.6",
    license="GNU Affero General Public License v3",
    entry_points=dict(console_scripts=["simple_slurm=simple_slurm.cli:cli"]),
)
