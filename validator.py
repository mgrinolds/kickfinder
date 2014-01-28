# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 16:33:48 2014

@author: Mike
"""

from __future__ import division
import kickfinder_settings as kfs
import grapher as graph
import numpy.random as rand

class RecValidator:
    
    def __init__(self):
        self.project_sql = kfs.project_graph_tbl
        self.backer_sql = kfs.backer_graph_tbl
        self.holdout_frac = 0.25
        self.graph = graph.NetworkGraph()        
    
    def validate_all(self,reset=False):
        
        ntotalbackings = self.project_sql.query("SELECT SUM(nbackers) FROM %s" \
                                                    % self.project_sql.table_name)[0][0]
        
        if reset:
            id_backers = self.backer_sql.extract_all_manycols('idbackers',\
                added_clause = "WHERE num_projects > %d" % kfs.backer_backed_thresh)
                
            self.backer_sql.query("UPDATE %s SET validated_found = Null WHERE validated_found IS NOT NULL" % self.backer_sql.table_name)
            self.backer_sql.query("UPDATE %s SET validated_tried = Null WHERE validated_tried IS NOT NULL" % self.backer_sql.table_name)
            self.backer_sql.query("UPDATE %s SET validated_baseline = Null WHERE validated_baseline IS NOT NULL" % self.backer_sql.table_name)
        else:
            id_backers = self.backer_sql.extract_all_manycols('idbackers',\
                added_clause = "WHERE num_projects > %d AND validated_found IS NULL" % kfs.backer_backed_thresh)

        print len(id_backers)
        for ind,id_backer in enumerate(id_backers):

#             print (ind,id_backer[0])             
                     
             self.validate_backer_single(id_backer[0],ntotalbackings) 
             

        return id_backers
    
    def validate_backer_single(self,backer_id,ntotalbackings):
        db_extract = self.backer_sql.extract_all_manycols(\
            'projects_inds',added_clause = "WHERE idbackers = %d" % backer_id)
        
#        nprojects = self.project_sql.query("SELECT COUNT(*) FROM %s" % self.project_sql.table_name)[0][0]

        # User not in the database 
        if not db_extract:
            return -1
         
        # User not in graph
        if not self.graph.G.has_node(backer_id):
            return -1
 
        backed_project_ids = eval(db_extract[0][0])
        
        nholdout = int(self.holdout_frac*len(backed_project_ids))
        
        # User doesn't have sufficient backed projects
        if nholdout < 1:
            return -1
            
        remove_ids = [None] * nholdout
        for ind in range(nholdout):
            rand_ind = rand.randint(len(backed_project_ids))
            remove_ids[ind] = backed_project_ids.pop(rand_ind)
            
        remove_nodes_in_graph = [self.graph.G.has_node(ind_id) for ind_id in remove_ids]            

        # Can't find all of the nodes to be removed in the graph
        if sum(remove_nodes_in_graph) < nholdout:
            return -1
        
        total_graph_edges = self.graph.G.number_of_edges()

        remove_edges = zip(remove_ids,[backer_id]*nholdout)
        self.graph.G.remove_edges_from(remove_edges)

        results = self.graph.find_project_from_profile(backer_id,nholdout,remove_ids)
        
        if not results:
            return -1
        
        rec_ids, discard = zip(*results)
        
        noverlap = len(set(rec_ids) & set(remove_ids))       
        
        nremovedbackings = int(self.project_sql.extract_all_manycols_noL("SUM(nbackers)",\
                'idprojects',remove_ids)[0][0])           
        
        
#        nrandoverlap = nholdout/nprojects             

        nrandoverlap = nremovedbackings/ntotalbackings
        
        print (noverlap,nrandoverlap,backer_id)
        
        self.graph.G.add_edges_from(remove_edges)

        # Make sure graph hasn't changed
        assert(total_graph_edges == self.graph.G.number_of_edges())
        
        # Update db
        self.backer_sql.update_value('validated_found',noverlap,'idbackers',backer_id)
        self.backer_sql.update_value('validated_tried',nholdout,'idbackers',backer_id)
        self.backer_sql.update_value('validated_baseline',nrandoverlap,'idbackers',backer_id)
        
        return noverlap
        
if __name__ == '__main__':
        rv = RecValidator()
        
#    out = rv.validate_backer_single(12)
        out = rv.validate_all(reset=True)