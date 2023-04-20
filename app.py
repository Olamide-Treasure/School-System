from flask import Flask, flash, session, render_template, redirect, url_for, request
from datetime import datetime, date

import random
import mysql.connector


app = Flask('app')
app.secret_key = 'SECRET_KEY'


mydb = mysql.connector.connect(
    host="phase2-7.cgi21eqy7g91.us-east-1.rds.amazonaws.com",
    user="admin",
    password="phasetwo7",
    database="integration"
)

####################################################
#                    FUNCTIONS                     #
####################################################

# reconnect to database if to referesh any changes made from another device
def _reconnect():
    global mydb
    mydb = mysql.connector.connect(
        host="phase2-7.cgi21eqy7g91.us-east-1.rds.amazonaws.com",
        user="admin",
        password="phasetwo7",
        database="integration"
    )



####################################################
#                    HOME PAGE                     #
####################################################

@app.route('/')
def home():
    return render_template('')