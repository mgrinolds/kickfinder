# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 22:16:26 2014

@author: Mike
"""
import kickfinder_settings as kfs
import scraper

class AutoScraper():
    
    def __init__(self):
        self.project_discoverer = scraper.DiscoveryScraper()
        self.backer_finder = scraper.BackerFinder()
        self.project_finder = scraper.ProjectFinder()
        
        self.current_step = None
        self.project_names = None
        self.backer_names = None
    
    def error_handler(self):
        
    def save_to_pickle(self):
        
    def load_to_pickle(self):
     
    def find_recent_projects(self):

    def find_backers(self,project_names):

    def scrape_backers(self,backer_names):
     
    def scrape_projects(self,project_names): 
     
    def parse_backers(self,backer_names):
        
    def parse_projects(self,project_names):
    
    def update_project_graph_db(self,project_names):
        
    def update_backer_graph_db(self,backer_names):
        
    def update_project_byname_db(self,project_names):
        
    def update_backer_byname_db(self,project_names):