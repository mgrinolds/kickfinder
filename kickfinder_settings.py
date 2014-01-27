# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 14:58:46 2014

@author: Mike
"""

from sqlwrap import SqlTable
import MySQLdb as mdb
import get_pw as gp
import requests 

database_name = 'kickstarter'
connection = mdb.connect('localhost', 'mgrinolds', gp.get_pw(), database_name) 
session = requests.Session()
sleep_time = 2.5 #max random time between scrapes
base_url = 'http://www.kickstarter.com'
backer_backed_thresh = 25
num_web_display = 20

backer_graph_tbl = SqlTable(connection,'backers_nohtml')
project_graph_tbl = SqlTable(connection,'projects_nohtml')

table_name = 'backers_byname'
create_str = \
    """CREATE TABLE %s (
      name VARCHAR(100) NOT NULL,
      idbackers INT(11) NULL,
      PRIMARY KEY (name),
      UNIQUE INDEX name_UNIQUE (name ASC));""" \
      % (table_name)
backer_byname_tbl = SqlTable(connection,table_name)
if not backer_byname_tbl.table_exists():
    backer_byname_tbl.query(create_str)
    
table_name = 'projects_byname'
create_str = \
    """CREATE TABLE %s (
      name VARCHAR(100) NOT NULL,
      idprojects INT(11) NULL,
      PRIMARY KEY (name),
      UNIQUE INDEX name_UNIQUE (name ASC));""" \
      % (table_name)
project_byname_tbl = SqlTable(connection,table_name)
if not project_byname_tbl.table_exists():
    project_byname_tbl.query(create_str)

backer_html_tbl = SqlTable(connection,'backers_html')
project_html_tbl = SqlTable(connection,'projects_html')



del table_name, create_str

