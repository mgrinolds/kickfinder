# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 19:38:21 2014

@author: Mike
"""

import kickfinder_settings as kfs
import dbconverter as dbc

class InputHandler():
    
    def __init__(self):
        self.project_sql = kfs.project_byname_tbl
        self.backer_sql = kfs.backer_byname_tbl
     
    def process_input(self,input_str):
        
        if not input_str:
            return (None, None)
   
        input_str = input_str.replace(';','')
   
        input_id = self._match_project_exact(input_str)
        if input_id: return (input_id,'project')
            
        input_id = self._match_backer_exact(input_str)
        if input_id: return (input_id,'backer')     
            
        input_id = self._match_project_regexp(input_str)
        if input_id: return (input_id,'project')
        
        input_id = self._match_backer_regexp(input_str)
        if input_id: return (input_id,'backer')

        return (None,None)
     
    def _match_project_exact(self,input_str):
        result = self.project_sql.extract_single('idprojects','name',input_str,added_clause = 'LIMIT 1')
        if result:
            return result
        else:
            return None
    
    def _match_project_regexp(self,input_str):
        result = self.project_sql.extract_all('idprojects',"WHERE name LIKE '%%%s%%' LIMIT 1" % input_str)
    
        if result:
            return result[0][0]
        else:
            return None
        
    def _match_backer_exact(self,input_str):
        result = self.backer_sql.extract_single('idbackers','name',input_str,added_clause = 'LIMIT 1')
        if result:
            return result
        else:
            return None
            
    def _match_backer_regexp(self,input_str):
        result = self.backer_sql.extract_all('idbackers',"WHERE name LIKE '%%%s%%' LIMIT 1" % input_str)
        if result:
            return result[0][0]
        else:
            return None
            
            
class OutputHandler():
    
    def __init__(self):
        self.project_sql = kfs.project_graph_tbl
        self.backer_sql = kfs.backer_graph_tbl  
        self.database_convert = dbc.DBconverter()
        self.base_url = kfs.base_url

    def process_output(self,output_ids,output_type):
        if not output_ids: return None
        
        if output_type == 'project':
            results = self._extract_project_info(output_ids)
        elif output_type == 'backer':
            results = self._extract_backer_info(output_ids)
        else:
            return None
            
        if not results: return None  
        return results

    def _extract_project_info(self,output_ids):
        results = self.database_convert.website_info_from_proj_ids(output_ids)    

        for ind,result in enumerate(results):
            results[ind]['url'] = kfs.base_url + results[ind]['url']
            results[ind]['type'] = 'project'

            if results[ind]['prediction']:
                results[ind]['prediction_number'] ='%.0f' % (results[ind]['prediction']*100)                
                
                if results[ind]['prediction'] > 0.9:
                    results[ind]['prediction'] = '>90'
                elif results[ind]['prediction'] < 0.1:
                    results[ind]['prediction'] = '<10'
                else:
                    results[ind]['prediction'] = '%.0f' % (results[ind]['prediction']*100)
                
                
#                results[ind]['prediction'] = '%.0f' % (results[ind]['prediction']*100)

        if not results: return None               
        return results

    def _extract_backer_info(self,output_ids):
        results = self.database_convert.website_info_from_backer_ids(output_ids) 

        if not results: return None               
        return results  
        
        
    
if __name__ == '__main__':
    input_handler = InputHandler()      
    output_handler = OutputHandler()    
    id1,type1 = input_handler.process_input('Mike Gr')
    id2,type2 = input_handler.process_input('Megac')
    id3,type3 = input_handler.process_input('This string is not in the database. asdhjgfha')
    
    res1 = output_handler.process_output(id1,type1)
    res2 = output_handler.process_output(id2,type2)
    res3 = output_handler.process_output(id3,type3)