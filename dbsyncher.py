# -*- coding: utf-8 -*-
"""
Created on Sat Feb 01 17:56:09 2014

@author: Mike
"""

import kickfinder_settings as kfs

class DBsyncher():
    def __init__(self):
        self.backer_html = kfs.backer_graph_tbl
        self.project_html = kfs.project_graph_tbl
        
        self.backer_graph = kfs.backer_graph_tbl
        self.project_graph = kfs.project_graph_tbl
        
        self.backer_byname = kfs.backer_byname_tbl
        self.project_byname = kfs.project_byname_tbl
        
        self.backer_graph_cols = """idbackers,
                                    name,
                                    seed_for_user_search,
                                    has_projects,
                                    num_projects,
                                    projects,
                                    discovered_from,
                                    image_url,
                                    description,
                                    projects_inds,
                                    validated_found,
                                    validated_tried,
                                    validated_baseline"""
                                    
        self.project_graph_cols = """idprojects,
                                     url,
                                     name,
                                     first_backed,
                                     currency,
                                     hours_remaining,
                                     ncomments,
                                     nexternal_links,
                                     category,
                                     goal,
                                     connected_facebook,
                                     pledged,
                                     has_video,
                                     project_duration,
                                     latitude,
                                     body_length,
                                     description,
                                     nbackers,
                                     nrewards,
                                     npictures,
                                     percent_raised,
                                     longitude,
                                     image_url,
                                     nupdates,
                                     first_created,
                                     prediction,
                                     r0_10,
                                     r10_25,
                                     r25_40,
                                     r40_60,
                                     r60_100,
                                     r100_200,
                                     r200_500
                                     r500,
                                     nquestions,
                                     nlimited_rewards,
                                     has_website,
                                     website_length,
                                     website_link"""
                                    
        self.backer_byname_cols = "name,idbackers"
        self.project_byname_cols = "name,idprojects"
        
        
    def add_backers_from_html_to_graph(self,links=None):
        if links:
            db_info = self.backer_html.extract_all_manycols(self.backer_graph_cols,
                            'profile_link',links,return_type='dict')
        else:
            db_info = self.backer_html.extract_all_manycols(self.backer_graph_cols,return_type='dict')      
       
        for row_dict in db_info:
            add_row_ignore_duplicates(self.backer_graph,row_dict)
    
    def add_projects_from_html_to_graph(self,links=None):
        if links:
            db_info = self.project_html.extract_all_manycols(self.project_graph_cols,
                            'url',links,return_type='dict')
        else:
            db_info = self.project_html.extract_all_manycols(self.project_graph_cols,return_type='dict')      
       
        for row_dict in db_info:
            add_row_ignore_duplicates(self.project_graph,row_dict)
        
    def add_backers_from_graph_to_byname(self,links=None):
        if links:
            db_info = self.backer_graph.extract_all_manycols(self.backer_byname_cols,
                            'profile_link',links,return_type='dict')
        else:
            db_info = self.backer_graph.extract_all_manycols(self.backer_byname_cols,return_type='dict')      
       
        for row_dict in db_info:
            add_row_ignore_duplicates(self.backer_byname,row_dict)
    
    def add_projects_from_graph_to_byname(self,links=None):
        if links:
            db_info = self.project_graph.extract_all_manycols(self.project_byname_cols,
                            'url',links,return_type='dict')
        else:
            db_info = self.project_graph.extract_all_manycols(self.project_byname_cols,return_type='dict')      
       
        for row_dict in db_info:
            add_row_ignore_duplicates(self.project_byname,row_dict)
    
def add_row_ignore_duplicates(sql_table,row_dict):
    try:    
        sql_table.add_row(row_dict)
    except Exception as e:
        if 'Duplicate' in e.args[1]:          
            return False
        else:
            raise e
    
    return True
    
if __name__ == '__main__':
    dbs = DBsyncher()
    
    dbs.add_backers_from_html_to_graph(['/profile/554880439'])
    dbs.add_projects_from_html_to_graph(['//projects/jbmovies/amnesia-tv-show-series'])
    dbs.add_backers_from_graph_to_byname(['/profile/554880439'])
    dbs.add_projects_from_graph_to_byname(['//projects/jbmovies/amnesia-tv-show-series'])