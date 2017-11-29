import pymysql

def get_connector():
    return pymysql.connect(user='root', password='tl35tl35', host='localhost', database='CSE305')

