import os
from time import sleep

import pandas as pd
import paramiko
import pymysql
from loguru import logger
from sshtunnel import SSHTunnelForwarder


def query_data(queries, config):
    """
    query_data queries data from MySQL remote and save the data in a dataframe.

    Input queries should be a list of dictionaries with `name` and `query` as keys.
    The key `name` is only used for logs. It is strongly advised to include it.

    .. code-block:: python

       queries = [{
          "name": query_name,
         "query": query_content
       }]

    Here is an example of the config param.

    .. code-block:: python

       config = {
           "sql_hostname": os.getenv("PLATFORM_SQL_URI"), # 'sql_hostname'
           "sql_username": os.getenv("PLATFORM_SQL_USERNAME"), # 'sql_username'
           "sql_password": os.getenv("PLATFORM_SQL_PWD"),  # 'sql_password'
           "sql_main_database": 'db_name', # 'db_name'
           "sql_port": 3306,
           "ssh_host": 'a.ssh.host.saloodo.com', #'ssh_hostname'
           "ssh_user": 'my_ssh_username', #'ssh_username'
           "ssh_port": 22,
           "ssh_key": ssh_key #
       }

    :param query: SQL queries arranged in a list of dictionaries with .
    :type query: str
    :return: dataframe of the returned data from the query
    :rtype: pandas.core.frame.DataFrame
    """

    sql_hostname = config.get("sql_hostname")  # 'sql_hostname'
    sql_username = config.get("sql_username")  # 'sql_username'
    sql_password = config.get("sql_password")  # 'sql_password'
    sql_main_database = config.get("sql_main_database")  # 'db_name'
    sql_port = config.get("sql_port")
    ssh_host = config.get("ssh_host")  #'ssh_hostname'
    ssh_user = config.get("ssh_user")  #'ssh_username'
    ssh_port = config.get("ssh_port")
    ssh_key = config.get("ssh_key")

    if ssh_key is None:
        logger.warning("config does not include ssh_key\nUsing default in .ssh/id_rsa")
        home = os.path.expanduser("~")
        pkeyfilepath = os.path.join(".ssh", "id_rsa")
        ssh_key = paramiko.RSAKey.from_private_key_file(
            os.path.join(home, pkeyfilepath)
        )
    if isinstance(ssh_key, str):
        logger.warning(
            f"input config has ssh_key as strings: {ssh_key}\nConverting to key"
        )
        ssh_key = paramiko.RSAKey.from_private_key_file(ssh_key)

    logger.info("Connecting to Server ... ")
    with SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_user,
        ssh_pkey=ssh_key,
        remote_bind_address=(sql_hostname, sql_port),
    ) as tunnel:
        sleep(3)
        conn = pymysql.connect(
            host="127.0.0.1",
            user=sql_username,
            passwd=sql_password,
            db=sql_main_database,
            port=tunnel.local_bind_port,
        )
        logger.info("Connected to the MySQL server")
        sleep(1)
        datasets = []
        for query in queries:
            logger.debug(query)
            query_query = query.get("query")
            logger.info(f"Running query for {query.get('name')}")
            data = pd.read_sql_query(query_query, conn)
            query["data"] = data.copy()
            datasets.append(query)
            sleep(10)

        conn.close()

    return datasets


def load_query(sql_file):
    """
    load_query loads a sql query file as strings.
    load_query is best combined with query_data to retrieve data from database.

    :param sql_file: path to sql file
    :type sql_file: str
    :return: string representation of the sql query
    :rtype: str
    """

    if not os.path.exists(sql_file):
        raise Exception(f"SQL file {sql_file} does not exist!")

    with open(sql_file) as fp:
        sql = fp.read()

    if not sql:
        logger.error(f"No content from sql file: {sql_file}")

    return sql
