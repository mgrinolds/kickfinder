# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 17:21:56 2014

@author: Mike
"""

import kickfinder_settings as kfs

class SynchDB:
    
    def __init__(self):
        self.backer_graph = kfs.backer_graph_tbl
        self.project_graph = kfs.project_graph_tbl
        
        self.backer_byname = kfs.backer_byname_tbl
        self.project_byname = kfs.project_byname_tbl
        
    def update_backer_byname(self,do_all=True):
        idname = 'idbackers'
        db_info = self.backer_graph.extract_all_manycols('%s, name' % idname,\
            added_clause="WHERE name IS NOT NULL AND num_projects > %d" % kfs.backer_backed_thresh)

        print len(db_info)
        for id, name in db_info:
            print (id,name)  
            row_dict = {'name':name,idname:id}
            try:    
                self.backer_byname.add_row(row_dict)
            except Exception as e:
                if 'Duplicate' in e.args[1]:
                    pass
                else:
                    raise e

    def update_project_byname(self,do_all=True):
        idname = 'idprojects'
        db_info = self.project_graph.extract_all_manycols('%s, name' % idname,\
            added_clause="WHERE name IS NOT NULL")
    
        print len(db_info)
        for id, name in db_info:
            print (id,name)
            row_dict = {'name':name,idname:id}
              
            try:    
                self.project_byname.add_row(row_dict)
            except Exception as e:
                if 'Duplicate' in e.args[1]:
                    pass
                else:
                    raise e
                
 
if __name__ == '__main__':
    sh = SynchDB()
    
    sh.update_backer_byname()