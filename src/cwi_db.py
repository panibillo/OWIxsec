'''
Created on May 24, 2021

Requires Python >= 3.6

@author: Bill
'''
'''
Created on May 24, 2021

A simple interface to a cwi clone database in sqlite. 

Provides a context manager that handles open and close, and a qmarks() method.
User should use standard pyodbc calls to execute queries. 

@author: Bill Olsen
'''
import sqlite3 as sqlite
import logging
logger = logging.getLogger('cwi_db')
if __name__ == '__main__':
    logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S',
    format = '%(asctime)s - %(name)s:%(funcName)s:%(lineno)d - %(levelname)s -- %(message)s')
logger.setLevel(logging.WARNING)

class DB_context_manager():
    """ 
    A simple context manager mixin for opening and closing connections to a db.
    
    The db should support methods:
        open_db()
        commit_db()
    The db should instantiate boolean variables:
        context_connected : True when a connection and cursor exist
        context_autocommit : True if db should be committed prior to closing 
                             the connection.
    """
    
    def __init__(self, commit=False):    
        self.context_connected = False
        self.context_autocommit = commit
    
    def __enter__(self):
        self.context_connected = self.connection_open==True
        self.open_db()
        return self
         
        
    def __exit__(self, exc_type, exc_value, exc_traceback): 
        if self.context_autocommit==True:
            self.commit_db()
        if self.context_connected == False:
            self.close_db()
        self.context_connected = False
        self.context_autocommit = False

    
class DB_SQLite(DB_context_manager):
        
    def __init__(self, db_name=None, open_db=False, commit=False):
        self.db_name = db_name
        if open_db: 
            self.connection_open = self.open_db()
        else: 
            self.connection_open = False
        super().__init__(commit)
 
    def __str__(self):
        rv = "DB_SQLite( db_name='%s' )"%self.db_name
        return rv

    def __repr__(self):
        rv = "WTDB_link(db_name='%s')"%self.db_name
        return rv

    def open_db(self):
        try:
            self.con = sqlite.connect(self.db_name)
            self.cur = self.con.cursor()
            self.connection_open = True
        except:
            logger.error (f"Could not open database: {self.db_name}")
            self.connection_open = False
        return self.connection_open
        
    def close_db(self, commit=False):    
        if commit==True:
            if self.db_name == ':memory:':
                raise ValueError ('Attempting to commit an in-memory database')
            self.commit_db()
        self.cur.close()
        self.con.close()
        self.connection_open = False

    @staticmethod
    def qmarks(vals):
        '''
        Return a string of comma separated questionmarks matching vals
    
        Questionmark parameter markers are used to prevent sql injection.
          
        if vals is string   : Interpret as 1 variable. No attempt to split.
        if vals is int      : Interpret as the number of variables.
        if vals is iterable : Interpret as a collection of variables, and count
                              the number of variables in the collection.
        
        qmarks( 'Bozo' )        return '?'
        qmarks( 4 )             return '?,?,?,?'
        qmarks( [4] )           return '?'
        qmarks( (1,2,'Bozo') )  return '?,?,?'
        '''
        if isinstance(vals, str):
            return '?'
        elif isinstance(vals, int):
            return ','.join(vals * ['?'])
        else:
            return ','.join(len(vals) * ['?'])


class c4db(DB_SQLite): 
    def __init__(self, 
                 db_name='.../OWI/db/cwi30.sqlite',
                 open_db=False, commit=False):
        DB_SQLite.__init__(self, db_name, open_db=open_db, commit=commit)
        self.c4tables = 'c4ix c4ad c4c1 c4c2 c4id c4pl c4rm c4st c4wl c4locs'.split()

    def __str__(self):
        rv=(f"c4db(db_name='{self.db_name}', commit={self.context_autocommit})",
            f"     connection_open: {self.connection_open}",
            f"     context_connected: {self.context_connected}",
            f"     context_autocommit: {self.context_autocommit}")
        
        return '\n'.join(rv)

    def __repr__(self):
        rv = f"c4db(db_name='{self.db_name}', commit={self.context_autocommit})" 
        return rv

if __name__ == '__main__':
    import os
    print (os.path.abspath('../demo_data/OWIxsec_demo.sqlite'))
    db = c4db(db_name = '../demo_data/OWIxsec_demo.sqlite', open_db=True)  
    s = "select tbl_name from sqlite_master where type='table';"
    data = db.cur.execute(s).fetchall()
    for row in data:
        s = f"select count(*) from {row[0]};"
        n = db.cur.execute(s).fetchall()
        print (f"  {row[0]} :{n[0][0]:4} records")
    print ('/////////// DONE ////////////')
    
    
    