from cassandra.cluster import *
from ssl import SSLContext, PROTOCOL_TLSv1_2 , CERT_REQUIRED
from cassandra.auth import PlainTextAuthProvider
from rediscluster import RedisCluster
import logging
import time

#Keyspaces connection
ssl_context = SSLContext(PROTOCOL_TLSv1_2)
ssl_context.load_verify_locations('/home/ec2-user/sf-class2-root.crt')
ssl_context.verify_mode = CERT_REQUIRED
exec_profile = ExecutionProfile(consistency_level=ConsistencyLevel.LOCAL_QUORUM, 
                                load_balancing_policy=DCAwareRoundRobinPolicy())
auth_provider = PlainTextAuthProvider(username='YOUR USERNAME', 
                                      password='YOUR PASSWORD')
cluster = Cluster(['cassandra.us-east-1.amazonaws.com'], 
                  ssl_context=ssl_context, 
                  auth_provider=auth_provider, 
                  port=9142, 
                  execution_profiles={EXEC_PROFILE_DEFAULT: exec_profile})
session = cluster.connect()


#Amazon Elasticache connection
logging.basicConfig(level=logging.ERROR)
redis = RedisCluster(startup_nodes=[{"host": "cluster_identifier.xxxxx.clustercfg.use1.cache.amazonaws.com", 
                                     "port": "6379"}], 
                     decode_responses=True,
                     skip_full_coverage_check=True)
if redis.ping():
    logging.info("Connected to Redis")


#Global variables
keyspace_name="catalog"
table_name="book_awards"

#Write a row 
def write_award(book_award):
    write_award_to_keyspaces(book_award)
    write_award_to_cache(book_award)

#write row to the Keyspaces table
def write_award_to_keyspaces(book_award):
    stmt = session.prepare(f"INSERT INTO {keyspace_name}.{table_name} (award, year, category, rank, author, book_title, publisher) VALUES (?, ?, ?, ?, ?, ?, ?);")
    session.execute(stmt, 
                    parameters=[book_award["award"], 
                                book_award["year"], 
                                book_award["category"], 
                                book_award["rank"], 
                                book_award["author"], 
                                book_award["book_title"], 
                                book_award["publisher"]])

#write row to the cache
def write_award_to_cache(book_award):
    #construct Redis key name
    key_name=book_award["award"]+str(book_award["year"])+book_award["category"]+str(book_award["rank"])
    
    #write to cache using Redis set, ex=300 sets TTL for this row to 300 seconds
    redis.set(key_name, str(book_award), ex=300)


#Delete a row
def delete_award(award, year, category, rank):
    delete_award_from_keyspaces(award, year, category, rank)
    delete_award_from_cache(award, year, category, rank)

#delete row from Keyspaces table
def delete_award_from_keyspaces(award, year, category, rank):
    stmt = session.prepare(f"DELETE FROM {keyspace_name}.{table_name} WHERE award=? AND year=? AND category=? AND rank=?;")
    session.execute(stmt, parameters=[award, int(year), category, int(rank)])

#delete row from cache
def delete_award_from_cache(award, year, category, rank):
    #construct Redis key name    
    key_name=award+str(year)+category+str(rank)
    
    #delete the row from cache if it exists
    if redis.get(key_name) is not None:
        book_award=redis.delete(key_name)

#Read a row
def get_award(award, year, category, rank):
    #construct Redis key name from parameters
    key_name=award+str(year)+category+str(rank)
    book_award=redis.get(key_name)
    
    #if row not in cache, fetch it from Keyspaces table
    if not book_award:
        print("Fetched from Cache: ", book_award)
        stmt = session.prepare(f"SELECT * FROM {keyspace_name}.{table_name} WHERE award=? AND year=? AND category=? AND rank=?;")
        res=session.execute(stmt, parameters=[award, int(year), category, int(rank)])
        if not res.current_rows:
            print("Fetched from Database: None")
            return None
        else:
            #lazy-load into cache
            book_award=redis.set(key_name, str(res.current_rows), ex=300)
            print("Fetched from Database: ")
            return res.current_rows
    else:
        print("Fetched from Cache: ")
        return book_award


#Read one or more rows based on parameters
def get_awards(parameters):
    #construct key name from parameters
    key_name=""
    for p in parameters:
        key_name=key_name+str(p)
    book_awards=redis.lrange(key_name, 0, -1)
    
    #if result set not in cache, fetch it from Keyspaces table
    if not book_awards:
        print("Fetched from Cache: ", book_awards)
        stmt = session.prepare(f"SELECT * FROM {keyspace_name}.{table_name} WHERE award=? AND year=? AND category=? AND rank<=?;")
        res=session.execute(stmt, parameters)
        if not res.current_rows:
            print("Fetched from Database: None")
            return None
        else:
            #lazy-load into cache
            redis.rpush(key_name, str(res.current_rows))
            redis.expire(key_name, 300)
            print("Fetched from Database: ")
            return res.current_rows
    else:
        print("Fetched from Cache: ")
        return book_awards

