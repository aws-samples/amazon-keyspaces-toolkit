# CQLSH Docker container optimized for Amazon Keyspaces (for Apache Cassandra)

A docker container for Cassandra Query Language Shell (CQLSH) to help you use CQLSH with Amazon Keyspaces for functional testing, light operations, and data migration. This container includes configuration settings optimized for Amazon Keyspaces, but it will also work with Self-Managed Apache Cassandra clusters.

## Amazon Keyspaces (for Apache Cassandra)
[Amazon Keyspaces (for Apache Cassandra)] (https://aws.amazon.com/keyspaces/) is a scalable, highly available, and managed Apache Cassandra–compatible database service. Amazon Keyspaces is serverless, so you pay for only the resources you use and the service can automatically scale tables up and down in response to application traffic.

## What's included
This container extends from [awscli container](https://aws.amazon.com/blogs/developer/aws-cli-v2-docker-image/) and includes the following Cassandra components.
* 3.11.6 Apache Cassandra distribution with CQLSH
* Amazon Web Services pem file for SSL connectivity
* CQLSHRC file with best practices
* Helpers to perform secure login with [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
* AWS CLI

### Architecture
![Figure 1-1](content/static/keyspaces-toolkit-architecture.png "Architecture")

* CQLSHRC file is located at root directory of this project
* Toolkit scripts located in /bin directory of this project
* Keyspaces PEM file is downloaded when creating the container


# TLDR;
The following steps to connect to Amazon Keyspaces using the Toolkit; Clone. Build. Connect. Go!

```sh
  git clone https://github.com/aws-samples/amazon-keyspaces-toolkit .

  docker build --tag aws/keyspaces-cqlsh .

  docker run --rm -ti aws/keyspaces-cqlsh \
   cassandra.us-east-1.amazonaws.com 9142 \
   -u "SERVICEUSERNAME" -p "SERVICEPASSWORD" --ssl

   #Voila! You are now connected.
```
# Detailed Steps and Advanced Examples

## Prerequisites

#### Generate Service Specific Credentials
Service-specific credentials enable IAM users to access a specific AWS service. The credentials cannot be used to access other AWS services. They are associated with a specific IAM user and cannot be used by other IAM users.

* IAM user [Generated service-specific credentials](https://docs.aws.amazon.com/keyspaces/latest/devguide/programmatic.credentials.html) for Amazon Keyspaces

```sh
aws iam create-service-specific-credential \
    --user-name alice \
    --service-name cassandra.amazonaws.com
```

_*Example Output*_

```json
{
    "ServiceSpecificCredential": {
        "CreateDate": "2019-10-09T16:12:04Z",
        "ServiceName": "cassandra.amazonaws.com",
        "ServiceUserName": "alice-at-111122223333",
        "ServicePassword": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "ServiceSpecificCredentialId": "ACCAYFI33SINPGJEBYESF",
        "UserName": "alice",
        "Status": "Active"
    }
}
```

#### Store Generated User Credentials in Amazon Secrets Manager (Optional)
AWS Secrets Manager helps you protect secrets needed to access your applications, services, and IT resources. The service enables you to easily rotate, manage, and retrieve database credentials, API keys, and other secrets throughout their lifecycle. Replace `SERVICEUSERNAME` and `SERVICEPASSWORD` with the generated values.

```sh
aws secretsmanager create-secret --name keyspaces-credentials \
--description "Store Amazon Keyspaces Generated Service Credentials" \
--secret-string "{\"username\":\"SERVICEUSERNAME\", \"password\":\"SERVICEPASSWORD\"}"
```

## Setup Docker

Containers add a level of platform independence allowing for installation on various operating systems including Linux, Mac, and Windows. Find your operating system below, and follow the installation process. After installing, you will have access to the docker terminal from the command line terminal.

* Windows: [Visit Windows Download and Tutorial](https://docs.docker.com/docker-for-windows/install/)
* Mac: [Visit Mac Download and Tutorial](https://docs.docker.com/docker-for-mac/install/)
* Linux: [Visit Linux Download and Tutorial](https://docs.docker.com/engine/install/)


## Build Image From Docker file

To start a container, you will need to build the docker image first. The repository is open source and open to customization.  [https://github.com/aws-samples/amazon-keyspaces-toolkit](https://github.com/aws-samples/amazon-keyspaces-toolkit)

`Parameters`

* `--tag`  - is used to give the image a name and version. The tag name provided will be used later when creating the container from the image
* `.`   -  sets the location of the Dockerfile as the current working directory

```sh
  git clone https://github.com/aws-samples/amazon-keyspaces-toolkit

  cd amazon-keyspaces-toolkit

  docker build --tag aws/keyspaces-cqlsh .
```

## Create and Run Container

After building the image we can then run the container. For more options see Docker's [run command reference](https://docs.docker.com/engine/reference/commandline/run)

`Parameters`

* `--rm` - removes the container after ending the CQLSH session
* `-ti`  - interactive bash shell in the container

```sh
docker run --rm -ti aws/keyspaces-cqlsh \
 cassandra.us-east-1.amazonaws.com 9142 \
 -u "SERVICEUSERNAME" -p "SERVICEPASSWORD" --ssl
```

_*Replace SERVICEUSERNAME and SERVICEPASSWORD with [Generated service-specific credentials](https://docs.aws.amazon.com/keyspaces/latest/devguide/programmatic.credentials.html)*_

## Executing statements

We can also use this container to execute commands using the --execute parameter. For a list of CQLSH commands see the following resource: [List of CQLSH commands](https://cassandra.apache.org/doc/latest/tools/cqlsh.html). This will allow you to embed this functionality in existing scripts.

  ```sh
  docker run --rm -ti aws/keyspaces-cqlsh \
  cassandra.us-east-1.amazonaws.com 9142 \
  -u "SERVICEUSERNAME" -p "SERVICEPASSWORD" --ssl \
  --execute "CREATE KEYSPACE \"aws\" WITH
	REPLICATION = {'class': 'SingleRegionStrategy'}"
  ```

## Using AWS Secrets Manager Wrapper
When using [Generated service-specific credentials](https://docs.aws.amazon.com/keyspaces/latest/devguide/programmatic.credentials.html) it is common practice to store the username and password in [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/). This allows you to use the AWS CLI to retrieve the credentials and not expose the credentials in plain text. The following script will use the AWS CLI config profile to grab stored service credentials from AWS Secrets Manager.

_*Requires AWS CLI to be installed and configured on local host or setup within container*_

`Parameters`

* `--rm` - removes the container after ending the CQLSH session
* `-ti`  - interactive bash shell in the container
* `-v` - mount a volume from existing directory
  * ~/.aws:/root/.aws in the example is the location of the host awscli configuration on _*localhost:container*_
* `--entrypoint` - choses a wrapper script for CQLSH with the username and password extracted from AWS Secrets Manager.

`aws-sm-cqlsh.sh Parameters`
* First parameter will be the AWS Secrets Manager key we created in the Prerequisites step. Every parameter following the secrets key will be passed into CQLSH command

_*Example: open cqlsh shell*_
```sh
docker run --rm -ti \
-v ~/.aws:/root/.aws \
--entrypoint aws-sm-cqlsh.sh \
 aws/keyspaces-cqlsh keyspaces-credentials \
 cassandra.us-east-1.amazonaws.com 9142 --ssl
```
_*Example: execute statement*_
```sh
docker run --rm -ti \
-v ~/.aws:/root/.aws \
--entrypoint aws-sm-cqlsh.sh  \
 aws/keyspaces-cqlsh keyspaces-credentials \
 cassandra.us-east-1.amazonaws.com 9142 --ssl \
 --execute "CREATE TABLE aws.workshop(
	id text,
	time timeuuid,
	event blob,
	PRIMARY KEY(id, time))
  WITH CUSTOM_PROPERTIES = {'capacity_mode':{'throughput_mode':'PAY_PER_REQUEST'}}"

```

## Exponential Backoff
Keyspace and table creation are Asynchronous in Amazon Keyspaces. This asynchronous functionality is different than Apache Cassandra where table creation is synchronous. We have been told by customers that some existing scripts require synchronous behavior when creating a table. A common solution is to add an exponential backoff describe statement to notify users when the table is created. This container contains an exponential backoff helper that will attempt multiple times until the CQL statement succeeds. Other options include building a CloudFormation template.

`Parameters`
* $1 maximum time for program to run in seconds
* $2 maximum number of attempts to run
* $3 CQL Statement to run

```sh
#!/bin/bash

#create a table
docker run -ti --name createtablec aws/keyspaces-cqlsh \
cassandra.us-east-1.amazonaws.com 9142 \
-u "SERVICEUSERNAME" -p "SERVICEPASSWORD" --ssl \
--execute "CREATE TABLE aws.workshop_backofftest(
 id text,
 time timeuuid,
 event blob,
 PRIMARY KEY(id, time))
 WITH CUSTOM_PROPERTIES = {'capacity_mode':{'throughput_mode':'PAY_PER_REQUEST'}}"

# Check the error code of container. Make sure to drop the --rm statement from the previous run command. You can always rm after.
docker inspect createtablec --format='{{.State.ExitCode}}'

docker rm createtablec

#exponential backoff describe
docker run --rm -ti --entrypoint aws-cqlsh-expo-backoff.sh aws/keyspaces-cqlsh \
 10 360 \
 cassandra.us-east-1.amazonaws.com 9142 \
 --ssl -u "SERVICEUSERNAME" -p "SERVICEPASSWORD" \
 --execute "DESCRIBE TABLE aws.workshop_backofftest"
```

## Performing multiple statements
When performing multiple calls it may be beneficial to perform the AWS Secrets Manager calls from outside of the container and pass the username and password into each containerized CQLSH statement.

```sh
#!/bin/bash
mysecret=$(aws secretsmanager get-secret-value --secret-id "keyspaces-credentials" --query SecretString --output text)

username=$(jq --raw-output '.username' <<< $mysecret)
password=$(jq --raw-output '.password' <<< $mysecret)

docker run --rm -it aws-keyspaces-ws \
 cassandra.us-east-1.amazonaws.com 9142\
 --execute "DESCRIBE KEYSPACE aws" \
 -u $username -p $password --ssl


 docker run --rm -it aws-keyspaces-ws \
  cassandra.us-east-1.amazonaws.com 9142\
  --execute "DESCRIBE TABLE aws.workshop" \
  -u $username -p $password --ssl
```

## Connect to Apache Cassandra
To connection to Apache Cassandra override the parameters or provide location of a different cqlshrc file. The following shows how to mount a local directory to docker and configure the container to use a cqlshrc file to configure the connection to an Apache Cassandra cluster.

To Change SSL Options you can
* Override paramters in the command line
* Override CQLSHRC location with the `--cqlshrc` paramter

```sh
docker run --rm -ti \
  -v ~/.aws:/root/.aws \
  -v ~/.cassandra/cqlsh:/root/.local-cassandra/cqlsh \
  aws/keyspaces-cqlsh \
  SelfManagedCassandraHost 9042 -u "cassandra" -p "cassandra" \
   --cqlshrc '/root/.local-cassandra/cqlsh/cqlshrc' \
   --execute "DESCRIBE TABLE aws.workshop"
```


## Copy Data From Apache Cassandra
You can export data from Cassandra clusters by using the CQLSH COPY command. You can export the data to a mounted directory. In this example we use a folder called datadump on the localhost to store the export.

* `COPY` table to copy from
* `TO` the directory to load to. Since we will remove the container after running the process, we will save the export to a mounted directory 'datadump'.
* `MAXOUTPUTSIZE` number of lines to export in single file. You can break your data into smaller files to make it easier to load the data into Keyspaces or a different cluster later.  
* `HEADER` leave header out since we want to explicitly map columns
* `DELIMITER` choose a different delimiter than ',' since it is used in other types such as maps, lists, and sets

```sh
docker run --rm -ti \
  -v ~/.aws:/root/.aws \
  -v ~/.cassandra/cqlsh:/root/.local-cassandra/cqlsh \
  -v ~/datadump:/root/datadump \
  aws/keyspaces-cqlsh \
  SelfManagedCassandraHost 9042 -u "cassandra" -p "cassandra" \
   --cqlshrc '/root/.local-cassandra/cqlsh/cqlshrc' \
   --execute "CONSISTENCY LOCAL_ONE;
         COPY aws.workshop (id,time,event)
         TO '/root/datadump/export.csv'
         WITH HEADER=false AND MAXOUTPUTSIZE=5000000 AND DELIMITER='|'"
```

## Copy Data To Amazon Keyspaces
We can now copy this data to Amazon Keyspaces by using the COPY FROM command and specifying the mounted directory used in the export process. For best practices on loading data, see [Loading Data into Amazon Keyspaces with cqlsh](https://aws.amazon.com/blogs/database/loading-data-into-amazon-mcs-with-cqlsh/).


#### Shuffle Data for even distribution
From the blog we learned that exporting existing data from Cassandra will result in an ordered dataset. Before loading the data to Amazon Keyspaces, it’s recommended to shuffle the data in the CSV to improve the import performance by distributing the load across data partitions. The following script will shuffle the lines in all files within a directory starting with 'export.csv'.

```sh
#!/bin/bash

# For every file in directory perform shuffle and add new file to a directory containing only shuffled data.
for filename in export.csv*; do
   shuf "$filename" -o "shuffled/$filename.shuffled"
done
```

#### Load to Amazon Keyspaces
* `COPY` table to copy from
* `FROM` the directory/file to load from. We use the same directory of newly shuffled data 'datadump/shuffled'.
* `HEADER` leave header out since we want to explicitly map columns
* `DELIMITER` choose a different delimiter than ',' since it is used in other types such as maps, lists, and sets
--cqlshrc '/root/.local-cassandra/cqlsh/cqlshrc' \
```sh
docker run --rm -ti \
  -v ~/.aws:/root/.aws \
  -v ~/.cassandra/cqlsh:/root/.local-cassandra/cqlsh \
  -v ~/datadump:/root/datadump \
  aws/keyspaces-cqlsh \
  cassandra.us-east-1.amazonaws.com 9142 -u "SERVICEUSERNAME" -p "SERVICEPASSWORD" --ssl \
   --execute "CONSISTENCY LOCAL_QUORUM;
         COPY aws.workshop (id,time,event)
         FROM '/root/datadump/shuffled/*'
         WITH HEADER=false AND DELIMITER='|'"
```

### Cheatsheet

```text
--- Docker ---
#Logs
$> docker logs aws/keyspaces-cqlsh

#Remove Image
$> docker rmi aws/keyspaces-cqlsh

#exit code
docker inspect createtablec --format='{{.State.ExitCode}}'

--- CQL ---
#Describe keyspace
DESCRIBE KEYSPACE keyspace_name;

#Select Samples
SELECT * FROM keyspace_name.table_name LIMIT 10;

--- Serverless ---
#Change Provisioned Capacity
ALTER TABLE aws.workshop WITH custom_properties={'capacity_mode':{'throughput_mode': 'PROVISIONED', 'read_capacity_units': 4000, 'write_capacity_units': 3000}} ;

#Describe current capacity mode
SELECT keyspace_name, table_name, custom_properties FROM system_schema_mcs.tables where keyspace_name = 'aws_cassandra_ws';

--- Linux ---
#Line count of multiple/all files in the current directory
find . -type f | wc -l

#Remove header from csv
sed -i '1d' myData.csv
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
