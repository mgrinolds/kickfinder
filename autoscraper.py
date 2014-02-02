# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 22:16:26 2014

@author: Mike
"""
import kickfinder_settings as kfs
import scraper 
import htmlparser
import dbsyncher
import cPickle

class AutoScraper():
    
    def __init__(self):
        self.project_discoverer = scraper.DiscoveryScraper()
        self.backer_finder = scraper.BackerFinder()
        self.project_finder = scraper.ProjectFinder()
        
        self.projct_parser = htmlparser.ProjectParser()
        self.backer_parser = htmlparser.BackerParser()
        
        self.syncher = dbsyncher.DBsyncher()
        
        self.pickle_filename = 'autoscrape_status.p'

        self.status = {}
        
        self._init_status()

    def autoscrape(self):
        
        self._find_recent_projects(0)
        self._find_backers()
        self._scrape_backers()
        self._scrape_projects()
        
        self._update_project_graph_db()
        self._update_backer_graph_db() 
        
        self._parse_projects()
        self._parse_backers()
        
        self._update_project_byname_db()
        self._update_backer_byname_db()   

        self._init_status()

    def _init_status(self):
        self.status['current_step'] = None
        self.status['current_vars'] = None
        self.status['project_ids'] = None
        self.status['project_links'] = None
        self.status['backer_ids'] = None
        self.status['backer_links'] = None

    def _find_recent_projects(self,npages):        
        self.status['current_step'] = '_find_recent_projects'
        self.status['current_vars'] = (npages,)
        discovered_projects = self.project_discoverer.scrape_range(1,npages)
        
        self.project_finder.add_project_names(discovered_projects)
        
        self.status['project_links'] = discovered_projects
        self.status['project_links'] = self.status['project_links']
        print self.status['project_links']
        
        self._save_to_pickle()       
        
    def _find_backers(self):
        self.status['current_step'] = '_find_backers'
        self.status['current_vars'] = None
        
        project_links = self.status['project_links']
        if project_links:        
            self.status['backer_links'] = \
                self.backer_finder.scrape_from_project_links(project_links)
        
            self.status['backer_links'] = self.status['backer_links']
            print self.status['backer_links']
        
        self._save_to_pickle()   
    
    def _scrape_backers(self):
        self.status['current_step'] = '_scrape_backers'
        self.status['current_vars'] = None
        
        backer_links = self.status['backer_links']

        if backer_links:
            discovered_projects = \
                self.backer_finder.scrape_html_from_backer_links(backer_links) 
  
            new_discovered_projects = \
                self.project_finder.add_project_names(discovered_projects)
                
            [self.status['project_links'].append(link) for link in new_discovered_projects]
        
        print self.status['project_links']
        
        self._save_to_pickle()   
    
    def _scrape_projects(self): 
        self.status['current_step'] = '_scrape_projects'
        self.status['current_vars'] = None
        
        project_links = self.status['project_links']
        if project_links:        
            self.project_finder.get_project_html_from_links(project_links)        
                
        self._save_to_pickle()  
    
    def _update_project_graph_db(self):
        self.status['current_step'] = '_update_project_graph_db'
        self.status['current_vars'] = None
        
        project_links = self.status['project_links']
        if project_links:        
            self.syncher.add_projects_from_html_to_graph(project_links)  
                
        self._save_to_pickle() 
    
    def _update_backer_graph_db(self):
        self.status['current_step'] = '_update_backer_graph_db'
        self.status['current_vars'] = None
        
        backer_links = self.status['backer_links']
        if backer_links:        
            self.syncher.add_backers_from_html_to_graph(backer_links)  
                
        self._save_to_pickle() 
    
    def _update_project_byname_db(self):
        self.status['current_step'] = '_update_project_byname_db'
        self.status['current_vars'] = None
        
        project_links = self.status['project_links']
        if project_links:        
            self.syncher.add_projects_from_graph_to_byname(project_links)
                
        self._save_to_pickle() 
        
    def _update_backer_byname_db(self):
        self.status['current_step'] = '_update_backer_byname_db'
        self.status['current_vars'] = None
        
        backer_links = self.status['backer_links']
        if backer_links:        
            self.syncher.add_backers_from_graph_to_byname(backer_links)  
                
        self._save_to_pickle() 
    
    def _parse_projects(self):
        self.status['current_step'] = '_parse_projects'
        self.status['current_vars'] = None    
        
        project_links = self.status['project_links']
        if project_links:        
            self.projct_parser.parse_html_from_links(project_links)

        
        self._save_to_pickle()  
    
    def _parse_backers(self):
        self.status['current_step'] = '_parse_backers'
        self.status['current_vars'] = None    
        
        backer_links = self.status['backer_links']
        if backer_links:
            self.backer_parser.parse_html_from_links(backer_links)
            self.backer_parser.convert_links_to_ids(backer_links)
        
        self._save_to_pickle()         


    def _error_handler(self):
        self._save_to_pickle()
        
    def _save_to_pickle(self):
        fid = open(self.pickle_filename, 'wb+')
        cPickle.dump(self.status,fid)
        fid.close()
        
    def _load_from_pickle(self):
        fid = open(self.pickle_filename, 'rb')
        self.status = cPickle.load(fid)
        fid.close()        
  

class DBMaintainer():
    
    def __init__(self):
        self.project_discoverer = scraper.DiscoveryScraper()
        self.backer_finder = scraper.BackerFinder()
        self.project_finder = scraper.ProjectFinder()    
    
    def get_all_project_html(self): 
        self.project_finder.get_project_html()
  
    
if __name__ == '__main__':
    asc = AutoScraper()
    asc.autoscrape()