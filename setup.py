import setuptools


with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='simple-slurm',
    version='0.1.5',
    author='Arturo Mendoza',
    description='A simple Python wrapper for Slurm with flexibility in mind.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/amq92/simple-slurm',
    packages=setuptools.find_packages(),
    package_data={'': ['*.txt']},
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
