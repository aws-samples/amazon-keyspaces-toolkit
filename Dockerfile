#Amazon Keyspaces toolkit

ARG CLI_VERSION=latest
FROM amazon/aws-cli:$CLI_VERSION

ENV AWS_KEYSPACES_WORKING_DIR=/root
ENV CASSANDRA_HOME=$AWS_KEYSPACES_WORKING_DIR/cassandra
ENV CQLSHRC_HOME=$AWS_KEYSPACES_WORKING_DIR/.cassandra

WORKDIR $AWS_KEYSPACES_WORKING_DIR

#Install jq
RUN yum install -y jq && yum clean all

#setup directory structure
RUN mkdir $CASSANDRA_HOME && \
    mkdir $CASSANDRA_HOME/bin  && \
    mkdir $CASSANDRA_HOME/lib  && \
    mkdir $CASSANDRA_HOME/pylib  && \
    mkdir $CASSANDRA_HOME/pylib/cqlshlib  && \
    mkdir $AWS_KEYSPACES_WORKING_DIR/bin && \
    mkdir $AWS_KEYSPACES_WORKING_DIR/distro && \
    mkdir $CQLSHRC_HOME

#CQLSH SETUP
COPY cqlsh-expansion/LICENSE.txt $CASSANDRA_HOME
COPY cqlsh-expansion/bin/cqlsh cqlsh-expansion/bin/cqlsh.py $CASSANDRA_HOME/bin/
COPY cqlsh-expansion/pylib/ $CASSANDRA_HOME/pylib/
COPY cqlsh-lib/cassandra-driver*.zip $CASSANDRA_HOME/lib/
COPY cqlsh-lib/futures-*.zip $CASSANDRA_HOME/lib/

#ThirdParty License directory
COPY THIRD-PARTY-LICENSES.txt $AWS_KEYSPACES_WORKING_DIR/distro/

#toolkit helpers
COPY bin/aws-cqlsh-expo-backoff.sh $AWS_KEYSPACES_WORKING_DIR/bin/aws-cqlsh-expo-backoff.sh
COPY bin/aws-sm-cqlsh-expo-backoff.sh $AWS_KEYSPACES_WORKING_DIR/bin/aws-sm-cqlsh-expo-backoff.sh
COPY bin/aws-cqlsh-expansion-expo-backoff.sh $AWS_KEYSPACES_WORKING_DIR/bin/aws-cqlsh-expansion-expo-backoff.sh
COPY bin/aws-sm-cqlsh.sh $AWS_KEYSPACES_WORKING_DIR/bin/aws-sm-cqlsh.sh

COPY cqlsh-expansion/bin/cqlsh-expansion $CASSANDRA_HOME/bin/cqlsh-expansion
COPY cqlsh-expansion/bin/cqlsh-expansion.py $CASSANDRA_HOME/bin/cqlsh-expansion.py

COPY cqlsh-lib/boto3-1.16.52-py2.py3-none-any.zip $CASSANDRA_HOME/lib/
COPY cqlsh-lib/botocore-1.19.54-py2.py3-none-any.zip $CASSANDRA_HOME/lib/
COPY cqlsh-lib/cassandra_sigv4-4.0.2-py2.py3-none-any.zip $CASSANDRA_HOME/lib/
COPY cqlsh-lib/six-1.15.0-py2.py3-none-any.zip $CASSANDRA_HOME/lib/
COPY cqlsh-lib/python_dateutil-2.8.1-py2.py3-none-any.zip $CASSANDRA_HOME/lib/
COPY cqlsh-lib/urllib3-1.26.2-py2.py3-none-any.zip $CASSANDRA_HOME/lib/
COPY cqlsh-lib/jmespath-0.10.0-py2.py3-none-any.zip $CASSANDRA_HOME/lib/

#Setup pem file
COPY cqlsh-expansion/config/sf-class2-root.crt $CQLSHRC_HOME/sf-class2-root.crt
COPY cqlsh-expansion/config/cqlshrc $CQLSHRC_HOME/cqlshrc


ENV PATH="${PATH}:$AWS_KEYSPACES_WORKING_DIR/bin:$CASSANDRA_HOME/bin"

ENTRYPOINT ["cqlsh"]
