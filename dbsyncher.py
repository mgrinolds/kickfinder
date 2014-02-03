# -*- coding: utf-8 -*-
"""
Created on Sat Feb 01 17:56:09 2014

@author: Mike
"""

import kickfinder_settings as kfs

class DBsyncher():
    def __init__(self):
        self.backer_html = kfs.backer_html_tbl
        self.project_html = kfs.project_html_tbl
        
        self.backer_graph = kfs.backer_graph_tbl
        self.project_graph = kfs.project_graph_tbl
        
        self.backer_byname = kfs.backer_byname_tbl
        self.project_byname = kfs.project_byname_tbl
        
        self.backer_graph_cols = """idbackers,
                                    name,
                                    profile_link,
                                    seed_for_user_search,
                                    has_projects,
                                    num_projects,
                                    projects,
                                    discovered_from,
                                    image_url,
                                    description"""
                                    
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
     
        nadded = 0
        for row_dict in db_info:
            was_added = add_row_ignore_duplicates(self.backer_graph,row_dict)
            
            if was_added:
                nadded += 1
                
        print 'number of items_added: %d (out of %d)' % (nadded, len(db_info))
    
    def add_projects_from_html_to_graph(self,links=None):      
        if links:
            db_info = self.project_html.extract_all_manycols(self.project_graph_cols,
                            'url',links,return_type='dict')
        else:
            db_info = self.project_html.extract_all_manycols(self.project_graph_cols,return_type='dict')      
        
        nadded = 0
        for row_dict in db_info:
            was_added = add_row_ignore_duplicates(self.project_graph,row_dict)
            
            if was_added:
                nadded += 1
                
        print 'number of items_added: %d (out of %d)' % (nadded, len(db_info))
        
    def add_backers_from_graph_to_byname(self,links=None):
        if links:
            db_info = self.backer_graph.extract_all_manycols(self.backer_byname_cols,
                            'profile_link',links,return_type='dict')
        else:
            db_info = self.backer_graph.extract_all_manycols(self.backer_byname_cols,return_type='dict')      
       
        nadded = 0
        
        for row_dict in db_info:
            was_added = add_row_ignore_duplicates(self.backer_byname,row_dict)
            
            if was_added:
                nadded += 1
                
        print 'number of items_added: %d (out of %d)' % (nadded, len(db_info))
    
    def add_projects_from_graph_to_byname(self,links=None):
        if links:
            db_info = self.project_graph.extract_all_manycols(self.project_byname_cols,
                            'url',links,return_type='dict')
        else:
            db_info = self.project_graph.extract_all_manycols(self.project_byname_cols,return_type='dict')      
        
        nadded = 0
        for row_dict in db_info:
            was_added = add_row_ignore_duplicates(self.project_byname,row_dict)
            
            if was_added:
                nadded += 1
                
        print 'number of items_added: %d (out of %d)' % (nadded, len(db_info))
    
def add_row_ignore_duplicates(sql_table,row_dict):
    try:    
        sql_table.add_row(row_dict)
    except Exception as e:
        if 'Duplicate' in e.args[1]: 
            return False
        else:
            print 'unhandled exception in adding row'
            raise e
    
    return True
    
if __name__ == '__main__':
    dbs = DBsyncher()

    profile_list = ['/profile/16932040', '/profile/1803973224', '/profile/704122876', '/profile/1453428300', '/profile/99348026', '/profile/1221227613', '/profile/1929265448', '/profile/1089603846', '/profile/1842553552', '/profile/919767357', '/profile/1583957315', '/profile/1237753022', '/profile/889474712', '/profile/43336738', '/profile/1291093065', '/profile/1694374051', '/profile/428658332', '/profile/1632133265', '/profile/1924420385', '/profile/609705246', '/profile/779003908', '/profile/1701774094', '/profile/1268527785', '/profile/742440860', '/profile/1157414967', '/profile/2117860457', '/profile/1384229546', '/profile/1798609905', '/profile/9633548', '/profile/609397589', '/profile/1750666460', '/profile/1993517269', '/profile/512397762', '/profile/1875460750', '/profile/366710114', '/profile/307469224', '/profile/1123951701', '/profile/1364637240', '/profile/1217296661', '/profile/935907788', '/profile/1536798379', '/profile/289627094', '/profile/961255302', '/profile/2091057356', '/profile/paperseedtree', '/profile/278568979', '/profile/1775198947', '/profile/1220278452', '/profile/2103372143', '/profile/736631914', '/profile/1046385297', '/profile/177204560', '/profile/165147529', '/profile/1656511998', '/profile/876814160', '/profile/191870660', '/profile/1231993568', '/profile/1332158474', '/profile/1723146242', '/profile/779894014', '/profile/1494751096', '/profile/1808368265', '/profile/1595965150', '/profile/519330292', '/profile/981886800', '/profile/851191755', '/profile/359231459', '/profile/1838584047', '/profile/1933436069', '/profile/1042985078', '/profile/789647240', '/profile/1078474807', '/profile/681441930', '/profile/1641322430', '/profile/443065469', '/profile/178157311', '/profile/182829170', '/profile/1795894899', '/profile/619809786', '/profile/1386054764', '/profile/695980231', '/profile/1247615320', '/profile/874353858', '/profile/1558513859', '/profile/704007946', '/profile/1464613517', '/profile/832210434', '/profile/2109128327', '/profile/1510150042', '/profile/2070170040', '/profile/1082817999', '/profile/ginacarli', '/profile/1440171360', '/profile/737025000', '/profile/1557055557', '/profile/683385567']
    
    dbs.add_backers_from_html_to_graph(profile_list)
#    dbs.add_backers_from_html_to_graph(['/profile/554880439','/profile/1042985078'])
        
    
#    dbs.add_projects_from_html_to_graph(['//projects/jbmovies/amnesia-tv-show-series'])
#    dbs.add_backers_from_graph_to_byname(['/profile/554880439'])
#    dbs.add_projects_from_graph_to_byname(['//projects/jbmovies/amnesia-tv-show-series'])