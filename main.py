import mysql.connector as connection
from flask import Flask, session, render_template, redirect, url_for, request, flash
import time, random
from datetime import datetime

app = Flask('app')
app.secret_key = 'SECRET_KEY'
letterID = 0
db = connection.connect(
    host="phase2-7.cgi21eqy7g91.us-east-1.rds.amazonaws.com",
    user="admin",
    password="phasetwo7",
    database="integration"
)

####################################################
#                    FUNCTIONS                     #
####################################################

# reconnect to database if to referesh any changes made from another device
def _reconnect():
    global db
    db = connection.connect(
        host="phase2-7.cgi21eqy7g91.us-east-1.rds.amazonaws.com",
        user="admin",
        password="phasetwo7",
        database="integration"
    )

# given a time string, return the start and end time
def _process_time(class_time):
    time_list = class_time.split("-")

    start_time = float(time_list[0][0:2])
    if str(time_list[0][3]) != '0':
        start_time += 0.5

    end_time = float(time_list[1][0:2])
    if str(time_list[1][3]) != '0':
        end_time += 0.5

    return start_time, end_time

# uses the current time to determine the current semester
def _get_curr_semester():
    seasons = {
            'Spring': ['August','September', 'October', 'November', 'December'],
            'Fall': ['January', 'February', 'March', 'April', 'May', 'June']
            }
    
    current_time = datetime.now()
    current_month = current_time.strftime('%B')
    current_year = int(current_time.strftime('%Y'))

    for season in seasons:
      if current_month in seasons[season]:
        if season == 'Spring':
          current_year += 1
        return season, current_year
    return 'Invalid input month'

def _calendar_map(class_time):
    times = _process_time(class_time)
    hour1 = times[0] - 12
    hour2 = times[1] - 12
    diff = hour2 - hour1

    return hour1, hour2, diff*2+1



def sessionStatus():
    return session['user_id']

def sessionType():
    return session['type']

def checkComplete():
  cursor = db.cursor(dictionary = True)
  cursor.execute("SELECT * FROM applications WHERE status = 'incomplete'")
  apps = cursor.fetchall()
  for i in range(len(apps)):
    app = apps[i]
    if(app["student_id"]!=None and app["semester"]!=None and app["s_year"]!=None and app["degree_type"]!=None and app["interest"]!=None and app["experience"]!=None):
      cursor.execute("UPDATE applications SET status = 'review' WHERE student_id = %s and semester = %s and s_year = %s", (app["student_id"], app["semester"], app["s_year"]))
      db.commit()
  global letterID
  letterID += 1


####################################################
#                WEBSITE FUNCTIONS                 #
####################################################

# Reset the database
@app.route('/reset', methods=['GET', 'POST'])
def reset():
  cur = db.cursor(dictionary=True)
  with open('phase2create.sql', 'r') as f:
    sql_scr = f.read()
  sql_c = sql_scr.split(';')
  for c in sql_c:
    cur.execute(c)
    db.commit()
  session.pop('username', None)
  session.pop('user_id', None)
  session.pop('fname', None)
  session.pop('lname', None)
  session.pop('type', None)
  session.clear()

  return redirect('/')




# Commits all the saved registered classes to the database
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # Commit data to enrollment table
    if request.method == 'POST':
        cursor = db.cursor(dictionary=True)
        semester = _get_curr_semester()
        for cid in session["registration"]:
            cursor.execute("INSERT INTO student_courses (student_id, class_id, grade, csem, cyear) VALUES (%s, %s, 'IP', %s, %s)", (session['user_id'], cid, semester[0], semester[1]))
            db.commit()

        session["registration"] = []
        session.modified = True

        flash("You've successfully registered!", "success")

    return redirect('/register') 

# Route to add a class
@app.route('/add', methods=['GET', 'POST'])
def add():
  if request.method == 'POST':
      _reconnect()

      cursor = db.cursor(dictionary=True)

      # Retrieve form data
      cid = request.form["cid"]
      csem = request.form["csem"]
      cyear = request.form["cyear"]
      course = request.form["course"]
      day = request.form["day_of_week"]

      # 1. Check if class already in currently registered class
      if cid in session["registration"]:
          flash("You've already added that class", "error")
          return redirect('/register')


      # Check if already enrolled previously
      cursor.execute('''SELECT * FROM student_courses s 
      JOIN class_section c ON s.class_id = c.class_id AND s.csem = c.csem AND s.cyear = c.cyear
      JOIN course i ON c.course_id = i.id
      WHERE i.id = %s AND s.student_id = %s AND s.grade != "D" AND s.grade != "F" ''', (course, session['user_id']))
      data = cursor.fetchone()

      if data:
          if data['csem'] == csem and data['cyear'] == cyear:
            message = "You are currently enrolled in " + data['course_name'] + " for this semester"
          else:
            message = "You've already taken " + data['course_name'] +" in " + data['csem'] + " " + str(data['cyear'])
          flash(message, "error")
          return redirect('/register') 

      # Check prereq  
      cursor.execute('''SELECT p.prereq_id FROM class_section c
      JOIN course i ON c.course_id = i.id
      JOIN prerequisite p ON i.id = p.course_id
      WHERE i.id = %s''',(cid, ))
      ids = cursor.fetchall()
      print(ids)

      cursor.execute("SELECT * FROM student_courses s JOIN class_section c ON s.class_id = c.class_id JOIN course i ON c.course_id = i.id WHERE s.student_id = %s GROUP BY i.id", (session['user_id'],))
      taken = cursor.fetchall()
      for row in taken:
        print(row['id'])
      
      for id in ids:
        # Check if the id appears in taken 
        if id['prereq_id'] not in taken:
          flash("You do not fulfill the prerequisites for this class", "error")
          return redirect('/register') 
        

      # Check schedule conflict
      my_time = request.form["class_time"]
      my_class_time = _process_time(my_time)
      
      print("time: ", my_class_time)

      # Retrieve all class times for currently registering year and semester for each class and check
      for class_id in session["registration"]:
          cursor.execute("SELECT class_time FROM class_section WHERE class_id = %s AND csem = %s \
                          AND cyear = %s", (class_id, csem, cyear))
          other_time = cursor.fetchone()['class_time']
          curr_class_time =  _process_time(other_time)

          if (my_class_time[0] > curr_class_time[0] - 0.5 and my_class_time[0] < curr_class_time[1] + 0.5) or (my_class_time[1] > curr_class_time[0] - 0.5 and my_class_time[1] < curr_class_time[1] + 0.5):
              flash("This class has a time conflict with a class you've already added", "error")
              return redirect('/regsiter') 
        

      # Now we have to check for the classes that already got checked out but for current semester/year
      cursor.execute('''SELECT class_time FROM class_section cs JOIN student_courses e ON cs.class_id = e.class_id AND cs.csem = e.csem AND cs.cyear = e.cyear \
                      WHERE cs.csem = %s AND cs.cyear = %s AND cs.day_of_week = %s AND student_id = %s''', (csem, cyear, day ,session['user_id']))
      time_list = cursor.fetchall()
      for curr_class in time_list:
          curr_class_time = _process_time(curr_class['class_time'])
          print("test: ", curr_class_time)
          if (my_class_time[0] > curr_class_time[0] - 0.5 and my_class_time[0] < curr_class_time[1] + 0.5) or (my_class_time[1] > curr_class_time[0] - 0.5 and my_class_time[1] < curr_class_time[1] + 0.5):
            flash("This class has a time conflict with a class you've already registered for", "error")
            return redirect('/register') 
          

      # If no issue, then add to registered class
      session["registration"].append(cid)
      session.modified = True
      flash("Added class to cart", "success")

  return redirect('/register')

# Drop courses
@app.route('/drop', methods=['GET', 'POST'])
def drop():
    if request.method == 'POST':
        cursor = db.cursor(dictionary=True)
        stud_id = request.form['stud_id']
        cid = request.form["cid"]
        csem = request.form["csem"]
        cyear = request.form["cyear"]

        cursor.execute("DELETE FROM student_courses WHERE student_id = %s AND class_id = %s AND csem = %s AND cyear = %s", (stud_id, cid, csem, cyear))
        db.commit()

        flash("Successfully dropped the class", "success")


    return redirect('/register')

# Remove from registration 
@app.route('/remove', methods=['GET', 'POST'])
def remove():
    if request.method == 'POST':
        session["registration"].remove(request.form["cid"])
        session.modified = True

    return redirect('/register')


####################################################
#                    HOME PAGE                     #
####################################################

@app.route('/')
def home_page():
  _reconnect()
  if 'username' in session: 
    return redirect('/userloggedin')
  
  return render_template("home.html", title = 'Home Page')

####################################################
#                    LOGIN PAGE                    #
####################################################


@app.route('/userlogin', methods=['GET', 'POST'])
def login():
  _reconnect()

  if request.method == "GET":
    return render_template("login.html")

  if request.method == 'POST':

    # Connect to the database
    try:
      cur = db.cursor(dictionary = True)
      uname = (request.form["username"])
      passwrd = (request.form["password"])
    except:
      flash("Error connecting to database. Please try again", "error")
      return render_template('login.html')

    # Check if there's any input:
    if uname == "" or passwrd == "":
        flash("Please enter your username and password", "error")
        return render_template('login.html') 

    # Check if the username and password are correct
    try:
      cur.execute("SELECT username, user_password, user_type, user_id, fname, lname FROM user WHERE username = %s and user_password = %s", (uname, passwrd))
      data = cur.fetchone()
      print(data)
      if data:
        session['username'] = data['username']
        session['user_id'] = data['user_id']
        session['fname'] = data['fname']
        session['lname'] = data['lname']
        session['type'] = data['user_type']
        session['registration'] = []
        return redirect('/userloggedin')
      else:
        flash("Incorrect username and password", "error")
    except:
      flash("Error while logging in. Please try again", "error")

  return render_template('login.html')


####################################################
#                   CATALOG PAGE                   #
####################################################

@app.route('/catalog')
def catalog():
  _reconnect()
  
  # Get all departments from classes
  cursor = db.cursor(dictionary=True)
  cursor.execute("SELECT dept_name FROM course GROUP BY dept_name ORDER BY dept_name ASC")
  dept = cursor.fetchall()

  # Store all classes for each depatemtn in a dictionary
  course = {}
  for row in dept:
    cursor.execute("SELECT * FROM course WHERE dept_name = %s", (row["dept_name"],))
    course[row["dept_name"]] = cursor.fetchall()

  # Get all prerequisites
  cursor.execute("SELECT * FROM prerequisite p JOIN course c ON p.prereq_id = c.id ORDER BY c.course_num ASC")    
  prereq = cursor.fetchall()

  logged = False

  if 'user_id' in session:
    logged = True

  return render_template('catalog.html', dept=dept, course=course, prereq=prereq, logged=logged)

####################################################
#                  LOGIN REDIRECT                  #
####################################################

@app.route('/userloggedin', methods=['GET', 'POST'])
def user():
  if 'username' in session: 
    #check for the student logging in
    if(session['type'] == 5 or session['type'] == 4):
      return redirect('/studentlogging')
    
    #check for the alumni 
    if(session['type'] == 2):
      return redirect('/alumnilogging')
    
    #check for admin 
    if(session['type'] == 0):
      return redirect('/admin')

    #check for applicant 
    if(session['type'] == 6):
      return redirect('/welcome')

    #check for faculty advisor
    elif(session['type'] == 1):
      return redirect('/faculty')

   #check for grad secretary 
    elif(session['type'] == 3):
      return redirect('/gradsec')
    
  return redirect('/')

####################################################
#                REGISTRATION PAGE                 #
####################################################

@app.route('/register', methods=['GET', 'POST'])
def register():
    _reconnect()

    # Connect to database
    cursor = db.cursor(dictionary=True)
    semester = _get_curr_semester()
    query = "SELECT * FROM class_section cs \
            JOIN course c ON cs.course_id = c.id WHERE \
            cs.csem = %s AND cs.cyear = %s"
    params = [semester[0], semester[1]]

    # Display the courses
    if request.method == 'POST':   # If request = POST, query based on form data (i.e search function)
        dname = request.form["dname"]
        cnum = request.form["cnum"]
        cid = request.form["cid"]
        title = request.form["title"]  

        if dname != "":
            query += " AND c.dept_name LIKE  %s"
            params.append(f"%{dname}%")
        
        if cnum != "":
            query += " AND c.course_num = %s"
            params.append(cnum)

        if cid != "":
            query += " AND cs.class_id = %s"
            params.append(cid)

        if title != "":
            query += " AND c.course_name LIKE %s"
            params.append(f"%{title}%")
       
    query += " ORDER BY c.dept_name, c.course_num"

    cursor.execute(query, params)
    classes = cursor.fetchall()

    cursor.execute("SELECT * FROM class_section c JOIN course i ON c.course_id = i.id WHERE c.csem = %s AND c.cyear = %s", (semester[0], semester[1]))
    bulletin = cursor.fetchall()

    instructor_list = {}
    for each_class in classes:
        cursor.execute("SELECT fname, lname FROM user WHERE user_id = %s", (each_class['faculty_id'],))
        instructor_list[each_class['faculty_id']] = cursor.fetchone()

    cursor.execute("SELECT * FROM prerequisite p JOIN course c ON p.prereq_id = c.id")    
    prereqs = cursor.fetchall()

    renderer = {
        "cid": "Class ID",
        "csem": "Semester",
        "cyear": "Year",
        "day_of_week": "Day of week",
        "class_time": "Class Time",
        "fid": "Instructor",
        "dname": "Department",
        "cnum": "Course Number",
        "class_section": "Class Section",
        "title": "Title",
        "credits": "Credits",
    }
    cursor.execute('''SELECT * FROM student_courses s JOIN class_section c ON s.class_id = c.class_id 
    AND s.csem = c.csem AND s.cyear = c.cyear JOIN course i ON c.course_id = i.id 
    WHERE s.student_id = %s AND s.cyear = %s AND s.csem = %s ORDER BY c.class_time, CASE c.day_of_week 
    WHEN 'M' THEN 1 
    WHEN 'T' THEN 2 
    WHEN 'W' THEN 3 
    WHEN 'R' THEN 4
    ELSE 5 
    END''', (session['user_id'], semester[1], semester[0]))   
    schedule = cursor.fetchall()

    intervals = [("1:00", 1.0),("1:30", 1.5),
                 ("2:00", 2.0),("2:30", 2.5),
                 ("3:00", 3.0),("3:30", 3.5),
                 ("4:00", 4.0),("4:30", 4.5),
                 ("5:00", 5.0),("5:30", 5.5),
                 ("6:00", 6.0),("6:30", 6.5),
                 ("7:00", 7.0),("7:30", 7.5),
                 ("8:00", 8.0),("8:30", 8.5),
                 ("9:00", 9.0),("9:30", 9.5),]
    week = ['M', 'T', 'W', 'R', 'F']

    times = {}
    for row in schedule:
      time = _calendar_map(row['class_time'])
      times[row['class_id']] = [time[0], time[1], time[2], row['day_of_week']]

    cursor.execute("SELECT * FROM student_courses s JOIN class_section c ON s.class_id = c.class_id JOIN course i ON c.course_id = i.id WHERE s.student_id = %s GROUP BY i.id", (session['user_id'],))
    taken = cursor.fetchall()

    return render_template('registration.html', schedule=schedule, renderer=renderer, instructor_list=instructor_list,
                            classes=classes, prereqs=prereqs, session=session, semester=semester, times=times, 
                            intervals=intervals, week=week, taken=taken, bulletin=bulletin)



####################################################
#                  FACULTY PAGE                    #
####################################################


#faculty login 
@app.route('/faculty', methods=['GET', 'POST'])
def faculty():
  if sessionType() == 1:
    if request.method == "GET":
      return render_template('dashboard.html')
      
    if request.method == "POST": 
        user = get_session['user']
        return render_template('dashboard.html',  user=user)

  else:
    return redirect('/')


#alumni log in
@app.route('/alumnilogging')
def alumnilogging():
    if sessionType() == 2:
      cur = db.cursor(dictionary = True)
      cur.execute("SELECT email, user_address, user_id, user_phoneNUM FROM user WHERE username = %s", (session['username'],))
      data = cur.fetchone()
      db.commit()
      return render_template("alumni.html", title = 'Alumni Logged In', data = data)
    else:
      return redirect('/')


#student log in 
@app.route('/studentlogging')
def studentlogging():
  if sessionType() == 4 or sessionType() == 5:
    cur = db.cursor(dictionary = True)
    cur.execute("SELECT email, user_address, user_id, user_phoneNUM FROM user WHERE username = %s", (session['username'],))
    data = cur.fetchone()
    db.commit()


    #cur.execute("SELECT status FROM student_status WHERE student_id = %s", (session['user_id'],))
    #checksuspended = cur.fetchone()
    #if checksuspended == None:
      #get the students grade
    cur.execute("SELECT grade FROM student_courses WHERE student_id = %s", (session['user_id'],))
    grades = cur.fetchall()
    invalid_grades = ['C', 'D', 'F']
    counter = 0
    for g in grades:
      #print(g)
      if g in invalid_grades:
        #print(g)
        #print(counter)
        counter += 1

    #three grades below a B
    if counter >= 3:
      cur.execute("INSERT into student_status (student_id, status) VALUES (%s, %s)", (session['user_id'], 'Suspended'))
      db.commit()
    else: 
      cur.execute("DELETE from student_status WHERE student_id = %s", (session['user_id'], ))
      db.commit()
        
    cur.execute("SELECT status FROM student_status WHERE student_id = %s", (session['user_id'],))
    suspended = cur.fetchone()
    db.commit()

    return render_template("student.html", title = 'Student Logged In', data = data, suspended = suspended)
  
  else:
    return redirect('/')


#admin log in 
@app.route('/admin')
def admin():
  if sessionType() == 0:
    cur = db.cursor(dictionary = True)
    cur.execute("SELECT email, user_address, user_id, user_phoneNUM FROM user WHERE username = %s", (session['username'],))
    data = cur.fetchone()
    db.commit()
    return render_template("admin.html", title = 'Admin Logged In', data = data)
  else:
    return redirect('/')


#grad sec log in 
student_info = list()
@app.route('/gradsec', methods=['GET', 'POST'])
def gs_student_names():
  if sessionType() == 3:

    cur = db.cursor(dictionary = True)
    students = list()

    cur.execute("SELECT fname, lname, user_id FROM user WHERE user_type = %s OR user_type = %s", (4, 5))
    students = cur.fetchall()
    
    return render_template("student_names.html", students=students)
  
  else:
    return redirect('/')



@app.route('/viewform1/<id>')
def viewform1(id):
  if sessionType() == 0:
    cur = db.cursor(dictionary = True)
    cur.execute("SELECT courseID FROM form1answer WHERE student_id = %s", (id,))
    data = cur.fetchall()
    db.commit()

    cur.execute("SELECT * from course")
    courses = cur.fetchall()
    db.commit()

    return render_template("viewform1.html", data = data, courses = courses)

  else:
    return redirect('/')



@app.route('/updateinfo', methods=['GET', 'POST'])
def updateinfo():
  #connect to the database
  cur = db.cursor(dictionary = True)

  if request.method == 'POST':
    #update the sql database here
    if((request.form["lname"])):
      cur.execute("UPDATE user SET lname = %s WHERE user_id = %s", ( str((request.form["lname"])), session['user_id']))
      db.commit()

    if((request.form["fname"])):
      cur.execute("UPDATE user SET fname = %s WHERE user_id = %s", ( str((request.form["fname"])), session['user_id']))
      db.commit()

    if((request.form["email"])):
      cur.execute("UPDATE user SET email = %s WHERE user_id = %s", ( str((request.form["email"])), session['user_id']))
      db.commit()

    if((request.form["address"])):
      cur.execute("UPDATE user SET user_address = %s WHERE user_id = %s", ( str((request.form["address"])), session['user_id']))
      db.commit()

    if((request.form["phonenum"])):
      cur.execute("UPDATE user SET user_phoneNUM = %s WHERE user_id = %s", ( str((request.form["phonenum"])), session['user_id']))
      db.commit()
    

    #reset the session variables to change if the first and last name was updated
    cur.execute("SELECT username, user_password, user_id, fname, lname FROM user WHERE user_id = %s", (session['user_id'], ))
    data = cur.fetchone()
    db.commit()
    session['fname'] = data['fname']
    session['lname'] = data['lname']
    return redirect('/')




@app.route('/updategrade/<studID>/<courID>', methods=['GET', 'POST'])
def updategrade(studID, courID):
  #connect to the database
  cur = db.cursor(dictionary = True)

  if sessionType() == 0:

    if request.method == 'POST':
      #update grade
      if((request.form["grade"])):
        cur.execute("UPDATE student_courses SET grade = %s WHERE student_id = %s and class_id = %s", ( str((request.form["grade"])), studID, courID))
        db.commit()

    return redirect('/')

  else:
    return redirect('/')





@app.route('/form1', methods=['GET', 'POST'])
def form():
  cur = db.cursor(dictionary = True)
  if sessionType() == 4 or sessionType() == 5:

    if request.method == "GET":
      return render_template("form1.html")

    if request.method == 'POST':
      check = 0
      for i in range(100, 122):
        checkboxes = request.form.getlist(str(i))
        for checkbox in checkboxes:
          if(checkbox == "yes"):
            if (check == 0):
              #cur.execute("DELETE from student_courses WHERE grade = %s and student_id = %s", ('IP', session['user_id'] ))
              #db.commit()
              cur.execute("DELETE from form1answer WHERE student_id = %s", (session['user_id'], ))
              db.commit()
              check +=1

            #cur.execute("SELECT grade FROM student_courses WHERE class_id = %s and student_id = %s", (i,session['user_id']))
            #grade = cur.fetchone()
            #print(grade)
            

            #invalid_grades = ['D', 'F']
            #if grade != None:
              #if grade in invalid_grades:
                  #cur.execute("DELETE from student_courses WHERE class_id = %s", (i, ))
                  #db.commit()
                  #cur.execute("INSERT into student_courses (student_id, class_id, grade) VALUES (%s, %s, %s)", (session['user_id'], i, 'IP'))
                  #db.commit()

            #else:
              #print("reaches the else")
              #cur.execute("INSERT into student_courses (student_id, class_id, grade) VALUES (%s, %s, %s)", (session['user_id'], i, 'IP'))
              #db.commit()

            cur.execute("INSERT into form1answer (student_id, courseID) VALUES (%s, %s)", (session['user_id'], i))
            db.commit()

            #cur.execute("SELECT * from student_courses WHERE class_id = %s and student_id = %s", (i,session['user_id']))
            #data = cur.fetchall()
            
    return redirect('/')

  else:
    return redirect('/')
    #return render_template("form1.html")


@app.route('/student_courseslist')
def studentcourse():
  if sessionType() == 0:
    cur = db.cursor(dictionary = True)

    cur.execute("SELECT class_id FROM student_courses WHERE student_id = %s", (session['user_id'], ))
    course_id = cur.fetchall()
    db.commit()
    return course_id

  else:
    return redirect('/')


@app.route('/facultylist')
def facultylist():
  if sessionType() == 0:
    cur = db.cursor(dictionary = True)

    cur.execute("SELECT * FROM user WHERE user_type = %s", (1, ))
    data = cur.fetchall()
    db.commit()
    return render_template("facultylist.html", data = data)

  else:
    return redirect('/')


@app.route('/gradlist')
def gradlist():
  if sessionType() == 0:
    cur = db.cursor(dictionary = True)

    cur.execute("SELECT * FROM user WHERE user_type = %s", (4, ))
    data = cur.fetchall()
    db.commit()
    cur.execute("SELECT * FROM user WHERE user_type = %s", (5, ))
    phd = cur.fetchall()
    cur.execute("SELECT * FROM phd_req WHERE thesisapproved = %s", ('False', ))
    notappr = cur.fetchall()
    #for i in notappr:
      #print(i)
    db.commit()
    return render_template("gradlist.html", data = data, phd = phd, notappr = notappr)

  else:
    return redirect('/')


@app.route('/approvethesis/<id>')
def approvethesis(id):
  if sessionType() == 0:
    cur = db.cursor(dictionary = True)
    cur.execute("UPDATE phd_req SET thesisapproved = %s WHERE student_id = %s", ('True', id))
    db.commit()
    return redirect('/')
  else:
    return redirect('/')



@app.route('/gradseclist')
def gradseclist():
  if sessionType() == 0:
    cur = db.cursor(dictionary = True)

    cur.execute("SELECT * FROM user WHERE user_type = %s", (3, ))
    data = cur.fetchall()
    db.commit()
    return render_template("gradseclist.html", data = data)
  else:
    return redirect('/')


@app.route('/alumnilist')
def alumnilist():
  if sessionType() == 0:
    cur = db.cursor(dictionary = True)

    cur.execute("SELECT * FROM user WHERE user_type = %s", (2, ))
    data = cur.fetchall()
    db.commit()
    return render_template("alumnilist.html", data = data)
  else:
    return redirect('/')

#beginning of sameen's part

@app.route('/user/<id>/<type>')
def userinfo(id, type):
  if sessionType() == 0:
    cur = db.cursor(dictionary = True)

    cur.execute("SELECT * FROM user WHERE user_id = %s", (id, ))
    data = cur.fetchone()
    db.commit()
    studentcourses = None
    alumnicourses = None
    notappr = None
    suspended = None

    
    if type == '4' or type == '5':
      studentcourses = "student"
      db.commit()
      cur.execute("SELECT * FROM phd_req WHERE thesisapproved = %s", ('False', ))
      notappr = cur.fetchall()
      cur.execute("SELECT grade FROM student_courses WHERE student_id = %s", (id,))
      grades = cur.fetchall()
      invalid_grades = ['C', 'D', 'F']
      counter = 0
      for g in grades:
        #print(g)
        if g in invalid_grades:
          #print(g)
          #print(counter)
          counter += 1

      #three grades below a B
      if counter >= 3:
        cur.execute("INSERT into student_status (student_id, status) VALUES (%s, %s)", (id, 'Suspended'))
        db.commit()
      else: 
        cur.execute("DELETE from student_status WHERE student_id = %s", (id, ))
        db.commit()
        
      cur.execute("SELECT status FROM student_status WHERE student_id = %s", (id,))
      suspended = cur.fetchone()
      db.commit()

 

    if type == '2': 
      alumnicourses = "alumni"
      db.commit()


    #advsior: get the advisees, option to view their form 1, see the phd studnets and approve their thesis

    return render_template("userinfo.html", data = data, alumnicourses = alumnicourses, studentcourses = studentcourses, notappr = notappr, suspended = suspended)
  
  else:
    return redirect('/')


@app.route('/updateuserinfo/<id>', methods=['GET', 'POST'])
def updateuserinfo(id):
  #connect to the database
  cur = db.cursor(dictionary = True)

  if request.method == 'POST':
    #update the sql database here
    if((request.form["lname"])):
      cur.execute("UPDATE user SET lname = %s WHERE user_id = %s", ( str((request.form["lname"])), id))
      db.commit()

    if((request.form["fname"])):
      cur.execute("UPDATE user SET fname = %s WHERE user_id = %s", ( str((request.form["fname"])), id))
      db.commit()

    if((request.form["email"])):
      cur.execute("UPDATE user SET email = %s WHERE user_id = %s", ( str((request.form["email"])), id))
      db.commit()

    if((request.form["address"])):
      cur.execute("UPDATE user SET user_address = %s WHERE user_id = %s", ( str((request.form["address"])), id))
      db.commit()

    if((request.form["phonenum"])):
      cur.execute("UPDATE user SET user_phoneNUM = %s WHERE user_id = %s", ( str((request.form["phonenum"])), id))
      db.commit()
    

    return redirect('/')



@app.route('/assigned', methods=['GET', 'POST'])
def assigned():
  if sessionType() == 0:
    if request.method == "POST":
      cur = db.cursor(dictionary = True)
      student = (int)(request.form["student"])
      advisor = (int)(request.form["advisor"])
      cur.execute("DELETE from student_advisors WHERE studentID = %s ", (student, ))
      db.commit()
      cur.execute("INSERT into student_advisors (studentID, advisorID) VALUES (%s, %s)", (student, advisor))
      db.commit()
      cur.execute("DELETE from need_advisor WHERE student_id = %s ", (student, ))
      return redirect('/')
  else:
    return redirect('/')



@app.route('/assignadvsior')
def assignadvisor():
  if sessionType() == 0:
    cur = db.cursor(dictionary = True)

    cur.execute("SELECT fname, lname, user_id from user where user_type = %s", (1, ))
    advisors = cur.fetchall()

    cur.execute("SELECT fname, lname, user_id from user where user_type = %s", (4, ))
    mstudents = cur.fetchall()

    cur.execute("SELECT fname, lname, user_id from user where user_type = %s", (5, ))
    pstudents = cur.fetchall()

    return render_template("assignadvisor.html", advisors = advisors, mstudents = mstudents, pstudents = pstudents)
  
  else:
    return redirect('/')






@app.route('/graduatethestudent/<id>/<type>', methods=['GET', 'POST'])
def graduatethestudent(id, type):
  if sessionType() == 0: 
    if request.method == "POST":
      cur = db.cursor(dictionary = True)
      cur.execute("UPDATE user SET user_type = %s WHERE user_id = %s", (2, id))
      db.commit()
      if(type == '4'):
        y = 20
      if(type == '5'):
        y = 21
      cur.execute("INSERT into alumni (student_id, degree_id, grad_year) VALUES (%s, %s, %s)", (id, y, 2023))
      db.commit()
      cur.execute("DELETE from student_advisors WHERE studentID = %s ", (id, ))
      db.commit()
      cur.execute("DELETE from students WHERE student_id = %s ", (id, ))
      db.commit()
      return redirect('/')
  
  else:
    return redirect('/')
    


@app.route('/remove/<id>/<type>', methods=['GET', 'POST'])
def removeuser(id, type):
  if sessionType() == 0:
    if request.method == "POST":
      cur = db.cursor(dictionary = True)
      if type == '3': 
        cur.execute("DELETE from user WHERE user_id = %s", (id, ))
        db.commit()
      elif type == '2': 
        cur.execute("DELETE from student_courses WHERE student_id = %s ", (id, ))
        db.commit()
        cur.execute("DELETE from student_status WHERE student_id = %s", (id, ))
        db.commit()
        cur.execute("DELETE from application WHERE student_id = %s", (id, ))
        db.commit()
        cur.execute("DELETE from alumni WHERE student_id = %s", (id, ))
        db.commit()
        cur.execute("DELETE from students WHERE student_id = %s ", (id, ))
        db.commit()
        cur.execute("DELETE from user WHERE user_id = %s", (id, ))
        db.commit()
      elif type == '4' or type == '5': 
        cur.execute("DELETE from student_courses WHERE student_id = %s ", (id, ))
        db.commit()
        cur.execute("DELETE from need_advisor WHERE student_id = %s", (id, ))
        db.commit()
        cur.execute("DELETE from applied_grad WHERE student_id = %s", (id, ))
        db.commit()
        cur.execute("DELETE from application WHERE student_id = %s", (id, ))
        db.commit()
        cur.execute("DELETE from student_status WHERE student_id = %s", (id, ))
        db.commit()
        cur.execute("DELETE from application WHERE student_id = %s", (id, ))
        db.commit()
        cur.execute("DELETE from student_advisors WHERE studentID = %s", (id, ))
        db.commit()
        cur.execute("DELETE from phd_req WHERE student_id = %s", (id, ))
        db.commit()
        cur.execute("DELETE from need_advisor WHERE student_id = %s", (id, ))
        db.commit()
        cur.execute("DELETE from students WHERE student_id = %s ", (id, ))
        db.commit()
        cur.execute("DELETE from user WHERE user_id = %s", (id, ))
        db.commit()
      elif type == '1':
        cur.execute("SELECT studentID FROM student_advisors WHERE advisorID = %s", (id, ))
        students = cur.fetchall()
        for s in students:
          #print(s)
          cur.execute("INSERT into need_advisor (student_id) VALUES (%s)", (s,))
          db.commit()

        cur.execute("DELETE from student_advisors WHERE advisorID = %s", (id, ))
        db.commit()
        cur.execute("DELETE from user WHERE user_id = %s", (id, ))
        db.commit()

      return redirect('/')

  else:
    return redirect('/')





@app.route('/addthestudent', methods=['GET', 'POST'])
def addthestudent():
  if sessionType() == 0:
    if request.method == "GET":
      return render_template("addstudent.html")
    
    if request.method == "POST":
      cur = db.cursor(dictionary = True)
      unm = (request.form["username"])
      passwrd = (request.form["password"])
      fname = (request.form["fname"])
      lname = (request.form["lname"])
      ssn =  (request.form["ssn"])
      email =  (request.form["email"])
      address =  (request.form["address"])
      phone =  (request.form["phone"])
      type = (request.form["dates"])
      admit = (request.form["admityear"])

      if(type == "ms"):
        x = 4
        y = 20
      if(type == "phd"):
        x = 5
        y = 21
    
      while True:
        id = random.randint(10000000, 99999999)
        cur.execute("SELECT user_id FROM user WHERE user_id = %s", (id,))
        if not cur.fetchone():
          break


      cur.execute("SELECT username FROM user WHERE username = %s", (unm, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("userexists.html")

      db.commit()

      db.commit()
      cur.execute("SELECT ssn FROM user WHERE ssn = %s", (ssn, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("userexists.html")

      db.commit()
      cur.execute("SELECT email FROM user WHERE email = %s", (email, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("userexists.html")
      
      cur.execute("INSERT into user (user_id, user_type, fname, lname, username, user_password, user_address, user_phoneNUM, ssn, email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id, x, fname, lname, unm, passwrd, address, phone, ssn, email))
      db.commit()
      cur.execute("INSERT into students (student_id, degree_id, admit_year) VALUES (%s, %s, %s)", (id, y, admit))
      db.commit()
      cur.execute("INSERT into need_advisor (student_id) VALUES (%s)", (id, ))
      db.commit()
      if(x == 5):
        cur.execute("INSERT into phd_req (student_id, thesisapproved) VALUES (%s, %s)", (id, 'False'))
        db.commit()

      return redirect('/')

  else:
    return redirect('/')



@app.route('/applygrad', methods=['GET', 'POST'])
def applygrad():
  if sessionType() == 4 or sessionType() == 5:
  #connect to the database
    cur = db.cursor(dictionary = True)
    if request.method == "GET":
      return render_template("applying.html")

    if request.method == "POST":
      type = (request.form["dates"])
      if(type == "ms"):
        x = 4
        y = 20
      if(type == "phd"):
        x = 5
        y = 21
      cur.execute("INSERT into applied_grad (student_id, dtype) VALUES (%s, %s)", (session['user_id'], y))
      db.commit()
      return render_template("applygrad.html")
  else:
    return redirect('/')



@app.route('/coursehist/<id>', methods=['GET', 'POST'])
def coursehist(id):
  if sessionType() == 0 or sessionType() == 4 or sessionType() == 5 or sessionType() == 2:
  #connect to the database
    cur = db.cursor(dictionary = True)
    if request.method == "POST":
      #cur.execute("SELECT class_id, grade FROM student_courses WHERE student_id = %s", (id, ))
      #data = cur.fetchall()
      #class_ids = [row['class_id'] for row in data]
      #print(data)
      #cur.execute("SELECT id, course_name, course_num, credit_hours from course")
      #cour = cur.fetchall()
      #db.commit()

      #cur.execute("SELECT c.dept_name, c.id, c.course_num, c.course_name, c.credit_hours FROM course c JOIN class_section cs ON cs.course_id = c.id JOIN student_courses sc ON sc.class_id = cs.class_id WHERE cs.class_id IN ({}) GROUP BY c.id".format(','.join(['%s']*len(class_ids))), class_ids)
      #answer = cur.fetchall()

      cur.execute("SELECT DISTINCT c.dept_name, c.id, c.course_num, c.course_name, c.credit_hours, sc.class_id, sc.grade FROM course c JOIN class_section cs ON cs.course_id = c.id JOIN student_courses sc ON sc.class_id = cs.class_id WHERE sc.student_id = %s", (id, ))
      courses = cur.fetchall()
      for a in courses:
        print(a)



      grade_points = 0
      num_courses = 0
      #credits = 0
      cur.execute("SELECT class_id, grade FROM student_courses WHERE student_id = %s", (id, ))
      student_grades = cur.fetchall()
      db.commit()

      #cur.execute("SELECT class_section.class_id, course_id FROM class_section JOIN student_courses ON class_section.class_id = student_courses.class_id WHERE student_courses.student_id = %s", (id,))
      #data2 = cur.fetchall()

      

      for i in range(len(student_grades)):
        #cur.execute("SELECT credit_hours FROM course JOIN class_section ON course.id = class_section.course_id WHERE class_section.class_id = %s", (student_grades[i]['class_id'], ))
        #course_hours = cur.fetchone()
        #cur.execute("Select course_id from class_section where class_id = %s", (student_grades[i]['class_id'], ))
        #cur.execute("SELECT credit_hours FROM course WHERE id = %s", (student_grades[i]['class_id'], ))
        #course_hours = cur.fetchone()
        #credits += course_hours['credit_hours']
        grade = student_grades[i]['grade'] 
        #num_courses = num_courses + 1
        if grade == 'A':
            grade_points = grade_points + 4
            num_courses = num_courses + 1
        if grade == 'A-':
            grade_points = grade_points + 3.7
            num_courses = num_courses + 1
        if grade == 'B+':
            grade_points = grade_points + 3.3
            num_courses = num_courses + 1
        if grade == 'B':
            grade_points = grade_points + 3
            num_courses = num_courses + 1
        if grade == 'B-':
            grade_points = grade_points + 2.7
            num_courses = num_courses + 1
        if grade == 'C+':
            grade_points = grade_points + 2.3
            num_courses = num_courses + 1
        if grade == 'C':
            grade_points = grade_points + 2
            num_courses = num_courses + 1
        if grade == 'C-':
            grade_points = grade_points + 1.7
            num_courses = num_courses + 1
        if grade == 'F':
            grade_points = grade_points + 0
            num_courses = num_courses + 1
      if num_courses == 0:
        num_courses = 1
      gpa = grade_points / num_courses
      gpa = round(gpa, 2)
      return render_template("coursehist.html", id = id, gpa = gpa, courses = courses)
  else:
    return redirect('/')



@app.route('/addfaculty' , methods=['GET', 'POST'])
def addfaculty():
  if sessionType() == 0:
    if request.method == "GET":
      return render_template("addfaculty.html")

    if request.method == "POST":
      cur = db.cursor(dictionary = True)
      unm = (request.form["username"])
      passwrd = (request.form["password"])
      fname = (request.form["fname"])
      lname = (request.form["lname"])
      ssn =  (request.form["ssn"])
      email =  (request.form["email"])
      address =  (request.form["address"])
      phone =  (request.form["phone"])
      type = (int)(request.form["type"])


      while True:
        id = random.randint(10000000, 99999999)
        cur.execute("SELECT user_id FROM user WHERE user_id = %s", (id,))
        if not cur.fetchone():
          break
    
      cur.execute("SELECT username FROM user WHERE username = %s", (unm, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("userexists.html")

      db.commit()

      db.commit()
      cur.execute("SELECT ssn FROM user WHERE ssn = %s", (ssn, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("userexists.html")

      db.commit()
      cur.execute("SELECT email FROM user WHERE email = %s", (email, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("userexists.html")
      
      cur.execute("INSERT into user (user_id, user_type, fname, lname, username, user_password, user_address, user_phoneNUM, ssn, email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id, type, fname, lname, unm, passwrd, address, phone, ssn, email))
      db.commit()
      return redirect('/')

  else:
    return redirect('/')


@app.route('/addgradsec' , methods=['GET', 'POST'])
def addgradsec():
  if sessionType() == 0:
    if request.method == "GET":
      return render_template("addgradsec.html")

    if request.method == "POST":
      cur = db.cursor(dictionary = True)
      unm = (request.form["username"])
      passwrd = (request.form["password"])
      fname = (request.form["fname"])
      lname = (request.form["lname"])
      ssn =  (request.form["ssn"])
      email =  (request.form["email"])
      address =  (request.form["address"])
      phone =  (request.form["phone"])
      type = (int)(request.form["type"])

      while True:
        id = random.randint(10000000, 99999999)
        cur.execute("SELECT user_id FROM user WHERE user_id = %s", (id,))
        if not cur.fetchone():
          break
    
      cur.execute("SELECT username FROM user WHERE username = %s", (unm, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("userexists.html")

      db.commit()

      db.commit()
      cur.execute("SELECT ssn FROM user WHERE ssn = %s", (ssn, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("userexists.html")

      db.commit()
      cur.execute("SELECT email FROM user WHERE email = %s", (email, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("userexists.html")
      
      cur.execute("INSERT into user (user_id, user_type, fname, lname, username, user_password, user_address, user_phoneNUM, ssn, email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id, type, fname, lname, unm, passwrd, address, phone, ssn, email))
      db.commit()
      return redirect('/')

  else:
    return redirect('/')



@app.route('/addalumni' , methods=['GET', 'POST'])
def addalumni():
  if sessionType() == 0:
    if request.method == "GET":
      return render_template("addalumni.html")

    if request.method == "POST":
      cur = db.cursor(dictionary = True)
      unm = (request.form["username"])
      passwrd = (request.form["password"])
      fname = (request.form["fname"])
      lname = (request.form["lname"])
      ssn =  (request.form["ssn"])
      email =  (request.form["email"])
      address =  (request.form["address"])
      phone =  (request.form["phone"])
      type = (int)(request.form["type"])
      degree = (int)(request.form["dates"])
      year = (int)(request.form["gradyear"])

      while True:
        id = random.randint(10000000, 99999999)
        cur.execute("SELECT user_id FROM user WHERE user_id = %s", (id,))
        if not cur.fetchone():
          break
    
      cur.execute("SELECT username FROM user WHERE username = %s", (unm, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("userexists.html")

      db.commit()

      db.commit()
      cur.execute("SELECT ssn FROM user WHERE ssn = %s", (ssn, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("userexists.html")

      db.commit()
      cur.execute("SELECT email FROM user WHERE email = %s", (email, ))
      data = cur.fetchone()
      if(data != None):
        return render_template("userexists.html")
      
      cur.execute("INSERT into user (user_id, user_type, fname, lname, username, user_password, user_address, user_phoneNUM, ssn, email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id, type, fname, lname, unm, passwrd, address, phone, ssn, email))
      db.commit()
      cur.execute("INSERT into alumni (student_id, degree_id, grad_year) VALUES (%s, %s, %s)", (id, degree, year))
      db.commit()
      return redirect('/')

  else:
    return redirect('/')





@app.route('/logout')
def logout():
  session.pop('username', None)
  session.pop('user_id', None)
  session.pop('fname', None)
  session.pop('lname', None)
  session.pop('type', None)
  session.clear()
  return redirect('/')




#Faculty in department and can review Form 1
#For phD students they have to approve (pass) the phd thesis
#they can view their advisees' transcript but cannot update transcript.

@app.route('/faculty/login', methods=['GET', 'POST'])
def faculty_login():
    print(f'method is: ', request.method)


    if request.method == "GET":
        return render_template('faculty_login.html')
            
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        
        
        # try to login user 
        if len(username) < 1 : 
            flash("Username cannot be blank", category="danger")
            return redirect('login')
        elif len(password) < 1: 
            flash("Password cannot be blank", category="danger")
            return redirect('login')
        else:
            try:
                sql = '''SELECT * from user where username=%s AND user_password=%s '''
                
                print(f'DATA: {username}: {password}')
                cursor= db.cursor(dictionary=True)
                cursor.execute(sql, (username, password))
                result = cursor.fetchone()
                if result != None: 
                    set_session(user=result)
                    flash(f'Welcome {username}. \n You have been succesfully logged in', category='success')
                    return redirect('dashboard')
                    
                else:
                    flash(f'Username and password do not match', category='danger')
                    return redirect('login')
                
            except connection.Error as e: 
                print(f'Error: {e}')





@app.route('/faculty/dashboard', methods=['GET', 'POST'])
def faculty_dashboard():
  if sessionType() == 1:
    if request.method == "GET":
      return render_template('dashboard.html')
      
    if request.method == "POST": 
        user = get_session['user']
        return render_template('dashboard.html',  user=user)

  else:
    return redirect('/')
    



@app.route('/faculty/advisees/')
def faculty_advisees():
  if sessionType() == 1:
    if session.get('user_id') == None:
      return redirect(url_for('login'))
      # check if the user is logged in and is a faculty advisor
    
    else:
      return render_template('students.html')
  
  else:
    return redirect('/')


@app.route('/faculty/advisees/phd')
def phd_students():
  if sessionType() == 1:
    if session.get('user_id') == None:
      return redirect(url_for('login'))
    # check if the user is logged in and is a faculty advisor
    
    else:
    # get advisor id from login session 
      adv_id = session['user_id']
    # lets write a query to fetch all PhD students that belong to this particular advisor
      query = '''select user.user_id, user.user_type, user.fname, user.lname, user.email, student_advisors.studentID, student_advisors.advisorID, students.student_id, students.degree_id, 
            user_type.id, user_type.name as degree_name
            from user 
            JOIN student_advisors ON  user.user_id = student_advisors.studentID
            JOIN students ON  student_advisors.studentID = students.student_id
            JOIN user_type ON user.user_type = user_type.id
            where student_advisors.advisorID =%s AND user_type.id = 5'''


      cursor= db.cursor(dictionary=True)

      cursor.execute(query,(adv_id,) )
      result =cursor.fetchall()
      cursor.close()

      return render_template('phd_students.html', students=result)

  else:
    return redirect('/')

@app.route('/faculty/advisees/<transcript_id>')
def faculty_transcript(transcript_id): 
  if sessionType() == 1:
    if session.get('user_id') == None:
      return redirect(url_for('login'))
    # check if the user is lgged in and is a faculty advisor
    
    else:
      if transcript_id != None:
          transcript_id = int(transcript_id)

          query = '''
        select user.user_id, user.user_type, user.fname, user.lname, user.email, student_advisors.studentID, student_advisors.advisorID, students.student_id, students.degree_id, 
            user_type.id, user_type.name as degree_name, student_courses.student_id, student_courses.class_id, student_courses.grade, course.id, course.dept_name, course.course_num, course.course_name, course.credit_hours
            from user 
            JOIN student_advisors ON  user.user_id = student_advisors.studentID
            JOIN students ON  student_advisors.studentID = students.student_id
            JOIN user_type ON user.user_type = user_type.id
            JOIN student_courses ON user.user_id = student_courses.student_id
            JOIN course ON course.id = student_courses.class_id
            where user.user_id=%s 
        '''
       
        
          cursor= db.cursor(dictionary=True)

          cursor.execute(query,(transcript_id,) )
          result =cursor.fetchall()
          cursor.close()

          return render_template('student_transcript.html', transcript=result)

  else:
    return redirect('/')

@app.route('/faculty/advisees/formone/<user_id>', methods=['GET', 'POST'])
def faculty_form(user_id): 
    
  if sessionType() == 1:
    if session.get('user_id') == None:
      return redirect(url_for('login'))
    # check if the user is logged in and is a faculty advisor
    
    else:
      if request.method =="GET":
        if user_id != None:
            user_id = int(user_id)

            query = '''
              SELECT
              user.user_id,  
              user.fname, user.lname, user.email,
              course.id AS class_id,
              course.course_name,
              course.course_num, 
              phd_req.student_id, phd_req.thesisapproved
            FROM
              user
              JOIN student_advisors ON user.user_id = student_advisors.studentID
              JOIN students ON student_advisors.studentID = students.student_id
              JOIN form1answer ON user.user_id = form1answer.student_id
              JOIN course ON course.id = form1answer.courseID
              JOIN phd_req ON phd_req.student_id = students.student_id

            WHERE
              user.user_id = %s; 
          '''
        
          
            cursor= db.cursor(dictionary=True)

            cursor.execute(query,(user_id,) )
            result =cursor.fetchall()
            cursor.close()

            return render_template('review_formone.html', form_one=result)
    

      elif request.method == "POST":
      # get the form values 
        print("Student ID received:", request.form['student_id'])

        student= int(request.form['student_id'])
        if request.form['status'] == None:
          flash(f"Please approve to continue", category="danger")
          return render_template('review_formone.html', form_one=result)
        else:
          strstatus = request.form['status']
          if strstatus == "True": 
            status = True
          else:
            status = False
          print(f'student: {student}, thesis: {status}')
          query= "UPDATE phd_req SET thesisapproved = %s WHERE student_id = %s"


          cursor= db.cursor()
          cursor.execute(query, (strstatus, student))


          db.commit()
        # result =cursor.fetchall()


          query = '''
              SELECT
              user.user_id,  
              user.fname, user.lname, user.email,
              course.id AS class_id,
              course.course_name,
              course.course_num, 
              phd_req.student_id, phd_req.thesisapproved
            FROM
              user
              JOIN student_advisors ON user.user_id = student_advisors.studentID
              JOIN students ON student_advisors.studentID = students.student_id
              JOIN form1answer ON user.user_id = form1answer.student_id
              JOIN course ON course.id = form1answer.courseID
              JOIN phd_req ON phd_req.student_id = students.student_id

            WHERE
              user.user_id = %s; 
          '''
        
         
          
          cursor= db.cursor(dictionary=True)

          cursor.execute(query,(user_id,) )
          result =cursor.fetchall()
          cursor.close()
          db.commit()
          flash(f'Student Thesis has been approved!', category="success")

          return render_template('review_formone.html', form_one=result)
  else:
    return redirect('/')

      


@app.route('/faculty/advisees/formone/masters/<user_id>', methods=['GET', 'POST'])
def faculty_form_masters(user_id): 
    
  if sessionType() == 1:
    if session.get('user_id') == None:
      return redirect(url_for('login'))
    # check if the user is logged in and is a faculty advisor
    
    else:
      if request.method =="GET":
        if user_id != None:
            user_id = int(user_id)

            query = '''
              SELECT
              user.user_id,  
              user.fname, user.lname, user.email,
              course.id AS class_id,
              course.course_name,
              course.course_num
            FROM
              user
              JOIN student_advisors ON user.user_id = student_advisors.studentID
              JOIN students ON student_advisors.studentID = students.student_id
              JOIN form1answer ON user.user_id = form1answer.student_id
              JOIN course ON course.id = form1answer.courseID

            WHERE
              user.user_id = %s; 
          '''
        
          
            cursor= db.cursor(dictionary=True)

            cursor.execute(query,(user_id,) )
            result =cursor.fetchall()
            cursor.close()

            return render_template('review_formone_masters.html', form_one=result)
  else:
    return redirect('/')



@app.route('/faculty/advisees/masters')
def master_students():

  if sessionType() == 1:
    if session.get('user_id') == None:
      return redirect(url_for('login'))
    # check if the user is logged in and is a faculty advisor
    
    else:
    # get advisor id from login session 
      adv_id = session['user_id']
    # lets write a query to fetch all PhD students that belong to this particular advisor
      query = '''select user.user_id, user.user_type, user.fname, user.lname, user.email, student_advisors.studentID, student_advisors.advisorID, students.student_id, students.degree_id, 
            user_type.id, user_type.name as degree_name
            from user 
            JOIN student_advisors ON  user.user_id = student_advisors.studentID
            JOIN students ON  student_advisors.studentID = students.student_id
            JOIN user_type ON user.user_type = user_type.id
            where student_advisors.advisorID =%s AND user_type.id = 4'''


      cursor= db.cursor(dictionary=True)

      cursor.execute(query,(adv_id,) )
      result =cursor.fetchall()
      cursor.close()

      return render_template('master_students.html', students=result)
  else:
    return redirect('/')




@app.route('/student/<student_id>', methods=['GET', 'POST'])
def gs_student_data(student_id):
  if sessionType() == 3:

    cur = db.cursor(dictionary = True)

    degree = list()

    cur.execute("SELECT fname, lname, user_id, user_address, user_phoneNUM, email FROM user WHERE user_id = %s", (student_id, ))
    student_name = cur.fetchall()
    student_info.insert(0, student_name)
    eligible = {'eligible': 'True', 'reason': []}
    student_info.insert(1, eligible)

    # get degree_id
    cur.execute("SELECT degree_id FROM students WHERE student_id = %s", (student_id, ))
    degree = cur.fetchall()
    if not degree:
        degree = 0
    student_info.insert(2, degree[0])

    # get courses and grades
    cur.execute("SELECT class_id, grade FROM student_courses WHERE student_id = %s", (student_id, ))
    student_grades = cur.fetchall()
    if not student_grades:
        student_grades = list()
    student_info.insert(3, student_grades)

    # get gpa and credit hours
    # counters for grades
    grade_points = 0
    total_credit_hours = 0
    num_courses = 0
    bad_grade_ctr = 0
    req_courses_ctr = 0
    outside_courses_ctr = 0
    cs_courses_ctr = 0
    cs_credit_hours = 0

    for i in range(len(student_grades)):
        cur.execute("SELECT credit_hours FROM course JOIN class_section ON course.id = class_section.course_id WHERE class_section.class_id = %s", (student_grades[i]['class_id'], ))
        course_hours = cur.fetchone()
        cur.execute("Select course_id from class_section where class_id = %s", (student_grades[i]['class_id'], ))
        course_id = cur.fetchone()
        if course_id == 100 or 101 or 102:
            req_courses_ctr = req_courses_ctr + 1
        if course_id == 119 or 120 or 121:
            outside_courses_ctr = outside_courses_ctr + 1
        if course_id != 119 or 120 or 121:
            cs_courses_ctr = cs_courses_ctr + 1
            cs_credit_hours = cs_credit_hours + course_hours[0]['credit_hours']
        total_credit_hours = total_credit_hours + course_hours[0]['credit_hours']
        grade = student_grades[i]['grade'] 
        
        if grade == 'A':
            grade_points = grade_points + 4
            num_courses = num_courses + 1
        if grade == 'A-':
            grade_points = grade_points + 3.7
            num_courses = num_courses + 1
        if grade == 'B+':
            grade_points = grade_points + 3.3
            num_courses = num_courses + 1
        if grade == 'B':
            grade_points = grade_points + 3
            num_courses = num_courses + 1
        if grade == 'B-':
            grade_points = grade_points + 2.7
            bad_grade_ctr = bad_grade_ctr + 1
            num_courses = num_courses + 1
        if grade == 'C+':
            grade_points = grade_points + 2.3
            bad_grade_ctr = bad_grade_ctr + 1
            num_courses = num_courses + 1
        if grade == 'C':
            grade_points = grade_points + 2
            bad_grade_ctr = bad_grade_ctr + 1
            num_courses = num_courses + 1
        if grade == 'C-':
            grade_points = grade_points + 1.7
            bad_grade_ctr = bad_grade_ctr + 1
            num_courses = num_courses + 1
        if grade == 'F':
            grade_points = grade_points + 0
            bad_grade_ctr = bad_grade_ctr + 1
            num_courses = num_courses + 1
    if num_courses == 0:
       num_courses = 1
    gpa = grade_points / num_courses
    gpa = round(gpa, 2)
    gpa_dict = {'gpa': gpa}
    total_credit_hours_dict = {'total_credit_hours': total_credit_hours}
    student_info.insert(4, gpa_dict)
    student_info.insert(5, total_credit_hours_dict)
    if bad_grade_ctr >= 3:
        cur.execute("INSERT INTO student_status VALUES (%s, %s)", (student_id, "suspended"))
        gs_all_suspended()

    # check if they've applied for graduation
    cur.execute("SELECT * FROM applied_grad WHERE student_id = %s", (student_id, ))
    applied = cur.fetchall()
    if not applied:
       student_info[1]['eligible'] = 'False'
       student_info[1]['reason'].append('Has not applied to graduate')

    # requirements for master's students
    if student_info[2]['degree_id'] == 20:
        # check gpa
        if student_info[4]['gpa'] < 3.0:
            student_info[1]['eligible'] = 'False'
            student_info[1]['reason'].append('Has not met GPA requirement')
        # check credit hours
        if student_info[5]['total_credit_hours'] < 30:
            student_info[1]['eligible'] = 'False'
            student_info[1]['reason'].append('Has not met credit hour requirement')
        # check for grades below a B
        if bad_grade_ctr > 2:
            student_info[1]['eligible'] = 'False'
            student_info[1]['reason'].append('Has 2+ grades below a B')
        # check for required courses
        if req_courses_ctr < 3:
            student_info[1]['eligible'] = 'False'
            student_info[1]['reason'].append('Has not taken required courses')
        # check for outside courses
        if outside_courses_ctr < 2:
            student_info[1]['eligible'] = 'False'
            student_info[1]['reason'].append('Has not taken enough classes outside of CS')

    # requirements for phd students
    if student_info[2]['degree_id'] == 21:
        # check gpa
        if student_info[4]['gpa'] < 3.5:
            student_info[1]['eligible'] = 'False'
            student_info[1]['reason'].append('Has not met GPA requirement')
        # check credit hours
        if student_info[5]['total_credit_hours'] < 36:
            student_info[1]['eligible'] = 'False'
            student_info[1]['reason'].append('Has not met credit hour requirement')
        # check for grades below a B
        if bad_grade_ctr > 1:
            student_info[1]['eligible'] = 'False'
            student_info[1]['reason'].append('Has 1+ grades below a B')
        # check for 30 credits of CS courses
        if cs_credit_hours < 30:
            student_info[1]['eligible'] = 'False'
            student_info[1]['reason'].append('Has not met CS course credit requirement')

    # check if thesis is approved for phd 
    if student_info[2]['degree_id'] == 21:
      cur.execute("SELECT thesisapproved FROM phd_req WHERE student_id = %s", (student_id, ))
      approved = cur.fetchall()
      student_info.append(approved)
      if approved[0]['thesisapproved'] == 'False':
        student_info[1]['eligible'] = 'False'
        student_info[1]['reason'].append('Thesis has not been approved')

    # get advisor
    cur.execute("SELECT advisorID FROM student_advisors WHERE studentID = %s", (student_id, ))
    advisor_id = cur.fetchall()

    print(student_info[1]['reason'])

    if not advisor_id:
        advisor_name = [{'fname': "N/A"}]
        student_info.insert(6, advisor_name)
        return render_template ("student_data.html", student_info=student_info)
    
    cur.execute("SELECT fname, lname FROM user WHERE user_id = %s", (advisor_id[0]['advisorID'], ))
    advisor_name = cur.fetchall()
    student_info.insert(6, advisor_name)
    
    return render_template ("student_data.html", student_info=student_info)
  
  else:
    return redirect('/')


@app.route('/graduate/<student_id>')
def gs_graduate(student_id):
  if sessionType() == 3:
    data = list()
    data.insert(0, student_id)

    cur = db.cursor(dictionary = True)

    # get degree_id
    cur.execute("SELECT degree_id FROM students WHERE student_id = %s", (student_id, ))
    degree_id = cur.fetchall()
    data.insert(1, degree_id)

    cur.execute("SELECT fname, lname, user_id FROM user WHERE user_id = %s", (student_id, ))
    name = cur.fetchall()
    data.insert(2, name)

    # gets current year
    today = datetime.date.today()
    year = today.year

    cur.execute("INSERT INTO alumni (student_id, degree_id, grad_year) VALUES (%s, %s, %s)", (student_id, data[1][0]['degree_id'], year))
    cur.execute("DELETE FROM students WHERE student_id = %s", (student_id, ))
    cur.execute("UPDATE user SET user_type = %s WHERE user_id = %s", (2, student_id))

    return render_template("graduate.html", data=data)

  else:
    return redirect('/')



@app.route('/all_suspended')
def gs_all_suspended():
  if sessionType() == 3:
    cur = db.cursor(dictionary = True)
    suspended_students_names = list()

    cur.execute("SELECT student_id FROM student_status")
    all_suspended = cur.fetchall()

    for x in range(len(all_suspended)):
        cur.execute("SELECT fname, lname FROM user WHERE user_id = %s", (all_suspended[x]['student_id'], ))
        name = cur.fetchall()
        suspended_students_names.append(name)

    return render_template("suspension.html", suspended_students_names=suspended_students_names)
  else:
    return redirect('/')



@app.route('/assign_advisor/<student_id>', methods=['GET', 'POST'])
def gs_assign_advisor(student_id):
  if sessionType() == 3:
    cur = db.cursor(dictionary = True)

    if request.method == "POST":
        advisor_id = request.form.get("advisor_id")
        cur.execute("INSERT INTO student_advisors VALUES (%s, %s)", (student_id, advisor_id))

    # get student name
    cur.execute("SELECT fname, lname, user_id, user_address, user_phoneNUM, email FROM user WHERE user_id = %s", (student_id, ))
    student = cur.fetchall()

    # get advisor names
    cur.execute("SELECT fname, lname, user_id FROM user WHERE user_type = %s", (1, ))
    advisors = cur.fetchall()

    return render_template("assign_advisor.html", advisors=advisors, student=student)

  else:
    return redirect('/')


####################################################
#                  APPLICATION                    #
####################################################

@app.route('/welcome')
def welcome():
    cursor = db.cursor(dictionary = True)
    
    cursor.execute("SELECT fname FROM user WHERE user_id = %s", (session['user_id'],))
    name = cursor.fetchall()
    print(name)

    cursor.execute("SELECT fname, student_id, semester, s_year FROM applications INNER JOIN user ON applications.student_id = user.user_ID WHERE status = 'review'")
    apps = cursor.fetchall()
    print(apps)

    return render_template("applicant.html", apps = apps, name = name['fname'])

@app.route('/application', methods=['GET', 'POST'])
def application():
   cursor = db.cursor(dictionary=True) 
   cursor.execute("SELECT * FROM user WHERE user_id = %s", (session['user_id'],))
   info = cursor.fetchone()
   if request.method == 'POST':
       cursor = db.cursor(dictionary=True)
       prior_bac_deg_gpa = request.form["prior_bac_deg_gpa"]
       prior_bac_deg_major = request.form["prior_bac_deg_major"]
       prior_bac_deg_year = request.form["prior_bac_deg_year"]
       prior_bac_deg_university = request.form["prior_bac_deg_university"]
       prior_ms_deg_gpa = request.form["prior_ms_deg_gpa"]
       prior_ms_deg_major = request.form["prior_ms_deg_major"]
       prior_ms_deg_year = request.form["prior_ms_deg_year"]
       prior_ms_deg_university = request.form["prior_ms_deg_university"]
       gre_verbal = request.form["GRE_verbal"]
       gre_year = request.form["GRE_year"]
       gre_quantitative = request.form["GRE_quantitative"]
       gre_advanced_score = request.form["GRE_advanced_score"]
       gre_advanced_subject = request.form["GRE_advanced_subject"]
       toefl_score = request.form["TOEFL_score"]
       toefl_date = request.form["TOEFL_date"]
       interest = request.form["interest"]
       experience = request.form["experience"]
       semester = request.form["semester"]
       degree_type = request.form["degree_type"]
       s_year = request.form["s_year"]
       this = session["user_id"]
       cursor.execute("INSERT INTO applications VALUES ('incomplete', %s, %s, %s, %s, '', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '', %s, %s, %s, %s,'sent','not decided')", 
                      (this, semester, s_year, degree_type, prior_bac_deg_gpa, prior_bac_deg_major, prior_bac_deg_year, prior_bac_deg_university, gre_verbal, 
                       gre_year, gre_quantitative, gre_advanced_score, gre_advanced_subject, toefl_score, toefl_date, interest, experience, prior_ms_deg_gpa, prior_ms_deg_major, prior_ms_deg_year, prior_ms_deg_university))
      
      
       uid = session["user_id"]
       
       rname = request.form["field_rName"]
       affil = request.form["field_affil"]
       email = request.form["field_email"]

       rname1 = request.form["field_rName1"]
       affil1 = request.form["field_affil1"]
       email1 = request.form["field_email1"]

       rname2 = request.form["field_rName2"]
       affil2 = request.form["field_affil2"]
       email2 = request.form["field_email2"]
       
       cursor.execute("INSERT INTO letter (user_id, letter_id, contents, recommenderName, recommenderAffil, recommenderEmail,  recommenderName1, recommenderAffil1, recommenderEmail1,  recommenderName2, recommenderAffil2, recommenderEmail2) VALUES (%s, %s, 'please', %s, %s, %s,%s,%s,%s,%s,%s,%s)", (uid, letterID, rname, affil, email,  rname1, affil1, email1,  rname2, affil2, email2,))
      
       db.commit()
       checkComplete()
       
       return render_template("complete.html")
   return render_template("application.html", info = info)


@app.route('/infoViewer')
def infoViewer():
   cursor = db.cursor(dictionary = True)
   cursor.execute("SELECT * FROM user WHERE user_id = %s", (session['user_id'],))
   info = cursor.fetchone()
   return render_template("updateinfo.html", info = info)

@app.route('/view')
def view():
 cursor = db.cursor(dictionary=True)
 this = session["user_id"]
 cursor.execute("SELECT * FROM user INNER JOIN applications on user_id = student_id where user_id = %s;", (this,))
 data = cursor.fetchall()
 return render_template("view.html", content = data)

@app.route('/incomplete',  methods = ["POST", "GET"])
def incomplete():
   cursor = db.cursor(dictionary=True) 
   cursor.execute("SELECT * FROM user WHERE user_id = %s", (session['user_id'],))
   info = cursor.fetchone()
   if request.method == 'POST':
       cursor = db.cursor(dictionary=True)
       prior_bac_deg_gpa = request.form["prior_bac_deg_gpa"]
       prior_bac_deg_major = request.form["prior_bac_deg_major"]
       prior_bac_deg_year = request.form["prior_bac_deg_year"]
       prior_bac_deg_university = request.form["prior_bac_deg_university"]
       prior_ms_deg_gpa = request.form["prior_ms_deg_gpa"]
       prior_ms_deg_major = request.form["prior_ms_deg_major"]
       prior_ms_deg_year = request.form["prior_ms_deg_year"]
       prior_ms_deg_university = request.form["prior_ms_deg_university"]
       gre_verbal = request.form["GRE_verbal"]
       gre_year = request.form["GRE_year"]
       gre_quantitative = request.form["GRE_quantitative"]
       gre_advanced_score = request.form["GRE_advanced_score"]
       gre_advanced_subject = request.form["GRE_advanced_subject"]
       toefl_score = request.form["TOEFL_score"]
       toefl_date = request.form["TOEFL_date"]
       interest = request.form["interest"]
       experience = request.form["experience"]
       semester = request.form["semester"]
       degree_type = request.form["degree_type"]
       s_year = request.form["s_year"]
       this = session["user_id"]
       cursor.execute("INSERT INTO applications VALUES ('incomplete', %s, %s, %s, %s, '', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '', %s, %s, %s, %s,'sent','not decided')", 
                      (this, semester, s_year, degree_type, prior_bac_deg_gpa, prior_bac_deg_major, prior_bac_deg_year, prior_bac_deg_university, gre_verbal, 
                       gre_year, gre_quantitative, gre_advanced_score, gre_advanced_subject, toefl_score, toefl_date, interest, experience, prior_ms_deg_gpa, prior_ms_deg_major, prior_ms_deg_year, prior_ms_deg_university))
      #  global letterID
      #  letterID += 2
      
       uid = session["user_id"]
       
       rname = request.form["field_rName"]
       affil = request.form["field_affil"]
       email = request.form["field_email"]

       rname1 = request.form["field_rName1"]
       affil1 = request.form["field_affil1"]
       email1 = request.form["field_email1"]

       rname2 = request.form["field_rName2"]
       affil2 = request.form["field_affil2"]
       email2 = request.form["field_email2"]
       
       cursor.execute("INSERT INTO letter (user_id, letter_id, contents, recommenderName, recommenderAffil, recommenderEmail,  recommenderName1, recommenderAffil1, recommenderEmail1,  recommenderName2, recommenderAffil2, recommenderEmail2) VALUES (%s, %s, 'please', %s, %s, %s,%s,%s,%s,%s,%s,%s)", (uid, letterID, rname, affil, email,  rname1, affil1, email1,  rname2, affil2, email2,))
       db.commit()
       return redirect('/welcome')
   return render_template("application.html", info = info)
 
@app.route('/reviews')
def reviews():
   cursor = db.cursor(buffered = True)
  #  cursor.execute("SELECT student_id, semester, s_year FROM applications WHERE student_id /NOT IN (SELECT review_id FROM review WHERE student_id = %s) AND status ='review'", (session['user_id'],))
   cursor.execute("SELECT student_id, semester, s_year FROM applications WHERE status = 'review' ")
   info = cursor.fetchall()
   return render_template("review.html", applicants = info)

@app.route('/reviews/<student_id>', methods=['GET','POST'])
def review(student_id):
    if request.method == 'POST':
        cursor = db.cursor(dictionary = True, buffered = True)
        decision = request.form.getlist('decision')
        decision = decision[0]
        print(decision)
        deficiency_course = request.form["dcourse"]
        reason_reject = request.form['reason']
        GAS_comment = request.form['comment']
        advisor = request.form['radvisor']
        cursor.execute("SELECT semester, s_year FROM applications WHERE student_id = %s", (student_id,))
        info = cursor.fetchone()
        cursor.execute("INSERT INTO review (student_id, review_id, p_semester, p_year, rev_rating, deficiency_course, reason_reject, GAS_comment, decision, recom_advisor) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (session['user_id'],student_id,  info['semester'], info['s_year'], "1", deficiency_course, reason_reject, GAS_comment, decision, advisor))
        db.commit()
        return redirect('/')
    cursor = db.cursor(buffered = True)
    cursor.execute("SELECT * FROM applications WHERE student_id = %s", (student_id,))
    appinfo = cursor.fetchall()
    cursor.execute("SELECT fname, lname FROM user WHERE user_id = %s", (student_id,))
    name = cursor.fetchone()
    info = []
    for data in appinfo:
        info.extend(data)
    info.extend(name)
    print(appinfo)
    print(info)
    return render_template("appreview.html", appinfo = info, names = name)

@app.route('/gsview')
def gsview():
   cursor = db.cursor(buffered = True)
   cursor.execute("SELECT * from user INNER JOIN applications ON user_id = student_id WHERE user_type = 6")
   appinfo = cursor.fetchone()
   return render_template("gsview.html", appinfo = appinfo)

@app.route('/finalDecision/<student_id>', methods = ["POST", "GET"])
def finalDecision(student_id):
  if request.method == "POST": 
    print("this")
    cursor = db.cursor(dictionary=True, buffered = True)
    cursor.execute("SELECT semester, s_year FROM applications WHERE student_id = %s", (student_id,))
    info = cursor.fetchone()

    print(request.form["Decision"])
    print(request.form["Transcript"])
    print(request.form["Student"])
    cursor.execute("UPDATE applications SET status = %s, transcript = %s, student = %s WHERE UID = %s", (request.form["Decision"], request.form["Transcript"], request.form["Student"], student_id))
    db.commit()
    return render_template("final.html")
  return render_template("final.html")
#make into a student if yes

app.run(host='0.0.0.0', port=8080)
