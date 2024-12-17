from db_connection import Sql_database
from datetime import datetime
import openai
import base64
import matplotlib.pyplot as plt
import io
from io import StringIO
import csv
import os

class User(Sql_database):

    def __init__(self, user_id, username, password):
        self.__user_id = user_id
        self.username = username
        self.__password = password
        self.admin = False
        self.today_date = datetime.today().strftime("%Y-%m-%d")
    

    def user_id_getter(self): #method to get private user id feature
        return self.__user_id
    
    def user_password_getter(self): #method to get private password feature
        return self.__password
    
    def user_password_setter(self,new_password): #method to set new password
        self.__password = new_password

    def action_db(self): #abstract method to connect to db
        return self.connect_db()
    
    def view_collections(self):
        sql_obj = self.action_db()
        sql_obj.cursor.execute('SELECT * FROM collections_table')
        result = sql_obj.cursor.fetchall()
        print(result)
        return result
        #send result to flask app/HTML webpage
    
    def create_new_collection(self,disease_term,title): #get these entries from flask app/html post method

        sql_obj = self.action_db()
        sql_obj.cursor.execute('SELECT id from collections_table WHERE disease_term=? AND title=?',(disease_term,title))
        collections_id = sql_obj.cursor.fetchall()


        if collections_id:
            print('No Duplicates:This collection already exists')
            pass #print to page that collection already exists

        else:
            
            sql_obj = self.action_db()
            sql_obj.cursor.execute('INSERT INTO collections_table (disease_term,title) VALUES (?,?)',(disease_term,title))
            sql_obj.conn.commit()
            sql_query=f"INSERT INTO collections_table (disease_term,title) VALUES (?,?)',('{disease_term}','{title}')"
            user=self.username
            self.log_update(sql_query,user)

    def view_samples(self):
        sql_obj = self.action_db()
        sql_obj.cursor.execute('SELECT * FROM samples_table')
        result = sql_obj.cursor.fetchall()
        print(result)
        return result
        #send result to flask app/HTML webpage  
 

    def create_sample(self,collection_id,donor_count,material_type): #get these entries from flask app/html post method
        sql_obj=self.action_db()
        sql_obj.cursor.execute('SELECT id FROM collections_table WHERE id=?',(collection_id,))
        result = sql_obj.cursor.fetchone()

        if result:
            sql_obj.cursor.execute('''INSERT INTO samples_table 
                                   (collection_id,donor_count,material_type,last_updated,user_id)
                                    VALUES (?,?,?,?,?)''',(collection_id,donor_count,material_type,self.today_date,self.user_id_getter()))
            sql_obj.conn.commit()
            sql_query=f"""INSERT INTO samples_table 
                                   (collection_id,donor_count,material_type,last_updated,user_id)
                                    VALUES (?,?,?,?,?)',('{collection_id}','{donor_count}',{material_type},{self.today_date},{self.user_id_getter()})"""
            user=self.username
            self.log_update(sql_query,user)
        else:
            print('Please first Insert Collection')

    def delete_sample(self,sample_id): #get these entries from flask app/html post method
        sql_obj=self.action_db()
        sql_obj.cursor.execute("DELETE FROM samples_table WHERE id = ?", (sample_id,))
        sql_obj.conn.commit()
        sql_query=f'DELETE FROM samples_table WHERE id = ?", ({sample_id},)'
        user=self.username
        self.log_update(sql_query,user)


    def search_sample(self,collection_id=None, donor_count=None, material_type=None, last_updated=None) :#get these entries from flask app/html post method
        query = "SELECT * FROM samples_table"
        conditions = []
        parameters = []

        # Dynamically add conditions based on user input
        if collection_id is not None:
            conditions.append("collection_id = ?")
            parameters.append(collection_id)
        
        if donor_count is not None:
            conditions.append("donor_count <= ?")
            parameters.append(donor_count)
        
        if material_type is not None:
            conditions.append("material_type = ?")
            parameters.append(material_type)
        
        if last_updated is not None:
            conditions.append("last_updated BETWEEN '1880-01-01' AND ?")
            parameters.append(last_updated)

        # Combine the conditions with AND
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Execute the query
        sql_obj=self.action_db()
        print(query, parameters)
        sql_obj.cursor.execute(query, parameters)
        results = sql_obj.cursor.fetchall()
        print(results)

        return results

    def view_my_log(self):
        sql_obj = self.action_db()
        sql_obj.cursor.execute('SELECT * FROM logs_table WHERE user_id=?',(self.user_id_getter(),))
        result = sql_obj.cursor.fetchall()
        print(result)
        return result
        #send result to flask app/HTML webpage 


    def log_update(self,sql_query,username): #God's Eye method

        openai.api_key = os.getenv("OPENAI_API_KEY")

        messages = [
        {"role": "system", "content": "You are a log auditor. Describe SQL queries in past tense, briefly, and in an audit log style. Mention username.Don't include dates"},
        {"role": "user", "content": f"Audit the following SQL query executed by {username}:{sql_query}"}]

        # Call the GPT-3.5-turbo chat completion API
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=messages,max_tokens=100,temperature=0.5)
        description = response['choices'][0]['message']['content']
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql_obj = self.action_db()
        sql_obj.cursor.execute('''INSERT INTO logs_table (timestamp,user_id,command,gods_eye_description)
                                VALUES (?,?,?,?)''',(timestamp,self.user_id_getter(),sql_query,description))
        sql_obj.conn.commit()
        print(description)
        


class Regular_user(User):
    def __init__(self, user_id, username, password):
        super().__init__(user_id, username, password)
        self.admin=False
    
    def change_my_login_details(self,new_username,new_password):
        
        self.username=new_username
        self.user_password_setter(new_password)
        sql_obj = self.action_db()
        sql_obj.cursor.execute('UPDATE users_table SET username = ?, password = ?  where id=?',(new_username, new_password, self.user_id_getter()))
        sql_obj.conn.commit()
        sql_query=f"UPDATE users_table SET username = '{new_username}', password = '{new_password}' WHERE id = {self.user_id_getter()}"
        user=self.username
        self.log_update(sql_query,user)
    

class admin_user(User):
    def __init__(self, user_id, username, password):
        super().__init__(user_id, username, password)
        self.admin=True

    def view_all_logs(self):
        sql_obj = self.action_db()
        sql_obj.cursor.execute('SELECT * FROM logs_table')
        result = sql_obj.cursor.fetchall()
        print(result)
        return result
        #send result to flask app/HTML webpage 

    def view_all_users(self):
        sql_obj = self.action_db()
        sql_obj.cursor.execute('SELECT * FROM users_table')
        result = sql_obj.cursor.fetchall()
        print(result)
        return result  #send result to flask app/HTML webpage 


    def add_remove_user(self,option,username):  #get option from webpage
        if option=="add":
            sql_obj = self.action_db()
            sql_obj.cursor.execute("INSERT INTO users_table (username,password,admin) VALUES (?,?,?)",(username,username+str(1),0))
            sql_obj.conn.commit()
            sql_query=f"""INSERT INTO users_table (username,password,admin) VALUES (?,?,?)",('{username}','{username+str(1)}',False)"""
            user=self.username
            self.log_update(sql_query,user)

        elif option=="remove":
            sql_obj = self.action_db()

            sql_obj.cursor.execute("DELETE FROM users_table WHERE username = ?", (username,))
            sql_obj.conn.commit()
            sql_query=f'DELETE FROM users_table WHERE id = ?", ({username},)'
            user=self.username
            self.log_update(sql_query,user)


def download_gods_eye_report(log_table_data):
    csv_output = StringIO()
    csv_writer = csv.writer(csv_output)
    csv_writer.writerow(['','timestamp', 'user_id', 'command', 'gods_eye_description']) # Write the header
    csv_writer.writerows(log_table_data) #write data
    csv_output.seek(0)
    return csv_output.getvalue()
   

def samples_bar_plot_maker(samples_data):
    collection_ids = ['Coll_ID ' + str(x[1]) + '.' + x[3] for x in samples_data]
    donor_counts = [x[2] for x in samples_data]

    # Create the bar plot
    fig, ax = plt.subplots(figsize=(15, 7))
    
    
    bars = ax.bar(collection_ids, donor_counts, color='#052168', edgecolor='black')

    # Add title and labels
    ax.set_title('Donor Count per Collection per Material Type', fontsize=20, fontweight='bold', color='black',pad=30)
    ax.set_xlabel('Collection ID and Material Type', fontsize=12, color='black')
    ax.set_ylabel('Donor Count', fontsize=12, color='black')

    
    plt.xticks(rotation=45, ha='right', fontsize=10)
    ax.spines['top'].set_visible(False)
    
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 200, int(yval), ha='center', va='bottom', fontsize=15, color='black')

    # Adjust layout for tight layout
    plt.tight_layout()

    # Save the plot to a BytesIO object and convert it to base64
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    img_b64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

    
    return(img_b64)  


################################################## Unit Tests #########################################################################
if __name__=="__main__":

    #Method test: User login
    admin_obj = admin_user(user_id=1,username='Admin',password='Admin1')  #correct login details
    admin_obj_wrong_login_cred = admin_user(user_id=1,username='Admidadfn',password='Advdcfmin1') #wrong login details


    #Method test: Adding new collections
    admin_obj.create_new_collection(disease_term='Cirrhosis of liver',title='Mothers Pregnancy Samples')
    admin_obj.create_new_collection(disease_term='Malignant tumour of breast', title='Phase II multicentre study')
    admin_obj.create_new_collection(disease_term='Fit and well', title='Lymphoblastoid cell lines')
    admin_obj.create_new_collection(disease_term='Chronic fatigue syndrome', title='Samples available include ME/CFS Cases')
    admin_obj.create_new_collection(disease_term='Malignant tumour of breast', title='A randomised placebo-controlled trial')

    admin_obj.create_new_collection(disease_term='Malignant tumour of breast', 
                                    title='A randomised placebo-controlled trial')#try adding duplicate collection. Duplicate entry is rejected
    
    #Method test: Viewing all collections
    admin_obj.view_collections() 


    #Method test: Creating Samples
    admin_obj.create_sample(collection_id=4,donor_count=90210,material_type='Cerebrospinal fluid')
    admin_obj.create_sample(collection_id=2,donor_count=512,material_type='Cerebrospinal fluid')
    admin_obj.create_sample(collection_id=2,donor_count=7777,material_type='Core biopsy')


    #Method test: Viewing all samples
    admin_obj.view_samples()

    #Method test: Deleting a Sample
    admin_obj.create_sample(collection_id=2,donor_count=10000,material_type='Delete this Sample') 
    admin_obj.view_samples()
    admin_obj.delete_sample(sample_id=4)
    admin_obj.view_samples() 

    #Method test: Searching for Samples with miscellaneous queries
    admin_obj.search_sample(donor_count=8000)
    admin_obj.search_sample(collection_id=2)
    admin_obj.search_sample(donor_count=3000, material_type="Cerebrospinal fluid")
    admin_obj.search_sample(donor_count=117000, collection_id=4, last_updated="2024-12-01")
    admin_obj.search_sample(last_updated="2024-12-14")

    #Method test: Admin Add new User and view all users
    admin_obj.add_remove_user(option="add",username="Andy Rae")
    admin_obj.add_remove_user(option="add",username="Beforan")
    admin_obj.add_remove_user(option="add",username="Jonathan")
    admin_obj.add_remove_user(option="add",username="Tania")
    admin_obj.view_all_users()

    #Method test: Admin remove User
    admin_obj.add_remove_user(option="add",username="Emmanuel")
    admin_obj.view_all_users()
    admin_obj.add_remove_user(option="remove",username="Emmanuel")
    admin_obj.view_all_users()


    #Regular User tests: Regular User inherits all methods from the User Class
    regular_user_obj=Regular_user(user_id=2,username="Andy Rae",password="Andy Rae1")
    regular_user_obj.create_new_collection(disease_term="COVID",title="New Collection added by User")
    regular_user_obj.view_collections()


    regular_user_obj.view_my_log()

    admin_obj.view_all_logs()

    admin_obj.close_db()

    
