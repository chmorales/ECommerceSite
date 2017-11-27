import mysql.connector

def get_connector():
    return mysql.connector.connect(user='root', password='tl35tl35', host='localhost', database='CSE305')

