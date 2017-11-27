import mysql.connector

def get_connector():
    return mysql.connector.connect(user='root', password='noobama12', host='localhost', database='CSE305')

