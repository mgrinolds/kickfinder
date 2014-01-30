# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 15:36:49 2014

@author: Mike
"""

import numpy.random as random
import kickfinder_settings as kfs
import time
from collections import OrderedDict
from math import ceil
import bs4 as BeautifulSoup

class ProjectFinder:  
    def __init__(self):
        self.sql = kfs.project_html_tbl
        self.session = kfs.session
        
        self.base_url = kfs.base_url
        self.sleep_time = kfs.sleep_time
        
    def add_project_names(self,links):
        for link in links:
            row_dict = put_project_raw_new(link)
            self.sql.add_row(row_dict)
            
    def get_project_html(self,start_at=None):
        links = self.sql.extract_all('url',"WHERE html IS NULL")
        
        if start_at:
            links = links[start_at:]        
        
        print len(links)
        for ind,link in enumerate(links):
            print (ind,self.url + link)

            html = pull_html(self.session,self.url + link)  
            self.sql.update_value('html',html,'url',link)    
            sleep_random(self.sleep_time)
            

class DiscoveryScraper:
    
    def __init__(self):
        self.sql = kfs.project_html_tbl     
        self.session = kfs.session

        self.url = kfs.base_url
        self.sleep_time = kfs.sleep_time

    def scrape_single(self,iterInd=0):   
        html = pull_html(self.session,self.url + '/discover/advanced?page=%d&sort=popularity' \
             % iterInd) 
 
        links = get_links(html)
        project_links = get_project_links(links)     
        
        for link in project_links:
            row_dict = put_project_raw(link)    
            add_row_ignore_duplicates(self.sql,row_dict)
        
    def scrape_range(self,min_ind,max_ind):
        min_ind = max(0,min_ind)
        max_ind = min(len(self.iter_vals),max_ind)
        max_ind = max(min_ind,max_ind)
        
        print (min_ind,max_ind)        
        
        for ind in range(min_ind,max_ind):
            print ind
            self.scrape_single(ind)  
            sleep_random(self.sleep_time)    
    
    def scrape_html_from_db(self):
        links_without_html = self.sql.extract_all('name',\
            "WHERE html IS NULL")
            
        grab_links = links_without_html

        print len(grab_links)
        for ind,link in enumerate(grab_links):
            print (ind,link)
            
            html = pull_html(self.session,self.url + link)  

            self.sql.update_value('html',html,'name',link)    
            self.sql.update_value('html_exists',1,'name',link)     
    
            sleep_random(self.sleep_time)        
     

class BackerFinder:
    def __init__(self):     
        self.project_sql = kfs.project_html_tbl
        self.backer_sql = kfs.backer_html_tbl
        
        self.session = kfs.session      
        
        self.url = kfs.base_url      
        self.sleep_time = kfs.sleep_time

        self.project_url = '%s/backers?cursor=%s'
        self.profile_url = '%s?page=%d&'
        
    def setup_seeders(self,profile_ids):
        for id in profile_ids:
            backer_link = '/profile/%d' % id
            row_dict = put_backer_raw('',backer_link,seed=1)              
            add_row_ignore_duplicates(self.backer_sql,row_dict)    
       
    def scrape_from_projects(self,maxsearch=None,startfrom=0):
        all_projects = self.project_sql.extract_all('name')
        used_projects = self.backer_sql.extract_all('discovered_from')

        unused_projects = [x for x in all_projects if x not in used_projects]        
        unused_projects = filter(None,unused_projects)        
        
        #unique elements - presevers order
        unused_projects = list(OrderedDict.fromkeys(unused_projects))        
        unused_projects = unused_projects[startfrom:]

        print ('total:',len(unused_projects))

        for ind,full_url in enumerate(unused_projects):
            
            no_ref_link = full_url.split('?')[0]
            print ('project:',ind,no_ref_link)
            
            try:
                self.scrape_single_project(no_ref_link,full_url)
            except:
                pass
            
            if maxsearch and ind > maxsearch:
                break

    
    def scrape_single_project(self,project_link,discovery_link):
        seeders = self.backer_sql.extract_all('profile_link','WHERE seed_for_user_search=1')

        add_profiles = []
        add_num_backed = []
        for ind,seed in enumerate(seeders):
            url = self.url + self.project_url % (project_link,seed.split('/')[-1])
            print ('----page:',project_link,ind,url)

            html = pull_html(self.session,url)  
            
            profile_links, num_projects_backed = get_backer_link_and_numbers(html)
            
            n_prev_profiles = len(set(add_profiles))            
            
            add_profiles += profile_links            
            add_num_backed += num_projects_backed            
            
            sleep_random(self.sleep_time)        
    
            print ('n_prev_profiles',n_prev_profiles)
    
            if not len(add_num_backed) or n_prev_profiles == len(set(add_profiles)):
                break

        unique_entries = 0
    
        for backer,num in zip(add_profiles,add_num_backed):
            row_dict = put_backer_raw('',backer,seed=0,num_projects=num,discovered_link=discovery_link)            
            add_row_ignore_duplicates(self.backer_sql,row_dict)  
    
        print ('total_entries',len(set(add_profiles)),'unique_entries',unique_entries)    
        return (add_profiles,add_num_backed) 
  
    def scrape_html_from_db(self,num_proj_thresh=0):
        links_without_html = self.backer_sql.extract_all('profile_link',\
            "WHERE has_projects = 0 AND num_projects > %s" % num_proj_thresh)
            
        num_projects = self.backer_sql.extract_all('num_projects',\
            "WHERE has_projects = 0 AND num_projects > %s" % num_proj_thresh) 
             
        links_per_page = 32.  
    
        num_pages = [int(ceil(page/links_per_page)) for page in num_projects]     
        
        grab_links = links_without_html
        for ind,link in enumerate(grab_links):
            project_links = []
            for sub_ind in range(num_pages[ind]):
                url = self.profile_url % (link,sub_ind + 1)
                
                html = pull_html(self.session,url)  
                            
                if sub_ind == 0:
                    self.backer_sql.update_value('profile_html',html,'profile_link',link)    
                    self.backer_sql.update_value('has_html',1,'profile_link',link)    
                
                n_prev_profiles = len(set(project_links))                   
                
                project_links += get_project_links(get_links(html))
                
                sleep_random(self.sleep_time)        
                
                print ('-------',ind,sub_ind,url,n_prev_profiles)               
                
                if len(set(project_links)) == n_prev_profiles:
                    break
  
            self.backer_sql.update_value('projects',str(list(OrderedDict.fromkeys(project_links))),'profile_link',link)    
            self.backer_sql.update_value('has_projects',1,'profile_link',link) 
            
            print ('----num_found_projects',len(set(project_links)),\
                'num_backed',num_projects[ind]) 
                
                
def pull_html(session,url):
    html = None
    while not html:
        try:
            pull = session.get(url)
        except:
            time.sleep(120)
            print 'pull error'   
    
        html = pull.text.encode('ascii','ignore') 
    return html

def sleep_random(sleep_time):
    sleep_time = sleep_time/10 + sleep_time*random.rand()
    print sleep_time
    time.sleep(sleep_time)  
    
def add_row_ignore_duplicates(sql_table,row_dict):
    try:    
        sql_table.add_row(row_dict)
    except Exception as e:
        if 'Duplicate' in e.args[1]:
            pass
        else:
            raise e
            
def get_links(html):
    soup = BeautifulSoup(html)
    
    all_links = [link.get('href') for link in soup.find_all('a')]
    return all_links

def get_backer_link_and_numbers(html):
    soup = BeautifulSoup(html)    

    backer_data = soup.find_all('div',{'class' : 'NS_backers__backing_row'})
    
    backer_links = []
    num_backed = []
    for data in backer_data:

        backer_links.append(get_profile_links(get_links(str(data)))[0])
        try:   
            num_backed.append(get_num_projects_backed(str(data))[0])
        except:
            num_backed.append(0)    
        
    return (backer_links,num_backed)

def get_num_projects_backed(html):

    soup = BeautifulSoup(html)
    p_found = soup.find_all('p', {'class' : 'backings'})

    num_projects = [0]*len(p_found)
    for ind,p in enumerate(p_found):
        num_projects[ind] = int(''.join(x for x in str(p) if x.isdigit()))
        
    return num_projects

def get_project_links(links):
    prefix = '/projects'
    
    links = filter(None, links)    
    project_links = list(set([s for s in links if prefix in s]))
    return project_links
    
def get_profile_links(links):
    prefix = '/profile'
    
    links = filter(None,links)
    profile_links = list(set([s for s in links if prefix in s]))
    return profile_links 
   
def put_project_raw_new(link,html=None,name=None,num_backers=None,funded=None):
    
    row_dict = {'url':link,'name':name,'html':html}
    return row_dict
   
   
def put_project_raw(link,html=None):
        
    if html:
        row_dict = {'name':link,'html':html,'html_exists':1}
    else:
        row_dict = {'name':link,'html':None,'html_exists':0}            
        
    return row_dict
    
def put_backer_raw(name,link,seed=0,num_projects=0,discovered_link=None,project_links=None,html=None):
    
    row_dict = {'name':name,'profile_link':link,'seed_for_user_search':seed,\
        'num_projects':num_projects,'discovered_from':discovered_link}

    if project_links:
        row_dict['has_projects'] = 1
        row_dict['projects'] = project_links
    else:
        row_dict['has_projects'] = 0
        row_dict['projects'] = None
        
    if html:
        row_dict['has_html'] = 1
        row_dict['profile_html'] = html
    else:
        row_dict['has_projects'] = 0
        row_dict['profile_html'] = None
        
    return row_dict            
        
if __name__ == '__main__': 
#    con = mdb.connect('localhost', 'mgrinolds',pw.get_pw(), 'nvafm_scan')  
    sc = DiscoveryScraper()
    bf = BackerFinder()
    pf = ProjectFinder()
#    bf.parse_html()
#    bf.scrape_from_projects(100000,1600)
#    bf.scrape_html_from_db(25)
#    pf.get_project_html()