FROM amazon/aws-cli

ENV AWS_KEYSPACES_WORKSHOP=/root
ENV CASSANDRA_HOME=$AWS_KEYSPACES_WORKSHOP/apache-cassandra
ENV CQLSHRC_HOME=$AWS_KEYSPACES_WORKSHOP/.cassandra
ENV AWS_KEYSPACES_WORKSHOP_BIN=$AWS_KEYSPACES_WORKSHOP/bin

#Setup pem file
RUN mkdir $CQLSHRC_HOME
COPY cqlshrc $CQLSHRC_HOME/cqlshrc
ADD https://www.amazontrust.com/repository/AmazonRootCA1.pem $CQLSHRC_HOME/AmazonRootCA1.pem

#Install Helpers
RUN yum install tar -y
RUN yum install gzip -y
RUN yum install jq -y

ADD http://mirror.cc.columbia.edu/pub/software/apache/cassandra/3.11.6/apache-cassandra-3.11.6-bin.tar.gz $AWS_KEYSPACES_WORKSHOP
ADD https://downloads.apache.org/cassandra/3.11.6/apache-cassandra-3.11.6-bin.tar.gz.sha256 $AWS_KEYSPACES_WORKSHOP
RUN sha256sum $AWS_KEYSPACES_WORKSHOP/apache-cassandra-3.11.6-bin.tar.gz
RUN cat $AWS_KEYSPACES_WORKSHOP/apache-cassandra-3.11.6-bin.tar.gz.sha256
RUN rm $AWS_KEYSPACES_WORKSHOP/apache-cassandra-3.11.6-bin.tar.gz.sha256

RUN mkdir $CASSANDRA_HOME
RUN tar -xf $AWS_KEYSPACES_WORKSHOP/apache-cassandra-3.11.6-bin.tar.gz --directory $CASSANDRA_HOME --strip-components=1
RUN rm $AWS_KEYSPACES_WORKSHOP/apache-cassandra-3.11.6-bin.tar.gz
ENV PATH="${PATH}:$CASSANDRA_HOME/bin"

RUN mkdir $AWS_KEYSPACES_WORKSHOP_BIN
COPY bin/aws-sm-cqlsh.sh $AWS_KEYSPACES_WORKSHOP_BIN
COPY bin/aws-sm-cqlsh-expo-backoff.sh $AWS_KEYSPACES_WORKSHOP_BIN
COPY bin/aws-cqlsh-expo-backoff.sh $AWS_KEYSPACES_WORKSHOP_BIN

ENV PATH="${PATH}:$AWS_KEYSPACES_WORKSHOP_BIN"

WORKDIR $AWS_KEYSPACES_WORKSHOP

ENTRYPOINT ["cqlsh"]
