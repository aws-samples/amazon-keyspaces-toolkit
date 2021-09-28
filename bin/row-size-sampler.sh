#!/bin/bash
# The following script will help gather row size estimates for each table in
#   a cluster.
# It will query each table a fixed number of rows at a low query rate not to
#   distrube the cluster.
# It will not persist or log data , credentials, or diagnostic info
# the output will consist of table names and row size estimates.
# By nature of Cassandra data is already randomly stored and distributed
# For most case 20,000 to 50,0000 is enough samples to get accurate results
# By Default, system keyspaces are filtered out. You can add additional
#   keyspaces to filter by adding to the SYSTEMKEYSPACEFILTER string

# The script takes the same parameters as cqlsh to connect to cassandra
# example: ./row-size-sampler.sh cassandra.us-east-1.amazonaws.com 9142 -u "sampleuser" -p "samplepass" --ssl

SYSTEMKEYSPACEFILTER='system\|system_schema\|system_traces\|system_auth\|dse_auth\|dse_security\|dse_leases\|system_distributed\|dse_perf\|dse_system\|OpsCenter\|cfs\|cfs_archive\|dse_leases\|dsefs\|HiveMetaStore\|spark_system'

TABLEFILTER='^-\|^table_name\|(\|)'

keyspaces=$(echo desc keyspaces | ./cqlsh $@  | xargs -n1 echo | grep -v $SYSTEMKEYSPACEFILTER)
for ks in $keyspaces; do
  tables=$(echo "SELECT table_name FROM system_schema.tables WHERE keyspace_name='$ks';" | ./cqlsh $@ | xargs -n1 echo | grep -v $TABLEFILTER)
  for tb in $tables; do
    ./cqlsh $@ -e  "CONSISTENCY LOCAL_ONE; SELECT * FROM \"$ks\".\"$tb\" LIMIT 30000;" | grep -v '\[json\]\|rows)\|-----\|^$' | tr -d ' ' | awk -v keyspace=$ks -v table=$tb -F'|' 'BEGIN {columns=0; numSamples=100000; kilobyte=1024; min = "NaN"; max = -1; lines = 1; }  { if(NR==2){columns=NF;} if(NR>2){thislen=length($0)+107; total+=thislen; squares+=thislen^2;  lines+=1; avg=total/lines;  min = (thislen<min ? thislen : min); max =  (thislen>max ? thislen : max) }} NR==numSamples {exit} END { printf("%s.%s = { lines: %d, columns: %d, average: %d bytes, stdev: %d bytes, min: %d bytes, max: %d bytes}\n", keyspace, table, lines, columns, avg, sqrt(squares/lines - (avg^2)), min, max); }'  >> row-size-estimates.txt 2>&1
  done
done
