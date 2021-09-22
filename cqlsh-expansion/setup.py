from setuptools import setup

# Setting up
setup(
    name="cqlsh-expansion",
    install_requires=[
        "futures>=2.1.6",
        "six>=1.15.0",
        "urllib3>=1.26.2",
        "python_dateutil>=2.8.1",
        "cassandra-driver>=3.25.0",
        "botocore",
        "boto3",
        "cassandra-sigv4>=4.0.2",
    ],
    include_package_data=True,
    packages=["config", "cqlshlib"],
    package_dir={
        "": ".",
        "cqlshlib": "./pylib/cqlshlib",
    },
    entry_points={
        'console_scripts': [
            'cqlsh-expansion.init=config.set:expansion_config',
        ],
    },
)
