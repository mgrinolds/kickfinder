# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 16:14:28 2014

@author: Mike
"""

import kickfinder_settings as kfs
from bs4 import BeautifulSoup

class BackerParser:
    def __init__(self):
        self.html_sql = kfs.backer_html_tbl        
        self.graph_sql = kfs.backer_graph_tbl
        
        self.project_graph = kfs.project_graph_tbl
        
    def parse_html_all(self,start_at=None):      
        urls = self.html_sql('profile_link',"WHERE html IS NOT NULL")
        htmls = self.html_sql('profile_html',"WHERE html IS NOT NULL")
        
        if start_at:
            htmls = htmls[start_at:]
        
        print len(htmls)
        for ind,html in enumerate(htmls):
            print (ind)

            parsed_dict = self._parse_project_html(html)
        
            if not parsed_dict:
                continue
        
            col_names = parsed_dict.keys()
            col_values = [parsed_dict[name][0] for name in col_names]
                
            for (name,value) in zip(col_names,col_values):
                self.graph_sql.update_value_numeric_key(name,value,'profile_link',urls[ind]) 
    
    def parse_unparsed_html(self):
        ids = self.html_sql.extract_all_manycols('idbackers',\
            added_clause="WHERE profile_html IS NOT NULL AND description IS NULL")
            
        self.parse_html_from_ids(ids)
    
    def parse_html_from_links(self,links):
        ids = self.html_sql.extract_all_manycols('idbackers','profile_link',links)
        
        self.parse_html_from_ids(ids)
          
    def parse_html_from_ids(self,ids):
        print len(ids)
        for ind,id_value in enumerate(ids):
            id_value = id_value[0]
            print (ind,id_value)           
            
            html = self.html_sql.extract_single('profile_html','idbackers',id_value)
            
            if not html:
                print 'did not find id: ' + str(id)
                continue
            
            parsed_dict = self._parse_backer_html(html)
            
            if not parsed_dict:
                print 'could not parse html: ' + str(id)
                continue
            
            col_names = parsed_dict.keys()
            col_values = [parsed_dict[name][0] for name in col_names]
                
            for (name,value) in zip(col_names,col_values):
                print (name,value)
                self.graph_sql.update_value_numeric_key(name,value,'idbackers',id_value) 
            
                
    def convert_links_to_ids(self,links=None):
        
        if not links:
            db_info = self.graph_sql.extract_all_manycols('idbackers, projects',\
                added_clause="WHERE projects IS NOT NULL")
        else:
            db_info = self.graph_sql.extract_all_manycols('idbackers, projects',\
                'profile_link',links,added_clause="AND projects IS NOT NULL")    

        project_list = []
        for ind_id, ind_projects in db_info:
            print (ind_id)
            project_list = eval(ind_projects)
            
            projects_by_ind = []
            for link in project_list:
                ind = self.project_graph.extract_all('idprojects',\
                    "WHERE url = '%s'" % link)

                if ind:
                    projects_by_ind.append(ind[0][0])                    
                
            project_inds = str(projects_by_ind)
            
            if len(project_inds):
                self.graph_sql.update_value_numeric_key('projects_inds',project_inds,'idbackers',ind_id) 
  
    def _parse_backer_html(self,html):
        soup = BeautifulSoup(html)    
    
        try:    
            name = soup.find("meta", {"property":"og:title"})['content']       
            image_url = soup.find("meta", {"property":"og:image"})['content']
            description = soup.find("meta", {"property":"og:description"})['content']
        except Exception as e:
            print e.args[0]
            return None
            
        out_dict = dict()  
        
        out_dict['name'] = (name,'VARCHAR(200)')
        out_dict['image_url'] = (image_url,'VARCHAR(200)')
        out_dict['description'] = (description[:200],'TEXT')
        
        return out_dict
        
class ProjectParser:
    def __init__(self):
        self.html_sql = kfs.project_html_tbl        
        self.graph_sql = kfs.project_graph_tbl
        
    def parse_html_all(self,start_at=None):      
        urls = self.html_sql('url',"WHERE html IS NOT NULL")
        htmls = self.html_sql('html',"WHERE html IS NOT NULL")
        
        if start_at:
            htmls = htmls[start_at:]
        
        print len(htmls)
        for ind,html in enumerate(htmls):
            print (ind)

            parsed_dict = self._parse_project_html(html)
        
            if not parsed_dict:
                continue
        
            col_names = parsed_dict.keys()
            col_values = [parsed_dict[name][0] for name in col_names]
                
            for (name,value) in zip(col_names,col_values):
                self.graph_sql.update_value(name,value,'url',urls[ind]) 
    
    def parse_unparsed_html(self):
        ids = self.html_sql.extract_all_manycols('idprojects',\
            added_clause="WHERE html IS NOT NULL AND description IS NULL")
            
        self.parse_html_from_ids(ids)
    
    def parse_html_from_links(self,links):
        ids = self.html_sql.extract_all_manycols('idprojects','url',links)
        
        self.parse_html_from_ids(ids)
          
    def parse_html_from_ids(self,ids):
        print len(ids)
        for ind,id_value in enumerate(ids):
            id_value = id_value[0]
            print (ind,id_value)           
            
            html = self.html_sql.extract_single('html','idprojects',id_value)
            
            if not html:
                print 'did not find id: ' + str(id)
                continue
            
            parsed_dict = self._parse_project_html(html)
            
            if not parsed_dict:
                print 'could not parse html: ' + str(id)
                continue
            
            col_names = parsed_dict.keys()
            col_values = [parsed_dict[name][0] for name in col_names]
                
            for (name,value) in zip(col_names,col_values):
                self.graph_sql.update_value_numeric_key(name,value,'idprojects',id_value) 

    def _parse_project_html(self,html):
        soup = BeautifulSoup(html)
        
        try:    
            name = soup.find("meta", {"property":"og:title"})['content']
            
            image_url = soup.find("meta", {"property":"og:image"})['content']
            description = soup.find("meta", {"property":"og:description"})['content']
            
            latitude = float(soup.find("meta", {"property":"kickstarter:location:latitude"})['content'])
            longitude = float(soup.find("meta", {"property":"kickstarter:location:latitude"})['content'])
            
            pledged = float(soup.find('div',{'id':'pledged'})['data-pledged'])
            goal = float(soup.find('div',{'id':'pledged'})['data-goal'])
            percent_raised = float(soup.find('div',{'id':'pledged'})['data-percent-raised'])
            currency = soup.find('data',{'itemprop':'Project[pledged]'})['data-currency']
            
        #    delivery_date = soup.find('time')['datetime'] 
        #    end_date_str = soup.find('span',{"id":"project_duration_data"})['data-end_time']   
        #    end_date = datetime.strptime(end_date[5:-15],'%d %b %Y')
            
            hours_remaining = float(soup.find('span',{"id":"project_duration_data"})['data-hours-remaining'])
            project_duration = float(soup.find('span',{"id":"project_duration_data"})['data-duration'])  
            
            video = soup.find("meta", {"property":"og:video"})    
            
            category = soup.find("li", {"class":"category"})['data-project-parent-category']
            
            body = BeautifulSoup(str(soup.find_all('div',{"class":"full-description"})))  
            npictures = body.find_all('figure').__len__()    
            
            external_links = [link.get('href') for link in body.find_all('a')]    
            body_length = soup.find('div',{"class":"full-description"}).getText().__len__()
            
            other_projects = BeautifulSoup(str(soup.find_all("li", {"class":"projects"})))
            other_projects_string = other_projects.text
            
            website = soup.find('a',{'class':'popup'}).getText()        
            
            if website and (not 'facebook' in website):
                has_website = 1
                website_length = len(website)
            else:
                website_length = len(website)
                has_website = 0
            
            
            if 'First created' in other_projects_string:
                first_created = True
            else:
                first_created = False
                
            if '0 backed' in other_projects_string:
                first_backed = True
            else:
                first_backed = False
            
            facebook = BeautifulSoup(str(soup.find_all("li", {"class":"facebook"}))) 
            connected_facebook = not "Has not connected Facebook" in facebook.text
        
            nbackers = int(soup.find('data',{'itemprop':'Project[backers_count]'}).getText().replace(',', ''))
            ncomments = int(soup.find('data',{'itemprop':'Project[comments_count]'}).getText().replace(',', ''))
            nupdates = int(soup.find('span',{'id':'updates_count'})['data-updates-count'].replace(',', ''))   
                     
            rewards = soup.find_all('li',{"class":"NS-projects-reward"})
            reward_soup = BeautifulSoup(str(rewards))
            
            nlimited_rewards = reward_soup.find_all('span',{'class':'limited-number'}).__len__()
            
            reward_list = reward_soup.find_all('span',{'class':'money'})
            reward_str = [item.getText() for item in reward_list]
            reward_vals = [float(item[1:].replace(',','')) for item in reward_str]
                
            nquestions = soup.find_all('span',{'class':'question'}).__len__()
        
        except Exception as e:
            print e.args[0]
            return None
        
    
        out_dict = dict()  
        
        out_dict['name'] = (name,'VARCHAR(200)')
        out_dict['image_url'] = (image_url,'VARCHAR(200)')
        out_dict['description'] = (description,'TEXT')
        out_dict['latitude'] = (latitude,'DOUBLE')
        out_dict['longitude']= (longitude,'DOUBLE')
        
        out_dict['pledged'] = (pledged,'DOUBLE')
        out_dict['goal'] = (goal,'DOUBLE')
        out_dict['percent_raised'] = (percent_raised,'FLOAT')
        
        if currency == 'USD':
            out_dict['currency'] = (0,'INT')   
        elif currency == 'CAD':
            out_dict['currency'] = (1,'INT')  
        elif currency =='GPB':
            out_dict['currency'] = (2,'INT')    
        elif currency == 'AUD':
            out_dict['currency'] = (3,'INT')   
        elif currency == 'NZD':
            out_dict['currency'] = (4,'INT')    
        else:
            out_dict['currency'] = (5,'INT')    
            
    #    out_dict['currency'] = (currency,'VARCHAR(45)')    
        
        out_dict['hours_remaining'] = (hours_remaining,'FLOAT')
        out_dict['project_duration'] = (project_duration,'FLOAT')
        
        out_dict['first_created'] = (first_created,'INT')
        out_dict['first_backed'] = (first_backed,'INT')
        
        out_dict['category'] = (category,'VARCHAR(45)')
        out_dict['nexternal_links'] = (len(external_links),'INT')
        out_dict['body_length'] = (body_length,'DOUBLE')
        out_dict['connected_facebook'] = (connected_facebook,'INT')
        out_dict['nrewards'] = (len(rewards),'INT')
        out_dict['has_video'] = (bool(video),'INT')
        out_dict['nbackers'] = (nbackers,'INT')
        out_dict['ncomments'] = (ncomments,'INT')
        out_dict['npictures'] = (npictures,'INT')
        out_dict['nupdates'] = (nupdates,'INT')
        

        out_dict['nlimited_rewards'] = (nlimited_rewards,'INT')
        out_dict['nquestions'] = (nquestions,'INT')
      
        out_dict['website_link'] = (website,'VARCHAR(200)')
      
        out_dict['has_website'] = (has_website,'INT')
        out_dict['website_length'] = (website_length,'INT')
        
        
        out_dict['r0_10'] = (sum([int(0 < item <= 10) for item in reward_vals]),'INT')
        out_dict['r10_25'] = (sum([int(10 < item <= 25) for item in reward_vals]),'INT')
        out_dict['r25_40'] = (sum([int(25 < item <= 40) for item in reward_vals]),'INT')
        out_dict['r40_60'] = (sum([int(40 < item <= 60) for item in reward_vals]),'INT')
        out_dict['r60_100'] = (sum([int(60 < item <= 100) for item in reward_vals]),'INT')
        out_dict['r100_200'] = (sum([int(100 < item <= 200) for item in reward_vals]),'INT')
        out_dict['r200_500'] = (sum([int(200 < item <= 500) for item in reward_vals]),'INT')    
        out_dict['r500'] = (sum([int(500 < item) for item in reward_vals]),'INT')  
        
        out_dict['prediction'] = (None,'DOUBLE')    
        
        return out_dict
        
if __name__ == '__main__':

    bp = BackerParser()
    
    a = bp.convert_links_to_ids()