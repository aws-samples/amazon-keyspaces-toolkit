import pathlib

from setuptools import setup, find_packages

# Get the long description from the README file
long_description = (pathlib.Path(__file__).parent.resolve() / 'README.md').read_text(encoding='utf-8')

# Setting up
setup(
    name="cqlsh-expansion",
    version='0.9.6',
    description='The cqlsh-expansion utility extends native cqlsh functionality to include cloud native capabilities',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url = 'https://github.com/aws-samples/amazon-keyspaces-toolkit/tree/master/cqlsh-expansion',
    python_requires='>=3.6',
    install_requires=[
        "six>=1.12.0",
        "cassandra-driver",
        "boto3",
        "cassandra-sigv4>=4.0.2",
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    author='Michael Raney, Sri Rathan Rangisetti',
    keywords = 'cql,cqlsh,cqlsh-expansion,aws,keyspaces,cassandra,sigv4',
    packages=["cqlsh_expansion", "cqlshlib"],
    package_data={'config':  ['*'], 'cqlsh_expansion':['*']},
    include_package_data=True,
    exclude_package_data={'.': ['./cqlshlib/test']},
    entry_points={
        'console_scripts': [
            'cqlsh-expansion.init=cqlsh_expansion.post_install:initialize_cassandra_directory',
            'cqlsh=cqlsh_expansion.__main__:main',
            'cqlsh-expansion=cqlsh_expansion.__main_expansion__:main']
    }
)