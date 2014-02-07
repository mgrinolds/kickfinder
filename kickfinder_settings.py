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
sleep_time = 1 #max random time between scrapes
base_url = 'http://www.kickstarter.com'
backer_backed_thresh = 10
num_web_display = 20

backer_graph_tbl = SqlTable(connection,'backers_nohtml')
backer_graph_tbl.query("SET global wait_timeout=30000000;")
backer_graph_tbl.query("SET session wait_timeout=30000000;")

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

backer_html_tbl = SqlTable(connection,'backers_all')
project_html_tbl = SqlTable(connection,'projects_new')



del table_name, create_str

