import os
import sys
import mysql.connector
from database._db_manager import _DB_manager
from logs import logger

class MySQL (_DB_manager): 
    
    def get_cursor_connector (self): 
        """
        Connect to mysql database and return cursor
        """
        
        try: 
            self.connection.cursor()
        except AttributeError: 
            
            try: 
                self.connection = mysql.connector.connect(host=self.server, 
                                            database=self.database, 
                                            user=self.username, 
                                            password=self.password)
            except Exception as err: 
                
                self.error(err)

                return None
        
        return self.connection.cursor() 
                
    def run_sql (self, sql): 
        """ Exceute sql code
        
        Run sql code in the current data base, and commit it
        """
        
        cursor = self.get_cursor_connector()
           
        # Try to run sql  
        try: 
            cursor.execute (sql)
        except Exception as err:
            
            self.error(err, sql)
            
            return None
        
        # try to get returned part
        try: 
            results = cursor.fetchall()
        except: 
            results = None
        
        self.connection.commit()
        return results

    def get_tables_names (self): 
        """ Return all table name sin current data base
        """
        
        sql = ""
        sql += "SELECT * "
        sql += "FROM information_schema.tables "
        sql += f"WHERE table_schema = '{self.database}';"
        
        tables = []
        tables_data = self.run_sql(sql)
        for table_row in tables_data:
            tables.append (table_row[2])
            
        # Logs
        logger.debug (f"Returned table names")
        
        return tables

    def get_rows (self, table, top_rows=0): 
        """ Get column names from specific table
        """
        
        sql = ""
        
        if top_rows > 0: 
            sql += f"SELECT TOP ({top_rows}) * "
        else: 
            sql += f"SELECT * "
            
        sql += f"FROM {table}"
        
        rows = self.run_sql (sql)
        
        # Logs
        logger.debug (f"Returned rows of table {table}")
        
        return rows