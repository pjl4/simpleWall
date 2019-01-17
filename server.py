from flask import Flask,render_template,session,request,redirect,flash
# import the function connectToMySQL from the file mysqlconnection.py
from mysqlconnection import connectToMySQL
import re
from flask_bcrypt import Bcrypt
app = Flask(__name__)
bcrypt=Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = "ThisIsSecret!"
DB="simpledb"
@app.route('/')
def index():
    
    
    return render_template('index.html')

@app.route('/delete',methods=["POST"])
def delete():
    deleteMessage=request.form
    if int(session['id'])!=int(deleteMessage['recieverID']):
        return redirect('/danger')
    
    mysql=connectToMySQL(DB)
    query="DELETE FROM messages WHERE id = %(message_id)s "
       
    data={
        'message_id': deleteMessage['messageID']
    }
    delete=mysql.query_db(query,data)

    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    mysql=connectToMySQL(DB)
    user=request.form
    query="SELECT id,first_name FROM users;"
    users=mysql.query_db(query)

    getMessages="SELECT message,sender_id,reciever_id,first_name,messages.id FROM messages LEFT JOIN users ON messages.sender_id=users.id WHERE %(reciever_id)s;"
    data={
        'reciever_id': session['id']
    }
    mysql=connectToMySQL(DB)
    messages=mysql.query_db(getMessages,data)
    return render_template('dashboard.html',users=users,messages=messages)

@app.route('/send',methods=["POST"])
def sendMessage():
    mysql=connectToMySQL(DB)
    message=request.form
    userRecieve=message['reciever']
    userSend=session['id']
    messageContent=message['message']

    query = "INSERT INTO messages (message,reciever_id,sender_id) VALUES (%(message)s,%(reciever_id)s,%(sender_id)s);"
    data={
        'message':messageContent,
        'reciever_id':userRecieve,
        'sender_id':userSend
    }
    if mysql.query_db(query,data):
        flash("Message Sent!")
    

    return redirect('/dashboard')

@app.route('/danger')
def danger():
    return render_template('danger.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
@app.route('/register',methods=["POST"])
def create():
    mysql=connectToMySQL(DB)
    user=request.form
    query="SELECT * FROM users WHERE email=%(email)s;"
    data={
        'email': user['email']
    }
    
    if len(user['email']) <1:
        flash ("Email cannot be blank")
    if not EMAIL_REGEX.match(user['email']):
        flash ("Email is not valid")
    if mysql.query_db(query,data):
        flash ("Email or password incorrect")
    if (len(user['first_name']) < 2):
        flash("First Name must not be blank")
    if  re.search("[0-9]",user['first_name']):
        flash("First name cannot contain numbers")
    if  re.search("[0-9]",user['last_name']):
        flash("Last name cannot contain numbers")
    if (len(user['last_name']) < 2):
        flash("Last Name must not be blank")
    if (len(user['password'])<8):
        flash("Password must be more than 8 characters")
    if (user['password']!=user['confirm']):
        flash("Passwords must match")
    if not re.search("[A-Z]",user['password']):
        flash("Password must contain 1 Upper Case")
    if not re.search("[0-9]",user['password']):
        flash("Password must contain 1 Number")
    if '_flashes' in session.keys():
        return redirect("/")
    
    pw_hash = bcrypt.generate_password_hash(user['password'])
    query2= "INSERT INTO users (first_name,last_name,email,pw_hash) VALUES (%(first_name)s,%(last_name)s,%(email)s,%(pw_hash)s);"
    data2={
        'first_name': user['first_name'],
        'last_name':user['last_name'],
        'email': user['email'],
        'pw_hash': pw_hash
    }
    mysql=connectToMySQL(DB)
    
    new_user=mysql.query_db(query2,data2)
    flash("Successfully Registered!")
    session['first_name']=user['first_name']
    session['id']=new_user
    return redirect('/dashboard')


@app.route('/login',methods=['POST'])
def login():
    mysql=connectToMySQL(DB)
    user=request.form
    query="SELECT * FROM users WHERE email=%(email)s;"
    data={
        'email': user['email']
    }
    result=mysql.query_db(query,data)
    if result:
        if bcrypt.check_password_hash(result[0]['pw_hash'], user['passwordLogin']):
            session['first_name']=result[0]['first_name']
            session['id']=result[0]['id']
            return redirect('/dashboard')
    flash("You could not be logged in.")
    return redirect('/dashboard')

if __name__ == "__main__":
    app.run(debug=True)