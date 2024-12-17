from flask import Flask, request,render_template,redirect, session, url_for,flash,send_file,Response
from models import *
import os


app = Flask(__name__)  #create the flask application
app.secret_key=os.urandom(24)  #generate a secret key to manage a user session

def get_current_user(): #Initialises user credentials for current session
    user_id = session.get('user_id')
    username = session.get('username')
    password = session.get('password')

    if user_id == 1:  # Check user type
        return admin_user(user_id, username, password)
    else:
        return Regular_user(user_id, username, password)



@app.route('/',methods=['GET', 'POST'])        #url to login page
def login_page():

    if request.method == 'POST':  # Get user input from the login form
        user_id = int(request.form['user_id'])
        username = request.form['username']  
        password = request.form['password']

        session['user_id'] = user_id
        session['username'] = username
        session['password']=password
        
        login_credentials =(user_id,username,password)
        
        all_users = admin_user(1,'Admin','Admin1').view_all_users()

        passed_verification=False               

        for i in range(0,len(all_users)):
            
            if login_credentials == all_users[i][0:3]:
                passed_verification=True
                break

        if passed_verification:       
            return redirect(url_for('home_page')) # Go to the home page after login verified 
        else:
            flash("Invalid login details. Please try again or Contact Admin.") # Flash message and go to login page after login failure


    return render_template(template_name_or_list='login_page.html')


@app.route('/home_page',methods=['GET', 'POST'])
def home_page():


    if get_current_user().username==None:   #redirected to login page if not user
        #flash("You need to be an admin to access this page.")
        return redirect(url_for('login_page'))
    


    username = get_current_user().username
    collections = get_current_user().view_collections()  # show all collections
    samples = get_current_user().view_samples()  # show all samples

    if request.method == "POST":
        # Handle the Add New Collection form
        if request.form.get('form_action') == 'add_collection':
            disease = request.form['Disease_Term']
            title = request.form['title']
            get_current_user().create_new_collection(disease_term=disease, title=title)

        # Handle the Add New Sample form
        elif request.form.get('form_action') == 'add_sample':
            collection_id = request.form['collection_id']
            donor_count = request.form['donor_count']
            material_type = request.form['material_type']
            get_current_user().create_sample(collection_id, donor_count, material_type)

        # Handle the Delete Sample form
        elif request.form.get('form_action') == 'delete_sample':
            sample_id = request.form['sample_id']
            get_current_user().delete_sample(sample_id)

        return redirect(url_for('home_page'))

    return render_template('home_page.html', message=username, collections=collections, samples=samples)

@app.route('/search',methods=['GET', 'POST'])
def search():

    if get_current_user().username==None:   #redirected to login page if not user
        #flash("You need to be an admin to access this page.")
        return redirect(url_for('login_page'))

    samples = get_current_user().view_samples()
    bar_plot_img = samples_bar_plot_maker(samples)

    if request.method == 'POST':
        collection_id = request.form.get('collection_id')
        donor_count =request.form.get('donor_count')
        material_type=request.form.get('material_type')
        last_updated=request.form.get('last_updated')
        
        collection_id = collection_id if collection_id else None
        donor_count = donor_count if donor_count else None
        material_type = material_type if material_type else None
        last_updated = last_updated if last_updated else None
        

        samples = get_current_user().search_sample(collection_id,donor_count,material_type,last_updated)
        bar_plot_img = samples_bar_plot_maker(samples)

    return render_template('search.html',samples=samples,bar_plot_img=bar_plot_img)

@app.route('/admin_page',methods=['GET', 'POST'])
def admin_page():

    if get_current_user().username!="Admin":   #redirected to home page if not Admin
        #flash("You need to be an admin to access this page.")
        return redirect(url_for('home_page'))


    users = get_current_user().view_all_users()

    if request.method=="POST":
        username = request.form.get('username')
        form_action = request.form.get('form_action')

        if form_action == 'add':
            get_current_user().add_remove_user(option='add',username=username)
            return redirect(url_for('admin_page'))
    
        elif form_action == 'remove':
            get_current_user().add_remove_user(option='remove',username=username)
            return redirect(url_for('admin_page'))
        
        elif 'download_log_csv' in request.form:
            logs_data = get_current_user().view_all_logs()
            logs_csv = download_gods_eye_report(logs_data)
            
            # Return the CSV as a download response
            return Response(
                logs_csv,
                mimetype='text/csv',
                headers={"Content-Disposition": "attachment;filename=log_data.csv"}
            )
        
        elif 'download_log_csv_admin' in request.form:
            logs_data = get_current_user().view_my_log()
            logs_csv = download_gods_eye_report(logs_data)
            
            # Return the CSV as a download response
            return Response(
                logs_csv,
                mimetype='text/csv',
                headers={"Content-Disposition": "attachment;filename=log_data.csv"}
            )
        
    return render_template('admin.html',users=users)



if __name__=="__main__":
    app.run(host='0.0.0.0',port=5555,debug=True)
    