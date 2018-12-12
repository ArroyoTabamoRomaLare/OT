import pymysql
from app import app
#from tables import Results
from db_config import mysql
from flask import flash, render_template, request, redirect, session, url_for,escape
from werkzeug import generate_password_hash, check_password_hash
from hashlib import md5
from flask_table import Table, Col, LinkCol
 
class Results(Table):
 stud_id = Col('ID', show=False)
 studno = Col('Student Number')
 fname = Col('First Name')
 lname = Col('Last Name')
 contact = Col('Contact Number')
 gender = Col('Gender')
 bday = Col('Birthday')
 program = Col('Program')
 edit = LinkCol('Update', 'updatestudentsview', url_kwargs=dict(id='stud_id'))
 delete = LinkCol('Delete', 'deletestudent', url_kwargs=dict(id='stud_id'))

@app.route('/')
def index():
    if 'username' in session:
        username_session = escape(session['username']).capitalize()
        return render_template('homepage.html', session_user_name=username_session)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username_form  = request.form['uname']
        password_form  = request.form['psw']
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(1) FROM users WHERE uname = %s;", [username_form])
        if cursor.fetchone()[0]:
        	cursor.execute("SELECT pass FROM users WHERE uname = %s;", [username_form])
        	for row in cursor.fetchall():
        		passx =(password_form).encode()
        		if md5(passx).hexdigest() == row[0]:
        			session['username'] = request.form['uname']
        			return redirect(url_for('index'))
        		else:
        			error = "Invalid Credential"
        else:
        	error = "Invalid Credential"
    return render_template('index.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/new_student')
def add_student():
	return render_template('addstuds.html')

#@app.route('/list_student')
#def list_student():
#	return render_template('listofstuds.html')

@app.route('/search_student')
def search_student():
	return render_template('searchstuds.html')

@app.route('/add', methods=['POST'])
def addstudent():
 try:
  _fname = request.form['firstname']
  _lname = request.form['lastname']
  _contact = request.form['contactno']
  _gender = request.form['gender']
  _month = request.form['month']
  _day = request.form['day']
  _year = request.form['year']
  _studno = request.form['studno']
  _progg = request.form['program']

  if _fname and _lname and _contact and _gender and _month and _day and _year and _studno and _progg and request.method == 'POST':
   bday = _month + " " + _day + ", " + _year  
   sql = "INSERT INTO students(fname,lname,contact,gender,bday,studno,program) VALUES (%s,%s,%s,%s,%s,%s,%s)"
   data = (_fname,_lname,_contact,_gender,bday,_studno,_progg)
   conn = mysql.connect()
   cursor = conn.cursor()
   cursor.execute(sql,data)
   conn.commit()
   flash('Student added successfully!')
   return redirect('/')
  else:
   return 'Error while adding user'
 except Exception as e:
  print(e)
 finally:
  cursor.close()
  conn.close()

@app.route('/list')
def liststudents():
 try:
  conn = mysql.connect()
  cursor = conn.cursor(pymysql.cursors.DictCursor)
  cursor.execute("SELECT * FROM students")
  rows = cursor.fetchall()
  table = Results(rows)
  table.border = True
  return render_template('listofstuds.html',table=table)
 except Exception as e:
  print(e)
 finally:
  cursor.close()
  conn.close()

@app.route('/updatestudent/<int:id>')
def updatestudentsview(id):
 try:
  conn = mysql.connect()
  cursor = conn.cursor(pymysql.cursors.DictCursor)
  cursor.execute("SELECT * FROM students WHERE stud_id=%s", id)
  row = cursor.fetchone()
  if row:
   return render_template('updatestuds.html', row=row)
  else:
   return 'Error loading #{id}'.format(id=id)
 except Exception as e:
   print(e)
 finally:
  cursor.close()
  conn.close()

@app.route('/update', methods=['POST'])
def updatestudent():
 try:
  _fname = request.form['ufname']
  _lname = request.form['ulname']
  _contact = request.form['ucontact']
  _progg = request.form['uprogram']
  _id = request.form['id']

  if _fname and _lname and _contact and _progg and _id and request.method == 'POST': 
   sql = "UPDATE students SET fname=%s,lname=%s,contact=%s,program=%s WHERE stud_id=%s"
   data = (_fname,_lname,_contact,_progg,_id)
   conn = mysql.connect()
   cursor = conn.cursor()
   cursor.execute(sql,data)
   conn.commit()
   flash('Student updated successfully!')
   return redirect('/list')
  else:
   return 'Error while updating user'
 except Exception as e:
  print(e)
 finally:
  cursor.close()
  conn.close()

@app.route('/deletestudent/<int:id>')
def deletestudent(id):
 try:
  conn = mysql.connect()
  cursor = conn.cursor()
  cursor.execute("DELETE FROM students WHERE stud_id=%s", id)
  conn.commit()
  flash('User deleted successfully!')
  return redirect('/list')
 except Exception as e:
  print(e)
 finally:
  cursor.close() 
  conn.close()

@app.route('/searchbyfname', methods=['POST'])
def searchfname():
 _fname = request.form['fname']
 try:
  conn = mysql.connect()
  cursor = conn.cursor(pymysql.cursors.DictCursor)
  cursor.execute("SELECT * FROM students WHERE fname LIKE %s", ("%"+_fname+"%"))
  rows = cursor.fetchall()
  table = Results(rows)
  table.border = True
  return render_template('searchstuds.html',table=table)
 except Exception as e:
  print(e)
 finally:
  cursor.close()
  conn.close()

@app.route('/searchbylname', methods=['POST'])
def searchlname():
 _lname = request.form['lname']
 try:
  conn = mysql.connect()
  cursor = conn.cursor(pymysql.cursors.DictCursor)
  cursor.execute("SELECT * FROM students WHERE lname LIKE %s", ("%"+_lname+"%"))
  rows = cursor.fetchall()
  table = Results(rows)
  table.border = True
  return render_template('searchstuds.html',table=table)
 except Exception as e:
  print(e)
 finally:
  cursor.close()
  conn.close()

@app.route('/searchbystudno', methods=['POST'])
def searchstudno():
 _studno = request.form['studno']
 try:
  conn = mysql.connect()
  cursor = conn.cursor(pymysql.cursors.DictCursor)
  cursor.execute("SELECT * FROM students WHERE studno LIKE %s", ("%"+_studno+"%"))
  rows = cursor.fetchall()
  table = Results(rows)
  table.border = True
  return render_template('searchstuds.html',table=table)
 except Exception as e:
  print(e)
 finally:
  cursor.close()
  conn.close()


if __name__ == "__main__":
    app.run()