'''The following script will export schema from existing cassandra cluster and checks if the current cassandra cluster is using any api's that Amazon Keyspaces doesn't support yet

## Prerequisites: download required libraries like python,boto3 and cassandra-driver

usage instructions:
1. Download this python script from github and move it to machine/vm/container that can access your cassandra cluster
2. If you want to connect to cassandra cluster and perform a compatibility assesment, then run below command
python toolkit-compat-tool.py --host "hostname or IP" -u "username" -p "password" --port "native transport port"
3. If you want to simply perform compatibility assesment against schema file, you can skip step 2 and run these commands
cqlsh '<hostname>' <port> -u '<username>' -p '<password>' -e "describe schema" > schema.cql
python toolkit-compat-tool.py --file 'schema.cql'
4. There are several workarounds available for unsupported features, you can reachout to AWS support for further assistance

##
 Execution Sample commands: python toolkit-compat-tool --host "hostname"  -u "username" -p "pwd" --ssl 
                            python toolkit-compat-tool --host "hostname"  -u "username" -p "pwd" --port 9042
                            python toolkit-compat-tool --file 'schema.cql' 

'''
import boto3, time, sys
import getpass
import optparse
import os, re
import sys
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.query import dict_factory
from cassandra.metadata import KeyspaceMetadata, TableMetadata, Metadata
from ssl import SSLContext, PROTOCOL_TLSv1_2, CERT_REQUIRED
#from cassandra_sigv4.auth import *
from cassandra.auth import PlainTextAuthProvider
import logging

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 9042
DEFAULT_SSL = False
DEFAULT_SIGV4 = False
DEFAULT_CONNECT_TIMEOUT_SECONDS = 5
DEFAULT_REQUEST_TIMEOUT_SECONDS = 10
DEFAULT_AUTH_PROVIDER = 'PlainTextAuthProvider'
auth = False

parser = optparse.OptionParser(description='Compatibility tool')
parser.add_option('--host', help='Amazon Keyspaces endpoint')
parser.add_option("--sigv4", action='store_true', help='Use SigV4AuthProvider plugin for autentication and authorization', default=DEFAULT_SIGV4)
parser.add_option("--auth-provider", help="The AuthProvider to use when connecting. Default is PlainTextAuthProvider", dest='auth_provider_name', default=DEFAULT_AUTH_PROVIDER)
parser.add_option("-u", "--username", help="Authenticate as user.")
parser.add_option("-p", "--password", help="Authenticate using password.")
parser.add_option('--ssl', action='store_true', help='Use SSL', default=False)
parser.add_option("--port", help='Port to connect to cassandra', type=int)
parser.add_option("--file", help='Schema file to run compatability script against')



# The function checks the schema and provides the compatability 
def schema_check(cluster_schema):

 api_features = ['CREATE INDEX', 'CREATE TYPE', 'CREATE TRIGGER', 'CREATE FUNCTION', 'CREATE AGGREGATE', 'CREATE MATERIALIZED VIEW', 'cdc = true']
 unsupported_features_List = {}
 unsupported_features_message = {}

 unsupported_features_message['CREATE INDEX'] = 'Secondary Index'
 unsupported_features_message['CREATE TYPE'] = 'User Defined Type'
 unsupported_features_message['CREATE TRIGGER'] = 'Trigger'
 unsupported_features_message['CREATE FUNCTION'] = 'User Defined function'
 unsupported_features_message['CREATE AGGREGATE'] = 'Aggregators'
 unsupported_features_message['CREATE MATERIALIZED VIEW'] = 'Materialized View'
 unsupported_features_message['cdc = true'] = 'Change Data Capture'

 for item in api_features:
  occurances = re.findall( item, cluster_schema, re.IGNORECASE)
  if len(occurances) != 0:
     unsupported_features_List[item] = len(occurances)   
 
 if len(unsupported_features_List) == 0:
    print("No unsupported Cassandra operators found")
 
 elif len(unsupported_features_List) > 0:
    print("")
    print('The following {} unsupported features were found. Some of these features have workarounds. Please contact AWS Account team or Amazon Keyspaces team through AWS support to know about Workaround information'.format(len(unsupported_features_List)))
    for item in unsupported_features_List.keys():
       print("")
       print("  {} | found {} time(s)".format(unsupported_features_message[item], unsupported_features_List[item]))
 
optvalues = optparse.Values()
(options, arguments) = parser.parse_args(sys.argv[1:], values=optvalues)

if hasattr(options, 'file'):
   schema_path = str(options.file)
   file_check = os.path.isfile(schema_path)
   if file_check:
    # Read the schema if file exists
     with open(schema_path, 'r') as file:
      schema = file.read()
    # calls the check schema function for compatability  
      schema_check(schema)
      print("")
      sys.exit("Script Execution Completed")
 # Exists the script if the file path provided is invalid   
   else:  
      print("")
      sys.exit("NO FILE EXISTS,re-validate the path and re-run the script again")   


if hasattr(options, 'host'):
   endpoint = str(options.host).replace("'", '')
else:
   endpoint = DEFAULT_HOST

if hasattr(options, 'username'):
   username = str(options.username)
else:
   username = None

if hasattr(options, 'password'):   
   password = str(options.password)
else:
   password = None

if hasattr(options, 'port'):
   cql_port = options.port
else:
   cql_port = DEFAULT_PORT

if hasattr(options, 'ssl'):
    ssl = True
else:
   ssl = DEFAULT_SSL

if ( hasattr(options, 'sigv4') | hasattr(options, 'auth_provider_name') ):
   auth = True

user = getpass.getuser()
user_dir = os.path.expanduser('~'+user)
config_dir = os.path.join( user_dir, '.cassandra')
cert_dir = os.path.join(config_dir, 'sf-class2-root.crt')
compat_log = os.path.join(config_dir, 'compat')

#now we will Create and configure logger 
logging.basicConfig(filename=compat_log, 
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
        raise SyntaxError('Invalid parameter for auth-provider. "%s" is not a valid AuthProvider' % (auth_provider,))
else:
    if username:
        auth = True
        if not hasattr(options, 'password'):
            password = getpass.getpass()
            auth_provider = PlainTextAuthProvider(username=username, password=password)
        else:
            auth_provider = PlainTextAuthProvider(username=username, password=password)

profile = ExecutionProfile(request_timeout= None, row_factory=dict_factory)

cluster = Cluster( [endpoint], ssl_context=ssl_context if ssl else None, auth_provider=auth_provider if auth else None, port=cql_port,
                   execution_profiles={EXEC_PROFILE_DEFAULT: profile})
session = cluster.connect()
cluster_schema = cluster.metadata.export_schema_as_string()
schema_check(cluster_schema)
print("")
sys.exit("Script Execution Completed")

