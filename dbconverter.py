# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 18:42:02 2014

@author: Mike
"""

import kickfinder_settings as kfs

class DBconverter():
    def __init__(self):
        self.backer_graph = kfs.backer_graph_tbl
        self.project_graph = kfs.project_graph_tbl
        
        self.backer_byname = kfs.backer_byname_tbl
        self.project_byname = kfs.project_byname_tbl
    
    def proj_id_from_unknown(self,input_str): 
        safe_str = input_str.replace(';','')
        
        if safe_str.find('/') == -1:
            return self.proj_id_from_name(safe_str)
        else:
            if kfs.base_url in safe_str:
                safe_str = safe_str.replace(kfs.base_url,'')                
                
            return self.proj_id_from_link(safe_str)
            
    def backer_id_from_unknown(self,input_str):
        safe_str = input_str.replace(';','')
        
        if safe_str.find('/') == -1:
            return self.backer_id_from_name(safe_str)
        else:
            if kfs.base_url in safe_str:
                safe_str = safe_str.replace(kfs.base_url,'')                
                
            return self.backer_id_from_link(safe_str)    
    
    def proj_id_from_name(self,name):
        db_info = self.project_byname.extract_single('idprojects','name',name)        
        return self._parse_return(db_info)
        
    def backer_id_from_name(self,name):
        db_info = self.backer_byname.extract_single('idbackers','name',name)   
        return self._parse_return(db_info)    
    
    
    def proj_id_from_link(self,links):
        db_info = self.project_graph.extract_all_manycols('idprojects','url',links)
        return self._parse_return(db_info)
     
    def backer_id_from_link(self,links):
        db_info = self.backer_graph.extract_all_manycols('idbackers','profile_link',links)
        return self._parse_return(db_info)
         
         
    def proj_name_from_id(self,ids):
        db_info = self.project_graph.extract_all_manycols('name','idprojects',ids)
        return self._parse_return(db_info)
        
    def backer_name_from_id(self,ids):
        db_info = self.backer_graph.extract_all_manycols('name','idbackers',ids)
        return self._parse_return(db_info)
    
    
    def website_info_from_proj_ids(self,ids):
        db_info = self.project_graph.extract_all_manycols_noL( """name, 
                                         url, 
                                         nbackers, 
                                         image_url, 
                                         description, 
                                         prediction, 
                                         percent_raised,
                                         idprojects"""\
                                         ,'idprojects',ids) 
        
#        return self._parse_return(db_info)
        return db_info

    def website_info_from_backer_ids(self,ids):
        db_info = self.backer_graph.extract_all_manycols_noL( """name, 
                                         profile_link, 
                                         image_url, 
                                         description,
                                         num_projects,
                                         idbackers"""\
                                         ,'idbackers',ids) 
        
#        return self._parse_return(db_info)
        return db_info        
        
    def _parse_return(self,db_info):
        if db_info:
            if (type(db_info) is not tuple):
                return db_info
            
            if len(db_info[0]) > 1:
                return db_info[0]
            else:
                return db_info[0][0]
        else:
            return None       
            
            
if __name__ == '__main__':
    input_string = 'MEGAcquire - An Enhanced Adventure Into High Finance'
    
    dc = DBconverter()
    
    result1 = dc.proj_id_from_unknown(input_string)
    
    result2 = dc.website_info_from_proj_ids(result1)