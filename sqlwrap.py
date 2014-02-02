# -*- coding: utf-8 -*-
"""
Created on Thu Jan 09 08:37:03 2014

@author: Mike
"""
import get_pw as gp
import MySQLdb as mdb

class SqlTable:
    
    def __init__(self,con,table_name):
        self.con = con
        self.cur = None
        self.table_name = table_name
        self.result = None     
    
    def query(self,query_str,pass_tuple=None):
        with self.con:      
            self.cur = self.con.cursor()
            
            if pass_tuple:
                self.cur.execute(query_str,pass_tuple)
            else:
                self.cur.execute(query_str)
            
            return self.cur.fetchall()    
            
    def query_dict(self,query_str,pass_tuple=None):
        with self.con:      
            self.cur = self.con.cursor(mdb.cursors.DictCursor)
            
            if pass_tuple:
                self.cur.execute(query_str,pass_tuple)
            else:
                self.cur.execute(query_str)
            
            return self.cur.fetchall()  
    
    def table_exists(self):     
        sql_str = "SHOW TABLES LIKE '%s'" % self.table_name 
        result = self._write(sql_str)
        if result:
            return True
        else:
            return False    
    
    def col_exists(self,col_name):
        sql_str = "SHOW COLUMNS FROM %s LIKE '%s';"
        pass_tuple = (self.table_name,col_name)
        
        self._write(sql_str % pass_tuple)
        if self.result:
            return True
        else:
            return False
    
    def add_table(self,table_dict):  
        sql_str = "CREATE TABLE %s" % self.table_name
        sql_str = sql_str + ' ('
        
        for col_name,data_type in table_dict.iteritems():
            sql_str = sql_str + col_name + ' ' + data_type + ', '

        sql_str = sql_str[:-2]
        sql_str = sql_str + ')'           
        
        return self._write(sql_str) 

    def copy_table(self,new_table_name):
        sql_str = "CREATE TABLE %s LIKE %s" % (new_table_name,self.table_name)
        self._write(sql_str) 
        
        sql_str = "INSERT INTO %s SELECT * FROM %s" % (new_table_name,self.table_name)
        self._write(sql_str) 
        
        return SqlTable(self.con,new_table_name)           

    def add_col(self,col_names,col_types):
        for col_name,col_type in zip(col_names,col_types):
            sql_str = ''  
            pass_list = []
            if not self.col_exists(col_name):
                sql_str += "ALTER TABLE %s ADD COLUMN %s %s; "
                pass_list += (self.table_name,col_name,col_type)

            pass_tuple = tuple(pass_list)        
        
        return self._write(sql_str % pass_tuple)
                    
    def add_row(self,row_dict): 
        sql_str = "INSERT INTO %s" % self.table_name
        sql_str = sql_str + ' ('
        
        for key in row_dict.keys():
            sql_str = sql_str + key + ', '
            
        sql_str = sql_str[:-2] 
        sql_str = sql_str + ') VALUES ('
        
        pass_tuple = tuple(row_dict.values())
        for value in row_dict.values():
            sql_str = sql_str + '%s, '
            
        sql_str = sql_str[:-2] 
        sql_str = sql_str + ')'
        
        return self._write(sql_str,pass_tuple)
         
    def extract_single(self,ret_col_name,test_col_name,test_col_val,added_clause=None):
        sql_str = "SELECT %s FROM %s WHERE %s"\
            % (ret_col_name, self.table_name,test_col_name)
        sql_str += " = %s " 
        
        if added_clause:
            sql_str += added_clause

        pass_tuple = (test_col_val,)
        result = self._queryOneTuple(sql_str,pass_tuple)        
        if result:
            result = result[0]
        return result            
            
    def extract_row(self,col_name,row_value,condition_str=None):
        sql_str = "SELECT * FROM %s WHERE %s = '%s'"  % (self.table_name,col_name,row_value)  
        if condition_str: sql_str = sql_str + condition_str

        return self._queryOne(sql_str)
            
    def extract_all(self,col_name,condition_str='',as_list=False):
        sql_str = "SELECT %s FROM %s" %  (col_name, self.table_name)
        if condition_str: sql_str = sql_str + ' ' + condition_str
        
        if as_list:
            return self._queryAllList(sql_str)    
        else:
            return self._queryAllTuple(sql_str)
            
    def extract_all_manycols_noL(self,ret_col_names,sel_col_name=None,\
        sel_col_values=None,added_clause = None):    
        if (type(sel_col_values) is list) or (type(sel_col_values) is tuple):
            str_values = str(sel_col_values)[1:-1]    
            
        elif type(sel_col_values) is not str:
            str_values = str(sel_col_values)
        else: 
            str_values = sel_col_values
            
        str_values = str_values.replace('L','')
        
        if sel_col_values:         
            sql_str = "SELECT %s FROM %s WHERE %s IN (%s) "\
                % (ret_col_names, self.table_name, sel_col_name, str_values)
#            print sql_str
        else:
            sql_str = "SELECT %s FROM %s "\
                % (ret_col_names, self.table_name)
#            print sql_str
            
        if added_clause:
            sql_str += added_clause
#        return self._queryAllTuple(sql_str)   
        return self._queryAllDict(sql_str)
     
    def extract_all_manycols(self,ret_col_names,sel_col_name=None,sel_col_values=None,\
            added_clause = None,return_type='tuple'):    
        if (type(sel_col_values) is list) or (type(sel_col_values) is tuple):
            str_values = str(sel_col_values)[1:-1]

            if type(sel_col_values[0]) is long:
                str_values = str_values.replace('L','')
            
        elif type(sel_col_values) is not str:
            str_values = str(sel_col_values)
        else: 
            str_values = sel_col_values
        
        if sel_col_values:         
            sql_str = "SELECT %s FROM %s WHERE %s IN (%s) "\
                % (ret_col_names, self.table_name, sel_col_name, str_values)
#            print sql_str
        else:
            sql_str = "SELECT %s FROM %s "\
                % (ret_col_names, self.table_name)
#            print sql_str
            
        if added_clause:
            sql_str += added_clause
            
        if return_type == 'tuple':
            return self._queryAllTuple(sql_str)  
        else:
            return self._queryAllDict(sql_str)
    
    def update_value(self,update_col_name,update_col_value,search_col_name,search_col_value):
        sql_str_pre = "UPDATE %s SET %s = " % (self.table_name,update_col_name)
        sql_str_post = " WHERE %s = '%s'" % (search_col_name,search_col_value)
        sql_str = sql_str_pre + '%s' + sql_str_post
        
        pass_tuple = (update_col_value,)
        return self._write(sql_str,pass_tuple)
        
    def update_value_numeric_key(self,update_col_name,update_col_value,search_col_name,search_col_value):
        sql_str_pre = "UPDATE %s SET %s = " % (self.table_name,update_col_name)
        sql_str_post = " WHERE %s = %d" % (search_col_name,search_col_value)
        sql_str = sql_str_pre + '%s' + sql_str_post
        
        pass_tuple = (update_col_value,)
        return self._write(sql_str,pass_tuple)
    
    def _write(self,sql_str,pass_tuple=None):
        with self.con:   
            self.cur = self.con.cursor()    
            
            if pass_tuple:
#                print sql_str % pass_tuple
                return self.cur.execute(sql_str,pass_tuple)
            else:
#                print sql_str
                return self.cur.execute(sql_str)
        
    def _queryOne(self,sql_str,pass_tuple=None):
        with self.con:
            self.cur = self.con.cursor(mdb.cursors.DictCursor)
            if pass_tuple:
#                print sql_str
                self.cur.execute(sql_str,pass_tuple)
                return self.cur.fetchone()
            else:
#                print sql_str
                self.cur.execute(sql_str)
                return self.cur.fetchone()
                
    def _queryOneTuple(self,sql_str,pass_tuple=None):
        with self.con:
            self.cur = self.con.cursor()
            if pass_tuple:
#                print sql_str
                self.cur.execute(sql_str,pass_tuple)
                return self.cur.fetchone()
            else:
#                print sql_str
                self.cur.execute(sql_str)
                return self.cur.fetchone()

    def _queryAllTuple(self,sql_str,pass_tuple=None): 
        with self.con:
            self.cur = self.con.cursor()
            if pass_tuple:
                self.cur.execute(sql_str,pass_tuple)
                return self.cur.fetchall()
            else:
                self.cur.execute(sql_str)
                return self.cur.fetchall()   

    def _queryAllList(self,sql_str,pass_tuple=None):
            data = self._queryAllTuple(sql_str,pass_tuple)
                
            COLUMN = 0
            column=[elem[COLUMN] for elem in data]
            return column
            
    def _queryAllDict(self,sql_str,pass_tuple=None):
        with self.con:
            self.cur = self.con.cursor(mdb.cursors.DictCursor)
            if pass_tuple:
                self.cur.execute(sql_str,pass_tuple)
                return self.cur.fetchall()
            else:
                self.cur.execute(sql_str)
                return self.cur.fetchall()  

if __name__ == '__main__':
    con = mdb.connect('localhost', 'mgrinolds', gp.get_pw(), 'kickstarter')    
    proj_table = SqlTable(con,'projects_nohtml')
    
    print proj_table.extract_single('name','idprojects',121)