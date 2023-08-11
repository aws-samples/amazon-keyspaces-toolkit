#!/bin/bash
shopt -s expand_aliases
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

# check if the cqlsh-expansion is installed, then if cqlsh installed, then check local file
if [ -x "$(command -v cqlsh-expansion)" ]; then
  echo 'using installed cqlsh-expansion'
  alias kqlsh='cqlsh-expansion'
elif [ -x "$(command -v cqlsh)" ]; then
  echo 'using installed cqlsh'
  alias kqlsh='cqlsh'
elif [ -e cqlsh ]; then
  echo 'using local cqlsh'
  alias kqlsh='./cqlsh'
else
  echo 'cqlsh not found' 
  exit 1
fi

echo 'starting...'

SYSTEMKEYSPACEFILTER='system\|system_schema\|system_traces\|system_auth\|dse_auth\|dse_security\|dse_leases\|system_distributed\|dse_perf\|dse_system\|OpsCenter\|cfs\|cfs_archive\|dse_leases\|dsefs\|HiveMetaStore\|spark_system'

TABLEFILTER='^-\|^table_name\|(\|)'

keyspaces=$(echo desc keyspaces | kqlsh $@  | xargs -n1 echo | grep -v $SYSTEMKEYSPACEFILTER)
for ks in $keyspaces; do
  tables=$(echo "SELECT table_name FROM system_schema.tables WHERE keyspace_name='$ks';" | kqlsh $@ | xargs -n1 echo | grep -v $TABLEFILTER)
  for tb in $tables; do
    kqlsh $@ -e  "CONSISTENCY LOCAL_ONE; PAGING 100; SELECT * FROM \"$ks\".\"$tb\" LIMIT 30000;" | grep -v '\[json\]\|rows)\|-----\|^$' | tr -d ' ' | awk -v keyspace=$ks -v table=$tb -F'|' 'BEGIN {columns=0; numSamples=30000; kilobyte=1024; min = "NaN"; max = -1; lines = 1; }  { if(NR==2){columns=NF;} if(NR>2){thislen=length($0)+107; total+=thislen; squares+=thislen^2;  lines+=1; avg=total/lines;  min = (thislen<min ? thislen : min); max =  (thislen>max ? thislen : max) }} NR==numSamples {exit} END { printf("%s.%s = { lines: %d, columns: %d, average: %d bytes, stdev: %d bytes, min: %d bytes, max: %d bytes}\n", keyspace, table, lines, columns, avg, sqrt(squares/lines - (avg^2)), min, max); }'
    kqlsh $@ -e  "DESCRIBE \"$ks\".\"$tb\";" | grep -i blob | while read line; do printf "\t...\"$ks\".\"$tb\" contains a BLOB type, if the majority of row size is from the BLOB, then divide the estimate in half" ; done
  done
done
