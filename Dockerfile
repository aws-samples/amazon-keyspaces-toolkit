#Amazon Keyspaces toolkit

ARG CLI_VERSION=latest
FROM amazon/aws-cli:$CLI_VERSION

ENV AWS_KEYSPACES_WORKING_DIR=/root
ENV CASSANDRA_HOME=$AWS_KEYSPACES_WORKING_DIR/cassandra
ENV CQLSHRC_HOME=$AWS_KEYSPACES_WORKING_DIR/.cassandra

WORKDIR $AWS_KEYSPACES_WORKING_DIR

RUN mkdir $AWS_KEYSPACES_WORKING_DIR/bin

#Install jq
RUN yum install -y jq && yum install python3-pip -y && yum clean all

RUN pip3 install importlib-metadata
RUN pip3 install boto3
RUN pip3 install six
RUN pip3 install -i https://test.pypi.org/simple/ cqlsh-expansion-mjpr==0.9.16

RUN cqlsh-expansion.init

#toolkit helpers
COPY bin/aws-cqlsh-expo-backoff.sh $AWS_KEYSPACES_WORKING_DIR/bin/aws-cqlsh-expo-backoff.sh
COPY bin/aws-sm-cqlsh-expo-backoff.sh $AWS_KEYSPACES_WORKING_DIR/bin/aws-sm-cqlsh-expo-backoff.sh
COPY bin/aws-cqlsh-expansion-expo-backoff.sh $AWS_KEYSPACES_WORKING_DIR/bin/aws-cqlsh-expansion-expo-backoff.sh
COPY bin/aws-sm-cqlsh.sh $AWS_KEYSPACES_WORKING_DIR/bin/aws-sm-cqlsh.sh

ENV PATH="${PATH}:$AWS_KEYSPACES_WORKING_DIR/bin"

ENTRYPOINT ["cqlsh-expansion"]