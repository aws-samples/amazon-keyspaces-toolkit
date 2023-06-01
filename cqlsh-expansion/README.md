
# The Amazon Keyspaces (for Apache Cassandra) developer toolkit cqlsh-expansion script

The Amazon Keyspaces toolkit contains common Cassandra tooling and helpers preconfigured for Amazon Keyspaces. The cqlsh-expansion utility extends native cqlsh functionality to include parameters and capabilities specific to Amazon Keyspaces without breaking compatibility with Apache Cassandra. This includes support for the Sigv4 Authentication plugin. Normally, cqlsh is packaged with the full distribution of Apache Cassandra, but since Amazon Keyspaces is a serverless database service, we only require the cqlsh scripts and not the full distribution. This repository provides a lightweight distribution of cqlsh that can be installed on platforms that support python. 


## Installing cqlsh-expansion

To install the cqlsh-expansion python package you can run the following pip command. The command below executes a “pip install” that will install the cqlsh-expansion scripts. It will also install a requirements file containing a list of dependencies. The --`user` flag tells pip to use the Python *user install directory* for your platform. Typically ~/.local/ on unix based systems. 

```
pip install --user cqlsh-expansion 
```

Alternatively, if you are using python3 as default you may have to use the following command to install the cqlsh-expansion package. 

```
python3 -m pip install --user cqlsh-expansion
```

## Setup cqlsh-expansion to connect to Amazon Keyspaces

To use the cqlsh-expansion with Amazon Keyspaces you can use the following post install script or by following the instructions found in the official [Amazon Keyspaces documentation.](https://docs.aws.amazon.com/keyspaces/latest/devguide/programmatic.cqlsh.html) 

By default the cqlsh-expansion is not configured with ssl enabled, but the package includes a [post install script](https://github.com/aws-samples/amazon-keyspaces-toolkit/blob/master/cqlsh-expansion/config/post_install.py) helper to quickly setup your environment after installation. The script will place the necessary configuration and SSL certificate in the user’s *.cassandra* directory. Amazon Keyspaces only accepts secure connections using Transport Layer Security (TLS). Encryption in transit provides an additional layer of data protection by encrypting your data as it travels to and from Amazon Keyspaces. The post install script first will create the .cassandra directory if it does not exist already. Then it will copy a [preconfigure a cqlshrc file](https://github.com/aws-samples/amazon-keyspaces-toolkit/blob/master/cqlsh-expansion/config/cqlshrc_template) and the Starfield digital certificate into the .cassandra directory. The .cassandra directory will be created in the user home directory as it is the default location. As best practice, please review the [post install script](https://github.com/aws-samples/amazon-keyspaces-toolkit/blob/master/cqlsh-expansion/config/post_install.py)before executing. Modifications made by this post install script will not be undone if uninstalling the cqlsh-expansion with pip. 

```

cqlsh-expansion.init

```

## Connection to Amazon Keyspaces

Now that you have you cqlsh-expansion installed and have setup up the configuration for SSL communication with Amazon Keyspaces, you can now connect to the Amazon Keyspaces services using your IAM access keys or Service Specific Credentials. 

### Choose a region and endpoint

To connect to Amazon Keyspaces you will need to choose one of the [service endpoints](https://docs.aws.amazon.com/keyspaces/latest/devguide/programmatic.endpoints.html). You can also connect to Amazon Keyspaces using [Interface VPC endpoints](https://docs.aws.amazon.com/keyspaces/latest/devguide/vpc-endpoints.html) to enable private communication between your virtual private cloud (VPC) running in Amazon VPC and Amazon Keyspaces. For example, to connect to the Keyspaces service in US East (N. Virginia) (us-east-1) you will want to use the [cassandra.us-east-1.amazonaws.com](http://cassandra.us-east-1.amazonaws.com/) service endpoint.  All communication with Amazon Keyspaces will be over port 9142. 

### Choose authentication method and connect
To provide users and applications with credentials for programmatic access to Amazon Keyspaces resources, you can do either of the following:

#### Connect with IAM access keys (users,roles, and federated identities)

For enhanced security, we recommend to create IAM access keys for IAM users and roles that are used across all AWS services. To use IAM access keys to connect to Amazon Keyspaces, customers can use the Signature Version 4 Process (SigV4) authentication plugin for Cassandra client drivers. To learn more about how the Amazon Keyspaces SigV4 plugin enables [IAM users, roles, and federated identities](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html) to authenticate in Amazon Keyspaces API requests, see [AWS Signature Version 4 process (SigV4)](https://docs.aws.amazon.com/general/latest/gr/signature-version-4.html). 

After you have the credentials setup with [privileges](https://docs.aws.amazon.com/keyspaces/latest/devguide/security_iam_service-with-iam.html) to access Amazon Keyspaces system tables, you can execute the following command to connect to Amazon Keyspaces with CQLSH using the Sigv4 process.  

Validate the module name and classname, region_name based on keyspaces endpoint in cqlshrc file. 

```
[auth_provider]
;; you can specify any auth provider found in your python environment
;; module and class will be used to dynamically load the class
;; all other properties found here and in the credentials file under the class name
;; will be passed to the constructor
module = cassandra_sigv4.auth
classname = SigV4AuthProvider
region_name = us-east-1
```
you can also set region as Environment variable

```
 export AWS_DEFAULT_REGION = us-east-1
```

To connect to Amazon Keyspaces with cqlsh-expansion using Sigv4 authenticator.  
```
cqlsh-expansion cassandra.us-east-1.amazonaws.com 
```

#### Connect with service-specific credentials

You can create service-specific credentials that are similar to the traditional username and password that Cassandra uses for authentication and access management. AWS service-specific credentials are associated with a specific AWS Identity and Access Management (IAM) user and can only be used for the service they were created for. For more information, see [Using IAM with Amazon Keyspaces (for Apache Cassandra)](http://using%20iam%20with%20amazon%20keyspaces%20%28for%20apache%20cassandra%29/) in the IAM User Guide. To connect to Amazon Keyspaces using the cqlsh-expansion and IAM service-specific credentials you can use the command below. In this command we are connecting to us-east-1 region with service specific user *‘Sri-user-99’ *and service specific user password* ‘user-pass-01’. *You will need to replace these credentials with your own user name and password that were given to you when creating the service specific credentials. 


```
[auth_provider]
;; you can specify any auth provider found in your python environment
;; module and class will be used to dynamically load the class
;; all other properties found here and in the credentials file under the class name
;; will be passed to the constructor
module = cassandra.auth
classname = PlainTextAuthProvider
```

```
cqlsh-expansion cassandra.us-east-1.amazonaws.com -u Sri-user-99 -p user-pass-01
```


## Cleanup
To remove the cqlsh-expansion package you can use the pip uninstall api. Additionally, if you executed the post install script ```cqlsh-expansion.init```, you may want to delete the .cassandra directory which contains the cqlshrc file and the ssl certificate. Using pip uninstall will not remove changes made by the post install script. 

```
pip uninstall cqlsh-expansion
```

### New output for TTY

When creating a new cqlsh session with the cqlsh-expansion utility, it will show the default consistency level after establishing a new connection. We find customers using cqlsh may not be aware of the default consistency level of `ONE`, and additional transparency will lead to better operational excellence.

### COPY FROM/TO required Consistency Levels

When executing the `COPY FROM` import operation from the cqlsh-expansion utility, `LOCAL_QUORUM` will be strictly enforced. Executing `COPY FROM` with consistency level other than LOCAL_QUORUM will result in an SyntaxError. This restriction is to provide better experience when using `COPY FROM` with Amazon Keyspaces. Amazon Keyspaces replicates all write operations three times across multiple Availability Zones for durability and high availability. Writes are durably stored before they are acknowledged using the `LOCAL_QUORUM` consistency level.
When executing the `COPY TO` export operation from the cqlsh-expansion utility, consistency of `ONE, LOCAL_ONE, or LOCAL_QUORUM` will be strictly enforced. Executing `COPY FROM` with consistency level other than these three will result in an SyntaxError. This restriction is to provide better experience when using `COPY FROM` with Amazon Keyspaces. 

### Contributing:

```

# Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

# License

This library is licensed under the MIT-0 License. See the LICENSE file.
```

