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

dc = dbc.DBconverter()
network_graph = graph.NetworkGraph()

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')
   
@app.route('/', methods=['POST'])
def search():
    input_string =  request.form['input-name']   
    

    id_from_project = dc.proj_id_from_unknown(input_string)
    id_from_backer = dc.backer_id_from_unknown(input_string)
    
    if id_from_project:
        own_info = dc.website_info_from_proj_ids(id_from_project)
        
        self_info = []
        self_info.append(dict(  index=0,\
                                name=unicode(own_info[0][0], 'utf8'), \
                                url=kfs.base_url + own_info[0][1], \
                                nbackers=own_info[0][2], \
                                image_url=own_info[0][3],\
                                description=own_info[0][4],\
                                count=0,\
                                prediction = '%.0f' % (own_info[0][5]*100)\
                                    ))
                                    
        results = network_graph.find_project_from_project(id_from_project,kfs.num_web_display)
            
    elif id_from_backer:
        
        print id_from_backer        
        own_info = dc.website_info_from_backer_ids(id_from_backer)
        
        self_info = []
        self_info.append(dict(  index=0,\
                                name=unicode(own_info[0][0], 'utf8'), \
                                url=kfs.base_url + own_info[0][1], \
                                nbackers=own_info[0][5], \
                                image_url=own_info[0][2],\
                                description=own_info[0][4],\
                                count=0\
                                    ))
        
        results = network_graph.find_project_from_profile(id_from_backer,kfs.num_web_display)   
    else:
        return 'database error'    

    
    ids,counts = zip(*results)
    
    db_info = dc.website_info_from_proj_ids(ids)
    
    base_url = "http://www.kickstarter.com"    
    
    results = []
    for ind,result in enumerate(db_info):
        count = counts[ids.index(result[7])]        
        results.append(dict(index=ind,name=unicode(result[0], 'utf8'), url=base_url + result[1], nbackers=result[2], \
            image_url=result[3],description=result[4],count=count,prediction='%.0f' % (result[5]*100)))

    results = sorted(results, key=itemgetter('count'), reverse=True)    
                  
    return render_template('index.html', self_info=self_info, results=results,input_string=input_string) 

  
@app.route('/_size_slider')
def mod_norm():
    value = request.args.get('value',0,type=int)
    
    return str(value)
  
def projects():
    """Return list of projects."""

    q = request.args.get('q')    
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
    app.run(debug=True)