import sqlite3
import os
import os.path as osp

sysPath = os.getcwd().replace('\\','/')

dataPath = sysPath + "/data"
dataBase = "ysdata.db"
tableName = "ys"


def mkdir(dir_name):
    if not osp.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
    return


def create_database_table(database_path, database, table_name):
    mkdir(database_path)
    database_connect = sqlite3.connect(osp.join(database_path, database))
    print("open database:%s successfully" % database)
    database_cur = database_connect.cursor()
    try:
        database_cur.execute(
            "create table %s(num INTEGER PRIMARY KEY, pname TEXT, pclass TEXT, ppointvalue TEXT, bdData TEXT);" % table_name)
    except:
        print("table:%s has existed" % table_name)
    return database_cur, database_connect

# create_database_table(dataPath,dataBase,tableName)

def insert(values):
    database_connect = sqlite3.connect(osp.join(dataPath, dataBase))
    database_cur = database_connect.cursor()
    database_cur.execute("INSERT INTO %s VALUES(?,?,?,?,?);" % tableName, (None, values[0], values[1], values[2],values[3]))
    database_connect.commit()
    database_connect.close()
    return True
# insert(("第二个","20220817","110000220"))
def fetchall(sqlLau='SELECT * FROM ys'):
     '''查询所有数据'''
     database_connect = sqlite3.connect(osp.join(dataPath, dataBase))
     database_cur = database_connect.cursor()
     database_cur.execute(sqlLau)
     database_connect.commit()
     res = database_cur.fetchall()
     database_connect.close()
     return res


def fetchValue(dxfPointRes):
    '''查询所有数据'''
    database_connect = sqlite3.connect(osp.join(dataPath, dataBase))
    database_cur = database_connect.cursor()
    sqlLau = "SELECT * FROM ys WHERE pcode = ? LIMIT 1;"
    database_cur.execute(sqlLau, (dxfPointRes,))
    res = database_cur.fetchall()
    database_connect.close()
    return res

res = fetchall(sqlLau='SELECT * FROM ys WHERE boxID=\'1\'')
print(len(res))
#select * from 表 where 字段名='查询的字段值';
# print(fetchall(sqlLau='select * from picSave where pclass=\'%s\'' %picClass))