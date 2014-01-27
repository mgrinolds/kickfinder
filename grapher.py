# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 16:22:02 2014

@author: Mike
"""

from __future__ import division
import networkx as nx
import numpy as np
from collections import Counter

import kickfinder_settings as kfs
import dbconverter as dbc

class NetworkGraph:
    
    def __init__(self):
        self.backer_sql = kfs.backer_graph_tbl
        self.project_sql = kfs.project_graph_tbl

        self.backer_backed_thresh = kfs.backer_backed_thresh          

        self.G = None        
        self._load_graph()
        
        
    def find_from_project(self,project_id,nentries):
        if not self.G.has_node(project_id):
            return None        
        
        neighbors = self.G.neighbors(project_id)
        next_neighbors_2d = [self.G.neighbors(neighbor) for neighbor in neighbors]    
        next_neighbors = [item for sublist in next_neighbors_2d for item in sublist]    
        
#        next_neighbors.remove(project_id)      
           
        nn_count = Counter(next_neighbors)
        nn_count.pop(project_id)
        nn_top_occur = nn_count.most_common(nentries)  

        return nn_top_occur

    def find_from_profile(self,profile_id,nentries):    
        if not self.G.has_node(profile_id):
            return None
        
        neighbors = self.G.neighbors(profile_id)
        next_neighbors_2d = [self.G.neighbors(neighbor) for neighbor in neighbors]    
        next_neighbors = [item for sublist in next_neighbors_2d for item in sublist]    
        
        next_neighbors.remove(profile_id)    

        nn_thresh = 5000
        next_neighbors = next_neighbors[:nn_thresh]
        
        next_next_neighbors_2d = [self.G.neighbors(next_neighbor) for next_neighbor in next_neighbors]    
        next_next_neighbors = [item for sublist in next_next_neighbors_2d for item in sublist]
            
        nnn_count = Counter(next_next_neighbors)
    
        [nnn_count.pop(neighbor_link) for neighbor_link in neighbors]
    
        common_tuple = nnn_count.most_common(len(nnn_count)//5)
        
        counts = np.array([count for link, count in common_tuple if count > 50],dtype='float')
        graph_links = [link for link, count in common_tuple if count > 50]

#        return graph_links

#        db_info = self.project_sql.extract_all_manycols('name, nbackers',\
#            'url',graph_links,"AND nbackers > 0")  

        db_info = self.project_sql.extract_all_manycols('idprojects, nbackers',\
            'idprojects',graph_links,added_clause="AND nbackers > 0") 

        db_links, sizes = zip(*db_info)
            
        for ind,graph_link in enumerate(graph_links):
            if graph_link in db_links:
                counts[ind] = counts[ind] / sizes[db_links.index(graph_link)]
            else:
                counts[ind] = 0
    
        top_inds = np.argsort(counts)[::-1][:nentries]
        
        top_projects = [graph_links[ind] for ind in top_inds]
        top_counts = [counts[ind] for ind in top_inds]    
        
        return zip(top_projects, top_counts)  
        
    def _load_graph(self):
        
#        db_extract = self.backer_sql.extract_all_manycols(\
#            'profile_link, projects',\
#            added_clause = "WHERE has_projects = 1 AND num_projects > %d" \
#                % self.backer_backed_thresh)
        
        db_extract = self.backer_sql.extract_all_manycols(\
            'idbackers, projects_inds',\
            added_clause = "WHERE projects_inds IS NOT NULL AND num_projects > %d" \
                % self.backer_backed_thresh)
              
        add_links = []
        total_projects = []
        backer_ids = []
        for backer_id, projects in db_extract:
            ind_projects = eval(projects)
            
            for single_project in ind_projects:
                total_projects.append(single_project)
                add_links.append((backer_id,single_project))
                
            backer_ids.append(backer_id)    
        
        unique_projects = list(set(total_projects))
        
        self.G = nx.Graph()    
        self.G.add_nodes_from(unique_projects + backer_ids)
        self.G.add_edges_from(add_links)

if __name__ == '__main__':
    try:
        ng
    except:
        ng = NetworkGraph()    

    dc = dbc.DBconverter()
    proj_id = dc.proj_id_from_link(['/projects/elitecards/one-million-bicycle-playing-cards-deck'])

    preds = ng.find_from_project(proj_id,10)
    for pred, count in preds:
        print (pred,count)
        print (dc.proj_name_from_id(pred),count)
     
    backer_id = dc.backer_id_from_link(['/profile/1044791950']) 
    preds = ng.find_from_profile(backer_id,10)
    for pred, count in preds:
        print (dc.proj_name_from_id(pred),count)