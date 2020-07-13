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
    mkdir $CQLSHRC_HOME

#CQLSH SETUP
COPY cassandra/LICENSE.txt $CASSANDRA_HOME
COPY cassandra/bin/cqlsh cassandra/bin/cqlsh.py $CASSANDRA_HOME/bin/
COPY cassandra/pylib/ $CASSANDRA_HOME/pylib/
COPY cassandra/lib/*.zip $CASSANDRA_HOME/lib/

#toolkit helpers
COPY bin/ $AWS_KEYSPACES_WORKING_DIR/bin/

#Setup pem file
ADD https://www.amazontrust.com/repository/AmazonRootCA1.pem $CQLSHRC_HOME/AmazonRootCA1.pem
COPY cqlshrc $CQLSHRC_HOME/cqlshrc

ENV PATH="${PATH}:$AWS_KEYSPACES_WORKING_DIR/bin:$CASSANDRA_HOME/bin"

ENTRYPOINT ["cqlsh"]
