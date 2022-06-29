'''The following script will simulate Truncate table in a region for the Amazon Keyspaces service. 
 This is achieved by dropping the existing table by executing the DROP command. The DROP command itself is asynchronous and success is only a service side
 confirmation of the request, but not confirmation that resources have been removed. When the table no longer appears
 in the system.schema_mcs table is it considered fully removed. Once the table is dropped script will recreate table with existing custom properties. The CREATE command itself is asynchronous and success is only a service side
 confirmation of the request, but not confirmation that resources have been Creates. When the table Status appears as 'ACTIVE' in the system.schema_mcs table is considered ready for Usage. Prior to table being dropped and recreated the schema of the table is backed to ~/.cassandra/truncate log 

 Currently the script will wait for 15 + 15  mins for table deletion/ creation to be complete, In case of exceptions or duration excedeed script will fail

 Usage - The inputs for the script are keyspace name, table name , and region respectively , for private endpoints need to manually change the endpoint variable in the script 

## Prerequisites cqlsh-expansion (download required libraries for script execution like cassandra-driver, sigv4 etc)
To install Refer to https://pypi.org/project/cqlsh-expansion/

##
 Execution Sample commands: python toolkit-truncate --table aws.test --host cassandra.us-east-1.amazonaws.com --ssl --auth-provider "SigV4AuthProvider"
                            python toolkit-truncate --table  "aws.test" --host "cassandra.us-east-1.amazonaws.com"  -u "sri" -p "Rangisetti" --ssl --auth-provider "PlainTextAuthProvider"
                            python toolkit-truncate --table  aws.test --host cassandra.us-east-1.amazonaws.com --ssl --sigv4

@author Sri Rathan Rangisetti
@author Michael Raney
'''
import boto3, time, sys
import getpass
import optparse
import os
import sys
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.query import dict_factory
from cassandra.metadata import KeyspaceMetadata, TableMetadata
from ssl import SSLContext, PROTOCOL_TLSv1_2, CERT_REQUIRED
from cassandra_sigv4.auth import *
from cassandra.auth import PlainTextAuthProvider
import logging

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 9142
DEFAULT_SSL = False
DEFAULT_SIGV4 = False
DEFAULT_CONNECT_TIMEOUT_SECONDS = 5
DEFAULT_REQUEST_TIMEOUT_SECONDS = 10
DEFAULT_AUTH_PROVIDER = 'PlainTextAuthProvider'

parser = optparse.OptionParser(description='Truncate the table')
parser.add_option('--table',  help='keyspace.table name')
parser.add_option('--host', help='Amazon Keyspaces endpoint')
parser.add_option("--sigv4", action='store_true', help='Use SigV4AuthProvider plugin for autentication and authorization', default=DEFAULT_SIGV4)
parser.add_option("--auth-provider", help="The AuthProvider to use when connecting. Default is PlainTextAuthProvider", dest='auth_provider_name', default=DEFAULT_AUTH_PROVIDER)
parser.add_option("-u", "--username", help="Authenticate as user.")
parser.add_option("-p", "--password", help="Authenticate using password.")
parser.add_option('--ssl', action='store_true', help='Use SSL', default=False)

optvalues = optparse.Values()
(options, arguments) = parser.parse_args(sys.argv[1:], values=optvalues)
endpoint = str(options.host).replace("'", '')
ks = str((options.table).split('.')[0]).replace("'", '')
tb = str((options.table).split('.')[1]).replace("'", '')

if hasattr(options, 'username'):
   username = str(options.username)

if hasattr(options, 'password'):   
   password = str(options.password)

user = getpass.getuser()
user_dir = os.path.expanduser('~'+user)
config_dir = os.path.join( user_dir, '.cassandra')
cert_dir = os.path.join(config_dir, 'sf-class2-root.crt')
truncate_log = os.path.join(config_dir, 'truncate')

#now we will Create and configure logger 
logging.basicConfig(filename=truncate_log, 
					format='%(asctime)s %(message)s', 
					filemode='a') 
#Let us Create an object 
logger=logging.getLogger() 

#Now we are going to Set the threshold of logger to INFO 
logger.setLevel(logging.INFO) 

ssl_context = SSLContext(PROTOCOL_TLSv1_2)
ssl_context.load_verify_locations(cert_dir) # change the location to access the cert file
ssl_context.verify_mode = CERT_REQUIRED

'''
The following connection example uses the SigV4Athentication plugin for the datastax python driver. 
This allows you to use user roles and service roles to delegate authentication and authorization to 
Amazon Keyspaces resources and actions.  
Documentation for the sigv4connection can be found here: 
 https://docs.aws.amazon.com/keyspaces/latest/devguide/using_python_driver.html
 Github example can be found here: https://github.com/aws/aws-sigv4-auth-cassandra-python-driver-plugin
'''
## Credntial Configuration https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
## https://docs.aws.amazon.com/keyspaces/latest/devguide/programmatic.endpoints.html 

if hasattr(options, 'sigv4'):
    my_session = boto3.session.Session()
    auth_provider = SigV4AuthProvider(my_session)
elif hasattr(options, 'auth_provider_name'):
    if options.auth_provider_name == 'SigV4AuthProvider':
            my_session = boto3.session.Session()
            auth_provider = SigV4AuthProvider(my_session)
    elif options.auth_provider_name == DEFAULT_AUTH_PROVIDER:
        if username:
            if not hasattr(options, 'password'):
              password = getpass.getpass()
              auth_provider = PlainTextAuthProvider(username=username, password=password)
            else:
              auth_provider = PlainTextAuthProvider(username=username, password=password)
    else:
        raise SyntaxError('cqlsh-expansion.py Invalid parameter for auth-provider. "%s" is not a valid AuthProvider' % (auth_provider,))
else:
    if username:
        if not hasattr(options, 'password'):
            password = getpass.getpass()
            auth_provider = PlainTextAuthProvider(username=username, password=password)
        else:
            auth_provider = PlainTextAuthProvider(username=username, password=password)

profile = ExecutionProfile(request_timeout= None, row_factory=dict_factory)

cluster = Cluster( [endpoint], ssl_context=ssl_context, auth_provider=auth_provider,
                  port=9142, execution_profiles={EXEC_PROFILE_DEFAULT: profile})
session = cluster.connect()

# Retrieves the schema of the table 
pk= {} # To store partition keys of the tables
cl ={} # To store clustering columns of the tables
cl_order ={}  # To store clustering order of the tables
columns= session.execute(("select column_name, type, kind, position, clustering_order from system_schema.columns WHERE keyspace_name = %s AND table_name = %s"), (ks,tb))
# Verifying if table exists or not
if columns.one() is  None:
    sys.exit("No such table exists to truncate")

# Recreating table schema
schema_tbl = 'CREATE TABLE ' + ks + '.' + tb + ' ('

for item in columns:
    schema_tbl += item['column_name'] +' '+ item['type']
    if item['kind'] == 'partition_key':
        pk[item['position']]= item['column_name']
    elif item['kind'] == 'clustering':
        cl[item['position']]= item['column_name']
        cl_order [item['column_name']] = item['clustering_order']
    elif item['kind'] == 'static':
        schema_tbl += ' '+ item['kind']
    schema_tbl = schema_tbl + ', '

def looper(schema_str, keys):
    for i in sorted(keys):
       schema_str += str(keys[i]) +',' 
    return schema_str

schema_cl_keys=''
schema_pk_keys = 'PRIMARY KEY (( '
schema_pk_keys = looper(schema_pk_keys, pk)
sch_par_keys = schema_pk_keys.rstrip(schema_pk_keys[-1])
schema_cl_order=''

if any(cl):
    schema_cl_keys = looper(schema_cl_keys, cl)   
    schema_cl_keys = ', ' + schema_cl_keys.rstrip(schema_cl_keys[-1])
    schema_cl_order = ' WITH CLUSTERING ORDER BY ('
    for i in cl_order:
       schema_cl_order +=  str(i) + ' ' + str(cl_order[i]) + ' ,'
    schema_cl_order = schema_cl_order.rstrip(schema_cl_order[-1]) + ')'
recreate_table = schema_tbl + sch_par_keys + ')' + schema_cl_keys + '))' + schema_cl_order 
if any(cl):
    recreate_table += ' AND'
else: 
    recreate_table += ' with'

# Removes the unicode(u) after converting to string 
def unicode_fixer(obj):
    return str(obj).replace("u'", "'")

# Retrieves the properties of the table such as TTL, Comments, Provisioning, Encryption 
cust_set = session.execute(("select custom_properties from system_schema_mcs.tables WHERE keyspace_name = %s AND table_name = %s"), (ks,tb)).one()
prop_set = session.execute(("select comment, default_time_to_live from system_schema_mcs.tables WHERE keyspace_name = %s AND table_name = %s"), (ks,tb)).one()

if prop_set['comment']:
 ttl_comm = ' default_time_to_live = ' + unicode_fixer(prop_set['default_time_to_live']) + ' AND comment = ' + '\'' + unicode_fixer(prop_set['comment']) + '\'' 
else:
  ttl_comm = ' default_time_to_live = ' + unicode_fixer(prop_set['default_time_to_live'])
   
capacity_mode = dict(cust_set['custom_properties']['capacity_mode'])

capacity_mode.pop('last_update_to_pay_per_request_timestamp', None)
pitr_status =  dict(cust_set['custom_properties']['point_in_time_recovery'])
pitr_status.pop('earliest_restorable_timestamp',None)

encry_st = cust_set['custom_properties']['encryption_specification']
cust_prop = '{ \'capacity_mode\':' + unicode_fixer(capacity_mode) + ',' + ' \'point_in_time_recovery\':' + unicode_fixer(pitr_status) + ',' + ' \'encryption_specification\':'+ unicode_fixer(encry_st) +'}'

# Retrieve the tags associated with the table
tags_result_set = session.execute(("SELECT * FROM system_schema_mcs.tags WHERE keyspace_name = %s AND resource_name = %s "), (ks,tb))
tags_data = tags_result_set.one()
tags_sch = unicode_fixer(tags_data['tags'])

# Building the schema to recreate the table
final_schema = recreate_table + ttl_comm  + ' AND TAGS = ' + tags_sch + ' AND CUSTOM_PROPERTIES = ' + cust_prop

# Printing final schema to log as backup for scenarios when table was dropped and unable to recreate succesfully 
logger.info(final_schema)

# execute the command check the status of the table. If no exception this represents acknowledgement that the service has received the request.
def DDL_status(resultset):
  try:
     results = resultset.result()
     status = session.execute(('SELECT keyspace_name, table_name, status FROM system_schema_mcs.tables WHERE keyspace_name = %s AND table_name = %s'), (ks,tb))
     if not status:
       return True;
     else :
        return True if status.one()['status'] == 'ACTIVE' else False
  except Exception as execp:
    print (' Exception Encountered :', execp)

# Time loop function to wait for the table status as commands are executed asynchronously 
def duration_loop(t_end, ddl):
    while time.time() < t_end:
      status = DDL_status(ddl)
      if status == True:
        return True;
      else:
         continue 
drp_tbl_state = 'DROP TABLE ' + ks + '.' + tb
# Executing the drop table async statement 
logger.info("Drop Table Initiated")
dp_tbl = session.execute_async(drp_tbl_state)
dp_time = time.time() + 60 * 15 # hard coded to 15 mins from now can increase or decrease time based on need
dp_status = duration_loop(dp_time, dp_tbl) 
time.sleep(30) # sleeping for 30 sec to make sure metadata is updated after table deletion

if dp_status == True :
    # Executing the create table async statement 
    logger.info("ReCreating Table Initiated")
    cr_tbl = session.execute_async(final_schema)
    crt_time = time.time() + 60 * 15 # hard coded to 15 mins from now can increase or decrease time based on need
    crt_status = duration_loop(crt_time, cr_tbl)

if crt_status:
    print("Table Truncate is completed")