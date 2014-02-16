# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 10:30:49 2014

@author: Mike
"""
from flask import Flask, render_template, request, json

from operator import itemgetter

import kickfinder_settings as kfs
import dbconverter as dbc
import grapher as graph
import iohandler as ioh

dc = dbc.DBconverter()
network_graph = graph.NetworkGraph()
input_handler = ioh.InputHandler()
output_handler = ioh.OutputHandler()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')
    
@app.route('/about')
def about():
    return render_template('about.html')
    
@app.route('/contact')
def contact():
    return render_template('contact.html')
   
@app.route('/', methods=['POST'])
def search():
    input_string =  request.form['input-name']   
    
    if request.form.has_key('only_active'):
        only_active_flag = request.form['only_active']
    else:
        only_active_flag = 'off'
   
    if not input_string:
        return render_template('index.html')
    
    if only_active_flag == 'on':
        only_active_flag = True
        return_flag = 'on'
    else:
        only_active_flag = False
        return_flag = 'off'
        
#    return str(only_active_flag)
        
    input_id,input_type = input_handler.process_input(input_string)

    if not input_id:
        return "Oops! We could not find this entry (or a similar match) in the database."
    
    if input_type == 'project':
        rec_ids_and_counts = network_graph.find_project_from_project(input_id,kfs.num_web_display,\
            only_active_flag=only_active_flag)
    elif input_type == 'backer':
        rec_ids_and_counts = network_graph.find_project_from_profile(input_id,kfs.num_web_display,\
            only_active_flag=only_active_flag)     
    else:
        return "Unknown input type"
        
    if not rec_ids_and_counts:
        return "Could not find any recommendations. Project not connected to our project/backer graph."
        
    rec_ids,counts = zip(*rec_ids_and_counts)

    input_jinja_dict = output_handler.process_output(input_id,input_type)
    output_jinja_dict = output_handler.process_output(rec_ids,'project')
    
    for ind,result in enumerate(output_jinja_dict):
        count = counts[rec_ids.index(result['idprojects'])]
        output_jinja_dict[ind]['count'] = count
        
    if not output_jinja_dict:
        return "Error in extracting suggested results from database."
    
    output_jinja_dict = sorted(output_jinja_dict, key=itemgetter('count'), reverse=True) 
    
    return render_template('index.html', self_info=input_jinja_dict, \
        results=output_jinja_dict,input_string=input_string,only_active=return_flag)
  
@app.route('/_size_slider')
def mod_norm():
    value = request.args.get('value',0,type=int)
    
    return str(value)
  
def projects():
    """Return list of projects."""

    q = request.args.get('q').replace(';','')   
    
    projects_list = kfs.project_byname_tbl.extract_all('name',"WHERE name LIKE '%%%s%%' LIMIT 5" % q,as_list=True)
    projects_list += kfs.backer_byname_tbl.extract_all('name',"WHERE name LIKE '%%%s%%' LIMIT 5" % q,as_list=True)

    # Python list is converted to JSON string
    return json.dumps(projects_list)

JSON = {
    'projects': projects,
}

@app.route("/json/<what>")
def ajson(what):

    return JSON[what]()


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)