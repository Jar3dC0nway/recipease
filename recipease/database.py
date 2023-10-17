"""
This is used to set up the database tables and import data from a given JSON file
Each
"""

import mysql.connector

from recipease.settings import DATABASE_URL, DATABASE_NAME, USER_NAME, USER_PASSWORD
from recipease.settings import CREATE_TABLES


def connect():
    db = mysql.connector.connect(
        host=DATABASE_URL,
        user=USER_NAME,
        passwd=USER_PASSWORD
    )
    cursor = db.cursor()
    db.database = DATABASE_NAME
    return db, cursor


def close(db):
    db.commit()
    db.close()


def create_tables():
    db, cursor = connect()
    cursor.execute(CREATE_TABLES)
    close(db)
