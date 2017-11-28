import pymysql

def get_connector():
    return pymysql.connect(user='root', password='PlaidFlannelFleece', host='localhost', database='CSE305')

