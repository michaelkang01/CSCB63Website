import sqlite3
from flask import Flask, render_template, request, g, session, redirect, url_for, escape


DATABASE = './assignment3.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
        for idx, value in enumerate(row))

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

app = Flask(__name__)
app.secret_key=b'ggkledsfkl'

@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()

@app.route('/')
def index():
	if 'username' in session:
		username = session['username']
		return redirect(url_for('home'))
	return redirect(url_for('login'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		sql = """SELECT * FROM people"""
		results = query_db(sql, args=(), one=False)
		for result in results:
			if result[0] == request.form['username']:
				if result[1] == request.form['password']:
					session['username']=request.form['username']
					return redirect(url_for('index'))
		error = 'Invalid Username or Password'
	elif 'username' in session:
		return redirect(url_for('index'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('index'))

@app.route('/changeLogin', methods = ['POST', 'GET'])
def changeLogin():
	db = get_db()
	db.row_factory = make_dicts
	currentUser = session['username']
	success = False
	error = None
	#using given info do or do not make the change
	if request.method == 'POST':
		sql = """SELECT * FROM people"""
		results = query_db(sql, args=(), one=False)
		#set update values
		oldUser = session['username']
		newUser = request.form['username']
		newPass = request.form['password']
		for result in results:
			#if the username already exists and it's not their current one
			if result['username'] == newUser and result['username'] != oldUser:
				error = 'This username is already taken!'
		if error == None:
			db.execute("UPDATE people SET username=? WHERE username=?", (newUser, oldUser))
			db.execute("UPDATE people SET password=? WHERE username=?", (newPass, newUser))
			db.commit()
			db.close()
			success = True
	logged = checkLogged()
	return render_template('changeLogin.html', user = currentUser, error=error, success=success, log = logged)


@app.route('/assignments')
def assignments():
	logged = checkLogged()
	return render_template('assignments.html', log = logged)

@app.route('/discussion')
def discussion():
	logged = checkLogged()
	return render_template('discussion.html', log = logged)
	
@app.route('/modules')
def modules():
	logged = checkLogged()
	return render_template('modules.html', log = logged)
	
@app.route('/team')
def team():
	logged = checkLogged()
	return render_template('team.html', log = logged)

@app.route('/index')
def home():
	logged = checkLogged()
	return render_template('index.html', log = logged)

@app.route('/calendar')
def calendar():
	logged = checkLogged()
	return render_template('calendar.html', log = logged)

@app.route('/grades', methods = ['POST', 'GET'])
def grades():
	db = get_db()
	db.row_factory = make_dicts
	grades = []
	currentType = ""

	#To deal with regrading for instructor
	if request.method == 'POST':
		gAssignment=request.form['assignment']
		gUpdate=request.form['update']
		gUsername=request.form['username']
		#create string for sql
		sql = 'UPDATE grades SET '+gAssignment+"="+gUpdate+" WHERE username=?"
		db.execute(sql, (gUsername,))
		db.commit()

	if 'username' in session:
		currentUser = session['username']
		currentName = query_db('select name from people where username=?',[currentUser], one=True)
		currentType = query_db('SELECT type FROM people WHERE username=?',[currentUser], one=True)
		#if the user is an instructor then show all grades
		if checkInstructor(currentType) == True:
			for grade in query_db('select * from grades'):
				grades.append(grade)
		#else user is a student and only show their grades
		else:
			grades = query_db('select * from grades where username=?',[currentUser])
		db.close()
	else:
		currentName =  {'name': 'user'}

	logged = checkLogged()
	return render_template('grades.html', grade = grades, user = currentName, log = logged, type = checkInstructor(currentType))


@app.route('/remark', methods= ['POST', 'GET'])
def remark():
	remarks = []
	currentType = ""
	db = get_db()
	db.row_factory = make_dicts
	error = None
	cur = db.cursor()
	#This is to deal with changing a request from open to close.
	#handle Post request
	if request.method == 'POST' and "req" in request.form:
		reqUsername=request.form['username']
		reqRequest=request.form['req']
		db.execute('UPDATE remarks SET status = "closed" WHERE (username=? AND request=?)', (reqUsername, reqRequest))
		db.commit()
	if request.method == 'POST' and "reqFor" in request.form:
		if 'username' in session:
			currentUser = session['username']
			currentType = query_db('SELECT type FROM people WHERE username=?',[currentUser], one=True)
			if checkInstructor(currentType) == False:
				new_req = request.form
				sql = """SELECT * FROM remarks"""
				results = query_db(sql, args=(), one=False)
				for result in results:
					if result['username'] == currentUser and result['request'] == new_req['reqFor']:
						error = 'This request has already been made!'

				if error == None:
					cur.execute('insert into remarks (username, request, reasoning, status) values (?, ?, ?, ?)', 
					[
					currentUser,
					new_req['reqFor'],
					new_req['reasoning'],
					"open"
					]
					)
					db.commit()
					cur.close()
					remarks = query_db('SELECT * FROM remarks WHERE username=?',[currentUser])

	if 'username' in session:
		currentUser = session['username']
		currentType = query_db('SELECT type FROM people WHERE username=?',[currentUser], one=True)
		#if the user is an instructor then show all requests
		if checkInstructor(currentType) == True:
			for req in query_db('SELECT * FROM remarks'):
				remarks.append(req)
		#else user is a student and only show their requests
		else:
			remarks = query_db('SELECT * FROM remarks WHERE username=?',[currentUser])
	logged = checkLogged()
	db.close()
	return render_template('remark.html', remarks = remarks, error=error, log = logged, type = checkInstructor(currentType))












@app.route('/anonfb', methods= ['POST', 'GET'])
def anonfb():
	db = get_db()
	db.row_factory = make_dicts
	feedbacks = []
	instructors = []
	currentType = ""
	cur = db.cursor()
	error = None
	numFeedback =0
	if request.method == 'POST':
		print("hi")
		newFeed = request.form
		currentUser = session['username']
		sql = """SELECT * FROM anonfeedback"""
		questions = query_db(sql, args=(), one=False)
		for question in questions:
			numFeedback += 1
			if (currentUser == question['username'] and newFeed['instructor'] == question['instructor'] and 
			((newFeed['Q1A']== question['Q1'] and newFeed['Q1A'] != None) or 
			(newFeed['Q2A']== question['Q2'] and newFeed['Q2A'] != None)or
			(newFeed['Q3A']== question['Q3'] and newFeed['Q3A'] != None)or
			(newFeed['Q4A']== question['Q4'] and newFeed['Q4A'] != None)or
			newFeed['Q5A']== question['Q5'])):
				error = 'The Question(s) have b=been submitted before! Please provide new feedback'
		if error == None:
			cur.execute('insert into anonfeedback (feedbackID, username, instructor, Q1, Q2, Q3, Q4, Q5) values (?, ?, ?, ?, ?, ?, ?, ?)', 
			[
			numFeedback + 1,
			currentUser,
			newFeed['instructor'],
			newFeed['Q1A'],
			newFeed['Q2A'],
			newFeed['Q3A'],
			newFeed['Q4A'],
			newFeed['Q5A']
			]
			)
			db.commit()
			cur.close()
	if 'username' in session:
		 

		currentUser = session['username']
		currentType = query_db('SELECT type FROM people WHERE username=?',[currentUser], one=True)
		#if the user is an instructor then show all feedback directed at them.
		if checkInstructor(currentType) == True:
			for fb in query_db('SELECT * FROM anonfeedback WHERE instructor=?',[currentUser]):
				feedbacks.append(fb)
		#else user is a student and only show their feedback
		else:
			feedbacks = query_db('SELECT * FROM anonfeedback WHERE username=?',[currentUser])
			instructors = query_db('SELECT * FROM people WHERE type="instructor"')
		db.close()

	logged = checkLogged()
	return render_template('anonfb.html', numFeedback = numFeedback, feedbacks = feedbacks, instructors = instructors, error = error, log = logged, type = checkInstructor(currentType))










@app.route('/signup', methods = ['POST', 'GET'])
def signup():
	db = get_db()
	db.row_factory = make_dicts
	success = False
	error = None
	# make a new cursor from the database connection
	cur = db.cursor()

	# get the post body
	if request.method == 'POST':
		sql = """SELECT * FROM people"""
		results = query_db(sql, args=(), one=False)
		new_user = request.form
		for result in results:
			#if the username already exists
			if result['username'] == new_user['username']:
				error = 'This username is already taken!'
		# insert the new student into the database
		if error == None:
			cur.execute('insert into people (username, password, name, type, lecture ) values (?, ?, ?,?, ?)', 
			[
			new_user['username'],
			new_user['password'],
			new_user['name'],
			new_user['type'],
			new_user['section']
			]
			)
			# commit the change to the database
			db.commit()
			# close the cursor
			cur.close()
			success = True
	return render_template('signup.html', success=success, error=error)

def checkLogged():
	if 'username' in session:
		return True
	return False

def checkInstructor(currentType):
	if currentType == {"type":"instructor"}:
		return True
	return False
	
if __name__=="__main__":
	app.run(debug=True, host='0.0.0.0')
