import os
import mysql.connector
from mysql.connector import errorcode
from pymysql import NULL
from sqlalchemy import create_engine
import pymysql
import pandas as pd


host = "localhost"
user = "js"
password = "Yamato%0"
database = "endoscopy"



def connect(host=host, user=user, password=password, database=database):
    try:
        con = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            )

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return NULL

    else:
        return con


def close(con):
    con.close()


def create_database(con, name):
    curs = con.cursor()
    curs.execute("CREATE DATABASE IF NOT EXISTS %s;"%(name))
    curs.close()


def use_database(con, name):
    curs = con.cursor()
    curs.execute("USE %s;"%(name))
    curs.close()


def list_databases(con):
    curs = con.cursor()
    curs.execute("SHOW DATABASES;")
    curs.close()


def list_tables(con,db):
    curs = con.cursor()
    curs.execute("SHOW TABLES;")
    for x in curs:
        print(x)
    curs.close()


def create_info_table(con):
    curs = con.cursor()
    curs.execute(
        "CREATE TABLE IF NOT EXISTS probes_info ("
        "UID INT UNSIGNED NOT NULL AUTO_INCREMENT, "
        "name VARCHAR(30) NOT NULL DEFAULT '', "
        "fiber VARCHAR(30) NOT NULL DEFAULT '', "
        "connector VARCHAR(30) NOT NULL DEFAULT '', "
        "objective VARCHAR(30) NOT NULL DEFAULT '', "
        "status VARCHAR(30) NOT NULL DEFAULT '', "
        "PRIMARY KEY (UID) "
        ");"
    )
    curs.close()


def create_calb_table(con):
    curs = con.cursor()
    curs.execute(
    "CREATE TABLE IF NOT EXISTS probes_cal ("
	"UID INT UNSIGNED NOT NULL, "
	"date DATE NOT NULL DEFAULT(CURDATE()), "
    "time TIME NOT NULL DEFAULT(CURTIME()), "
    "fov_um INT UNSIGNED NOT NULL, "
    "fps INT UNSIGNED NOT NULL, "
    "gain_a DECIMAL , "
    "gain_b DECIMAL NOT NULL, "
    "gain_c DECIMAL NOT NULL, "
    "sfreq DECIMAL NOT NULL, "
    "stime DECIMAL NOT NULL, "
    "sampcos DECIMAL NOT NULL, "
    "sampsin DECIMAL NOT NULL, "
    "stheta DECIMAL NOT NULL, "
    "sphaserel DECIMAL NOT NULL, "
    "bfreqcos DECIMAL NOT NULL, "
    "bfreqsin DECIMAL NOT NULL, "
    "btimecos DECIMAL NOT NULL, "
    "btimesin DECIMAL NOT NULL, "
    "btimerest DECIMAL NOT NULL, "
    "bampcos DECIMAL NOT NULL, "
    "bampsin DECIMAL NOT NULL, "
    "btheta DECIMAL NOT NULL, "
    "bphase DECIMAL NOT NULL, "
    "bphaserel DECIMAL NOT NULL "
	");"
    )
    curs.close()


def create_test_table(con):
    curs = con.cursor()
    curs.execute(
    "CREATE TABLE IF NOT EXISTS test ("
    "UID INT, "
    "date DATE NOT NULL DEFAULT(CURDATE()), "
    "time TIME NOT NULL DEFAULT(TIME(CURTIME())), "
    "n INT "
    ");"
    )
    curs.close()


def create_endo_tables(con, name):
    if name.lower() == "info":
        create_info_table(con)
    elif name.lower() == "calb":
        create_calb_table(con)
    elif name.lower() == "test":
        create_test_table()
    else:
        print("Invalid table name, doing nothing.")


def show_table(con, name, use_pandas=True):
    if use_pandas:
        df = pd.read_sql("SELECT * from %s"%(name), con)
        print(df)
    else:
        curs = con.cursor()
        curs.execute("SELECT * from %s"%(name))
        for x in curs:
            print(x)
        curs.close()


def export_table(con, name, path="", ext="csv"):
    query = "SELECT * from %s;"%(name)
    df = pd.read_sql(query, con)

    if path:
        if not os.path.isdir(path):
            os.makedirs(path)    

    if ext.lower() == "xlsx":
        df.to_excel(os.path.join(path, name + "." + ext))
    elif ext.lower() == "csv":
        df.to_csv(os.path.join(path, name + "." + ext))
    else:
        print("Invalid or non implemented extenstion type, doing nothing.")


def addto_table(con, table, list_cols, list_vals, autocommit=True):
    curs = con.cursor()

    str_cols =", ".join(map(str,list_cols))
    str_vals =", ".join(map(str,list_vals))

    query = "INSERT INTO %s (%s) VALUES (%s);"%(table, str_cols, str_vals)
    print("SQL query: " + query)

    curs.execute(query)
    curs.close()

    if autocommit:
        commit(con)


def deletefrom_table(con, table, condstr="", autocommit=True):
    curs = con.cursor()
    curs.execute("DELETE FROM %s %s;"%(table, condstr))
    curs.close()

    if autocommit:
        commit(con)


def delete_table(con, name):
    curs = con.cursor()
    curs.execute("DROP TABLE IF EXISTS %s;"%(name))
    curs.close()


def alter_add_col(con, name, col, type, after=""):
    curs = con.cursor()

    query = "ALTER TABLE %s ADD COLUMN %s %s"%(name, col, type)
    if after:
        query = query + " AFTER " + after + ";"
    curs.execute(query + ";")
    # mycursor.execute("ALTER TABLE test ADD COLUMN date DATE AFTER uid;")

    curs.close()


def commit(con):
    curs = con.cursor()
    curs.execute("COMMIT;")
    curs.close()


def rollback(con):
    curs = con.cursor()
    curs.execute("ROLLBACK;")
    curs.close()





if __name__ == "__main__":
    con = connect(host=host, user=user, password=password, database=database)
    use_database(con, "endoscopy")
    list_tables(con, "endoscopy")

    create_test_table(con)
    
    alter_add_col(con, "test", "hh", "INT", after="uid")

    addto_table(con, "test", ["UID","n"], ["1", "1"])
    addto_table(con, "test", ["UID","n"], ["2", "2"])
    addto_table(con, "test", ["UID","n"], ["3", "3"])
    # show_table(con, "test")

    # deletefrom_table(con, "test", condstr="WHERE uid = 10")
    # show_table(con, "test")

    # export_table(con, "test")

    delete_table(con, "test")

    delete_table(con, "probes_cal")

    create_calb_table(con)

    addto_table(con, "probes_cal", ["UID","fov_um","fps"], ["1", "100", "10"])



    

    close(con)










    






