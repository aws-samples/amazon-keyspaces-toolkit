#  Amazon Keyspaces (for Apache Cassandra) developer toolkit cqlsh expansion

The Amazon Keyspaces toolkit contains common Cassandra tooling and helpers preconfigured for Amazon Keyspaces. The cqlsh-expansion utility extends native cqlsh functionality to include parameters and capabilities specific to Amazon Keyspaces such as support for Sigv4 Authentication.


## Using the cqlsh-expansion
One of the primary reasons to use the cqlsh-expansion utility is for utilizing the Sigv4 Authentication method. The cqlsh-expansion utility supports the [Sigv4 authentication plugin for the Python Cassandra driver](https://github.com/aws/aws-sigv4-auth-cassandra-python-driver-plugin). This plugin enables python applications to use IAM users, roles, and federated identities to add authentication information to Amazon Keyspaces (for Apache Cassandra) API requests using the AWS Signature Version 4 Process (SigV4).  To use Siv4 authentication with cqlsh-expansion utility, simply add the `--sigv4` flag to the existing cqlsh command on startup.   

Use the following commands to download and execute the setup script
 ``` wget https://raw.githubusercontent.com/Rathan8/amazon-keyspaces-toolkit/master/cloudshell/setup.sh -P ~/ 
 chmod +x setup.sh
 sh setup.sh
 ```


## Functional differences from cqlsh

### Sigv4 authentication
Instead of using the service specific credentials for an IAM user, you can use the `--sigv4` parameter to leverage the Sigv4 authentication plugin for temporary credentials.  This plugin enables IAM users, roles, and federated identities to add authentication information to Amazon Keyspaces (for Apache Cassandra) API requests using the AWS Signature Version 4 Process (SigV4). The plugin depends on the AWS SDK for Python (Boto3) and the [Amazon Keyspaces Sigv4 plugin for the DataStax python driver](https://github.com/aws/aws-sigv4-auth-cassandra-python-driver-plugin).

### New output for TTY
When creating a new cqlsh session with the cqlsh-expansion utility, it will show the default consistency level after establishing a new connection. We find customers using cqlsh may not be aware of the default consistency level of `ONE`, and additional transparency will lead to better operational excellence.  

### COPY FROM/TO required Consistency Levels  
When executing the `COPY FROM` import operation from the cqlsh-expansion utility, `LOCAL_QUORUM` will be strictly enforced. Executing `COPY FROM` with consistency level other than LOCAL_QUORUM will result in an SyntaxError.  This restriction is to provide better experience when using `COPY FROM` with Amazon Keyspaces. Amazon Keyspaces replicates all write operations three times across multiple Availability Zones for durability and high availability. Writes are durably stored before they are acknowledged using the `LOCAL_QUORUM` consistency level.

When executing the `COPY TO` export operation from the cqlsh-expansion utility, consistency of `ONE, LOCAL_ONE, or LOCAL_QUORUM` will be strictly enforced. Executing `COPY FROM` with consistency level other than these three will result in an SyntaxError.  This restriction is to provide better experience when using `COPY FROM` with Amazon Keyspaces. Amazon Keyspaces replicates all write operations three times across multiple Availability Zones for durability and high availability. 
```

# Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

# License

This library is licensed under the MIT-0 License. See the LICENSE file.
