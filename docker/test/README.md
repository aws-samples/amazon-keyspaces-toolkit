
## Running Test
Simple test to execute cqlsh and additional entrypoints provided in the toolkit

`Parameters`

* `$1` SERVICEUSERNAME - Generate Service Specific Credentials user name
* `$2` SERVICEPASSWORD -  Generate Service Specific Credentials password
* `$3` SECRETKEY - AWS Secrets manager key containing service generated Credentials
* `$4` HOST - Amazon Keyspaces endpoint
* `$5` PORT Amazon Keyspaces port 9142

```sh
#!/bin/bash

> docker/test/toolkit-test.sh testuser+1-at-963740746376 gUuus3wDFt9Oli6mLeY7G+arlGdlL/ExampleKey= examplesecret4 cassandra.us-east-1.amazonaws.com 9142


```
