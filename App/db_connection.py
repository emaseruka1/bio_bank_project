import sqlite3
from abc import ABC,abstractmethod    


class Sql_database(ABC):

    def connect_db(self):                          #this concrete method is abstracted away to hide sensitive database connection logic
        self.conn=sqlite3.connect('bio_bank.db')
        self.cursor=self.conn.cursor()
        #print("Database Connected & Activated")
        return self
        


    @abstractmethod      
    def action_db(self):   #this abstract method is used to offer safe pathway to connect to database without showing database credentials
        pass



    def create_tables(self):                         #method creating relational database tables for first time if non-existent
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS collections_table (                 
        id INTEGER PRIMARY KEY,                
        disease_term TEXT,                  
        title TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS samples_table (                 
        id INTEGER PRIMARY KEY, 
        collection_id INTEGER,
        donor_count INTEGER,
        material_type TEXT, 
        last_updated DATE,
        user_id INTEGER,
        FOREIGN KEY (collection_id) REFERENCES collections_table(id),
        FOREIGN KEY (user_id) REFERENCES users_table(id)
        )                   
        """ )

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_table (
        id INTEGER PRIMARY KEY, 
        username TEXT, 
        password TEXT,
        admin BOOLEAN)
        """
        )

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs_table (
        id INTEGER PRIMARY KEY, 
        timestamp TEXT,
        user_id INTEGER, 
        command TEXT,
        gods_eye_description TEXT,
        FOREIGN KEY (user_id) REFERENCES users_table(id))
        """
        )
        print("Tables created")

    def close_db(self):
        self.conn.close()
        print("Database closed")
    
    def action_db(self):
        self.connect_db()
        self.create_tables()



################################################## Unit Tests #########################################################################
if __name__=="__main__":

    sql_object=Sql_database()
    sql_object.action_db()    #create database tables for first time

    sql_object.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';") #check tables in Database
    created_tables=sql_object.cursor.fetchall()
    
    for table in created_tables:
        print(table[0])

    #add Admin user for first time if non-existant
    sql_object.cursor.execute("SELECT COUNT(*) FROM users_table WHERE username = ?", ('Admin',))
    user_exists = sql_object.cursor.fetchone()[0]
    if user_exists == 0:
        sql_object.cursor.execute("""INSERT INTO users_table (username, password, admin) VALUES (?, ?, ?)
        """, ('Admin', 'Admin1', True)) 
        sql_object.conn.commit()

    sql_object.cursor.execute("SELECT * FROM users_table WHERE username='Admin'")   #check if admin exists in user table
    admin=sql_object.cursor.fetchall()
    print(f'Admin exists in user_table as: {admin}')
 
