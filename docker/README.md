# Amazon Keyspaces (for Apache Cassandra) developer toolkit
This repository contains Cassandra Query Language Shell (CQLSH) and common Cassandra developer tooling preconfigured for Amazon Keyspaces. The toolkit is based on open-source Apache Cassandra tooling, but is optimized for Amazon Keyspaces and Amazon Web Services.
Amazon Keyspaces (for Apache Cassandra) is a scalable, highly available, and managed Apache Cassandra–compatible database service. You don’t have to provision, patch, or manage servers, and you don’t have to install, maintain, or operate software. Amazon Keyspaces is serverless, so you pay for only the resources you use and the service can automatically scale tables up and down in response to application traffic.

The toolkit contains the cqlsh-expansion utility. The cqlsh-expansion supports the Amazon Keyspaces Sigv4 Authentication plugin. The SigV4AuthProvider plugin enables IAM users, roles, and federated identities to add authentication information to Amazon Keyspaces API requests using the AWS Signature Version 4 Process (SigV4).

# What's included
This docker image extends the official [AWS CLI version 2 Docker image](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-docker.html) allowing users to access cqlsh or the AWS CLI from the same container. Since Amazon Keyspaces requires SSL communication by default, the container also includes the Amazon Web Services Starfield digital certificate file and preconfigured cqlshrc file to get started quickly. Included are helpers collected from working with customers in the field to help with common administrative task like creating a table or capturing the average row size. For more on whats included and the source code visit the [amazon-keyspaces-toolkit github repository](https://github.com/aws-samples/amazon-keyspaces-toolkit).

# Docker CLI usage
## Tags
There are two sets of supported tags:

**Latest** - This corresponds to the latest released version of the Amazon Keyspaces toolkit.

**<major.minor.patch>** - This corresponds to each released version of the Amazon Keyspaces toolkit. For example, to use version 0.7.8 of the toolkit, use the tag 0.7.8. These tags are immutable and pushed once upon release of a particular version of the toolkit. These versions will also have a fixed version of the AWS CLI base image.
The Amazon Keyspaces toolkit can be executed from the Docker CLI with the following docker run command: The ```-ti```  flag will provide an interactive session, the ```--rm```  will remove the container after execution, and the ```--version``` flag is a cqlsh parameter that will print the version of the cqlsh process..

```
docker run -ti --rm amazon/amazon-keyspaces-toolkit –-version
```

This command will print out the version of the cqlsh script executed in the container. Note that the cqlsh-expansion executable was not specified in the docker run command. This is because the entrypoint for the image is defined as the cqlsh-expansion executable. All parameters passed after the image will be passed to the cqlsh-expansion executable running in the container.  For a list of cqlsh commands see the [Apache Cassandra cqlsh documentation](https://cassandra.apache.org/doc/latest/cassandra/tools/cqlsh.html) or by executing the ```--help``` command.

```
docker run -ti --rm amazon/amazon-keyspaces-toolkit –-help
```

# Support for Multiple Authentication models
The Amazon Keyspaces toolkit include the cqlsh-expansion script which extends the legacy cqlsh script to improve integration AWS IAM. You can access Amazon Keyspaces through IAM user or IAM roles. To authenticate using IAM roles you will want to use the custom authentication provider “SigV4AuthProvider”. For service specific credentials for IAM user, you will want to use the legacy “PlainTextAuthProvider” for user name and password.

## Custom Authentication Provider
The cqlsh-expansion has an additional flag --auth-provider that allows for additional authentication providers. The cqlsh-expansion comes with SigV4AuthProvider for Amazon Keyspaces. The SigV4AuthProvider plugin enables IAM users, roles, and federated identities to add authentication information to Amazon Keyspaces API requests using the AWS Signature Version 4 Process (SigV4). To access the aws credentials for the container host you can mount the ```.aws``` directory using the ```-v``` docker mount command.

```
docker run -ti --rm -v ~/.aws:/root/.aws amazon/keyspaces-toolkit cassandra.us-east-1.amazonaws.com --ssl --auth-provider "SigV4AuthProvider"
```

## PlainTextAuthProvider
PlainTextAuthProvider is the default authentication provider in cqlsh. This provider implements a Simple Authentication and Security Layer (SASL) requiring the user to provide a username and password on connection. You can use the PlainTextAuthProvider with Amazon Keyspaces by creating Identity Access Management (IAM) service-specific credentials. Service-specific credentials is specific to Amazon Keyspaces and enable IAM users to access the service. The credentials cannot be used to access other AWS services. They are associated with a specific IAM user and cannot be used by other IAM users. To learn more about service specific credentials and how to create them see the following documentation [Generate Service Specific Credentials](https://docs.aws.amazon.com/keyspaces/latest/devguide/programmatic.credentials.ssc.html).

```
docker run --rm -ti amazon/keyspaces-toolkit cassandra.us-east-1.amazonaws.com 9142 -u "SERVICEUSERNAME" -p "SERVICEPASSWORD" --ssl
```

# Drop-in replacement for cqlsh
Now, simplify the setup by assigning an alias (or DOSKEY for Windows) to the Docker command. The alias acts as a shortcut, enabling you to use the alias keyword instead of typing the entire command. You will use cqlsh as the alias keyword so that you can use the alias as a drop-in replacement for your existing Cassandra scripts.

The alias contains the parameter ```–v "$(pwd)":/source```, which mounts the current directory of the host allowing access to local files. This is useful for importing and exporting data with COPY or using the cqlsh ```--file``` command to load external cqlsh scripts.

```
alias cqlsh='docker run --rm -ti -v ~/.aws:/root/.aws -v "$(pwd)":/source amazon/keyspaces-toolkit cassandra.us-east-1.amazonaws.com 9142 --ssl --auth-provider "SigV4AuthProvider"
```

Now run the alias command by calling the alias name. The cqlsh alias will spin up a new container with the cqlsh-expansion process. You can pass standard cqlsh commands or start an interactive session. The command below will execute the version command returning the cqlsh version without having to specify the docker commands each time.  

```
cqlsh --version
```

Visit the [Amazon Keyspaces toolkit github repository](https://github.com/aws-samples/amazon-keyspaces-toolkit) for more examples, tooling, and best practices.
