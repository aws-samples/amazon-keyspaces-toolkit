# Accessing Amazon Keyspaces from AWS CloudShell using cqlsh expansion toolkit

AWS CloudShell is a browser-based shell that makes it easy to securely manage, explore, and interact with your AWS resources. Some Common development and operations tools are pre-installed. When using AWS CloudShell you have persistent storage of 1 GB for each AWS Region at no additional cost. The persistent storage is located in your home directory ($HOME) and is private to you. Unlike ephemeral environment resources that are recycled after each shell session ends, data in your home directory persists between sessions.

This toolkit helps with setup of cqlsh-expansion utility to connect to Amazon keyspaces from AWS CloudShell, as part of setup it downloads cqlsh using pip from Python Package Index (PyPI) https://pypi.org/project/cqlsh/
OR you can install the CQLSH standalone using a binary tarball for more info refer to https://cassandra.apache.org/doc/latest/getting_started/installing.html#installing-the-binary-tarball

Downloads digital certificate to encrypt your connections using Transport Layer Security (TLS), also installs necessary pip and other dependencies in home directory so that it persists and available the next time you start a new CloudShell session

Run the following commands to download and execute the setup script
 ```
 wget https://raw.githubusercontent.com/aws-samples/amazon-keyspaces-toolkit/master/aws-cloudshell/setup.sh
 bash setup.sh
 ```
## Using the cqlsh-expansion
One of the primary reasons to use the cqlsh-expansion utility is for utilizing the Sigv4 Authentication method. The cqlsh-expansion utility supports the [Sigv4 authentication plugin for the Python Cassandra driver](https://github.com/aws/aws-sigv4-auth-cassandra-python-driver-plugin). This plugin enables python applications to use IAM users, roles, and federated identities to add authentication information to Amazon Keyspaces (for Apache Cassandra) API requests using the AWS Signature Version 4 Process (SigV4). To use Sigv4 authentication with cqlsh-expansion utility, simply add the `--auth-provider "SigV4AuthProvider"` flag to the existing cqlsh command on startup.

The plugin depends on the AWS SDK for Python (Boto3), uses boto3.Session to obtain credentials to connect to Amazon keyspaces

To connect to Amazon keyspaces using cqlsh-expansion

``` cqlsh-expansion cassandra.us-east-2.amazonaws.com 9142 --ssl --auth-provider "SigV4AuthProvider" ```

## Additional info
cqlsh-expansion https://github.com/aws-samples/amazon-keyspaces-toolkit/tree/master/cqlsh-expansion#readme

AWS CloudShell https://docs.aws.amazon.com/cloudshell/latest/userguide/welcome.html
