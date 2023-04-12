import docker, psycopg2, sys
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql
from raftProcClass import raftProc
import os

def run_broker_container(broker_id: int):
    client = docker.from_env()
    env_str = []
    env_str.append("NAME=queue"+str(broker_id))
    env_str.append("PORT="+str(broker_id))
    ports = {'8000/tcp':broker_id, '9000/tcp':broker_id + 2000}
    cont = client.containers.run('broker', environment = env_str, ports = ports)

def create_database(id: int):
    con = psycopg2.connect(dbname='queue',
        user='postgres', host='localhost',
        password='eshamanideep25')

    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) # <-- ADD THIS LINE

    cur = con.cursor()

    database_name = "queue"+str(id)

    #Try to create the database if it does not exist
    try: 
        cur.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(database_name))
            )
    except psycopg2.Error as err:
        #Do nothing as the database already exists 
        print("Database " + database_name + " already exists " + str(err))

#Create the database and then 

create_database(int(sys.argv[1]))
run_broker_container(int(sys.argv[1]))
# pid = os.fork()
# if pid > 0 :
#     create_database(int(sys.argv[1]))
#     run_broker_container(int(sys.argv[1]))
# else :
#     broker = int(sys.argv[1])
#     obj = raftProc(broker + 2000, broker + 2000, broker)