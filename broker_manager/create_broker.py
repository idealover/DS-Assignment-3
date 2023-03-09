import docker, psycopg2, sys
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql

def run_broker_container(broker_id: int):
    client = docker.from_env()
    env_str = "NAME=queue"+str(broker_id)
    ports = {'8000/tcp':broker_id}
    cont = client.containers.run('broker', environment = [env_str], ports = ports)

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