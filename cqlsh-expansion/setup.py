from setuptools import setup

# Setting up
setup(
    name="cqlsh-expansion",
    install_requires=[
        "futures>=2.1.6",
        "six>=1.15.0",
        "urllib3>=1.26.2",
        "python_dateutil>=2.8.1",
        "cassandra-driver>=3.12.0,<3.18.0",
        "botocore",
        "boto3",
        "cassandra-sigv4>=4.0.2",
    ],
    packages=["config", "cqlshlib"],
    package_data={'config':  ['*']},
    include_package_data=True,
    package_dir={
        "": ".",
        "cqlshlib": "./pylib/cqlshlib"},
    exclude_package_data={'.': ['./pylib/cqlshlib/test']},
    entry_points={
        'console_scripts': [
            'cqlsh-expansion.init=config.post_install:initialize_cassandra_directory'],
    },
)
