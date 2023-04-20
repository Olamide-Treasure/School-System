from flask import Flask, flash, session, render_template, redirect, url_for, request
from datetime import datetime, date

import random
import mysql.connector

app = Flask('app')
app.secret_key = 'STINKY_RICE_THOUSAND_YEARS_EGG'


mydb = mysql.connector.connect(
    host = "regs-team15.crdbforhxr2l.us-east-1.rds.amazonaws.com",
    user = "admin",
    password = "1CrazyRaccoon?!",
    database = "uni"
)

# def _refresh():
#     global mydb
#     mydb.close()
#     mydb = mysql.connector.connect(
#     host = "regs-team15.crdbforhxr2l.us-east-1.rds.amazonaws.com",
#     user = "admin",
#     password = "1CrazyRaccoon?!",
#     database = "uni"
# )

def _process_time(class_time):
    time_list = class_time.split("-")

    start_time = float(time_list[0][0:2])
    if str(time_list[0][3]) != '0':
        start_time += 0.5

    end_time = float(time_list[1][0:2])
    if str(time_list[1][3]) != '0':
        end_time += 0.5

    return start_time, end_time

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

# Home page
@app.route('/')
@app.route('/<path:id>')
def home(id='/'):
    if 'id' not in session and id !='/': 
        # Logged out and in a session, redirect back to home
        return redirect('/')
    elif 'id' not in session and id == '/':
        # Logged out and in home, display landing page
        return render_template('landing.html', session=session)
    elif id.isdigit() and 'id' in session and int(id) == int(session['id']):
       # Logged in and in correct session
         return render_template('landing.html', logged=True, session =session)
    else:
         # Logged in and went to home or wrong session, redirect to correct session
        return redirect(url_for('home', id=session['id']))
       

 
# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Connect to database and get form variables
        try: 
            cursor = mydb.cursor(dictionary=True)
            id = request.form["id"]
            password = request.form["password"]
        except:
            flash("Error while connecting to database. Please try again", "error")
            return render_template('login.html') 
        

        # Check if there's any input:
        if id == "" or password == "":
            flash("Please enter your username and password", "error")
            return render_template('login.html') 
        
        
        # Error checking, if id is in the correct format 
        if not id.isdigit():
            flash("Please enter your ID in the correct format of 8-digit integer", "error")
            return render_template('login.html') 
        
        try: 
            cursor.execute("SELECT uni_id, user_pass, user_type FROM Users WHERE uni_id = (%s) AND user_pass = (%s) ", (id, password))
            data = cursor.fetchone()            
            # If data retrieved is not empty, that means it's correct, redirect to home page and set up session variable
            if data:
                # Set session variables
                session['id'] = data['uni_id']
                session['type'] = data['user_type']
                session['registration'] = []
                return redirect(url_for('account', id=id))
            else: # Otherwise, flash error message
                flash('Error! Invalid username or password', "error")
        except:
            flash("Error while logging in. Please try again", "error")

    return render_template('login.html')

# Logout route
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('home'))

# Route for signing up
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST' and 'id' in session and session['type'] =='administrator':
        # Connect to database and retrieve values
        cursor = mydb.cursor(dictionary=True)
        fname = request.form["fname"]
        lname = request.form["lname"]
        password = request.form["password"]
        bday = request.form["bday"]
        address = request.form["address"]
        user_type = request.form["user_type"]

        # Check if all values are entered
        if password == "" or fname == "" or lname == "" or bday == "" or address == "" or user_type == "":
            flash("Error. Please input all values", "error")
            return render_template('admin.html') 

        # Check if the birthday makes sense
        bday_obj = date.fromisoformat(bday)
        today = date.today()
        if bday_obj >= today:
            flash("Error. Please enter a birthday before today", "error")
            return render_template('admin.html') 
        
        # Standardize birthday input
        bday_arr = bday.split("-")
        bday_arr[0], bday_arr[-1] = bday_arr[-1], bday_arr[0]
        bday_arr[0], bday_arr[-2] = bday_arr[-2], bday_arr[0]
        bday = '/'.join(bday_arr)

        cursor.execute("SELECT uni_id FROM Users")
        data = cursor.fetchall()

        # If we retrieved at least as many data as the number of possible 8 digit numbers, then somehow we have exceeded id limit
        if len(data) >= 9000000000:
            flash("We've reached user limit. Cannot create more", "error")
            return render_template('admin.html') 
                    
        id_unique = True
        new_id  = random.randint(10000000, 99999999)
        while id_unique:
            new_id  = random.randint(10000000, 99999999)
            if not any(new_id in d.values() for d in data):
                id_unique = False

        
        # The following only apply for students
        if user_type == "master's" or user_type == "phd":
            admit_year = request.form["year"]
            if admit_year == "":
                flash("Error. Please enter your year of admittance", "error")
                return render_template('admin.html') 

            # Check correct input type
            if not (admit_year.isdigit()):
                flash("Error. Please input the year of admittance as numeric", "error")
                return render_template('admin.html') 
            
            # Check if year of admittance is at least this year
            if int(admit_year) > datetime.now().year:
                flash("We do not support creating account for people to be admitted in the future", "error")
                return render_template('admin.html') 
    
      
            # Attempt to insert values
            entry_type = "student"
            cursor.execute("INSERT INTO Users VALUES(%s, %s, %s, %s, %s, %s, %s)", (new_id, password, fname, lname, bday, address,entry_type))
            cursor.execute("INSERT INTO Student VALUES(%s, %s, %s)", (new_id, admit_year, user_type))

        elif user_type == "faculty":
            dname = request.form["dname"]
            cursor.execute("INSERT INTO Users VALUES(%s, %s, %s, %s, %s, %s, %s)", (new_id, password, fname, lname, bday, address, user_type))
            cursor.execute("INSERT INTO Faculty VALUES(%s, %s)", (new_id, dname))
        else:
            cursor.execute("INSERT INTO Users VALUES(%s, %s, %s, %s, %s, %s, %s)", (new_id, password, fname, lname, bday, address, user_type))

        mydb.commit()

        # Flash messages
        flash('Sign up successful', 'success')
    
    return redirect('/account')



# Remove from registration 
@app.route('/<id>/remove', methods=['GET', 'POST'])
def remove(id):
    if request.method == 'POST':
        session["registration"].remove(request.form["cid"])
        session.modified = True

    return redirect(url_for("register", id=id))


# Route to add a class
@app.route('/<id>/add', methods=['GET', 'POST'])
def add(id):
    if request.method == 'POST':
        cursor = mydb.cursor(dictionary=True)

        # Retrieve form data
        cid = request.form["cid"]

         # 1. Check if class already in currently registered class
        if cid in session["registration"]:
            flash("You've already registered for that class", "error")
            return redirect(url_for("register", id=id))


        # Check if already enrolled previously
        cursor.execute("SELECT * FROM Enrollment WHERE cid = %s AND stud_id = %s", (cid, id))
        data = cursor.fetchone()
        if data:
            flash("You've already taken that class", "error")
            return redirect(url_for("register", id=id)) 

        # Check prereq
        for i in range(int(request.form["total_prereq"])):
            curr = "prereq" + str(i+1)
            prereq_info = request.form[curr].split()
            cursor.execute("SELECT * FROM Enrollment e JOIN Course_to_class cc ON e.cid = cc.cid \
                            WHERE stud_id = %s AND dname = %s AND cnum = %s", (id, prereq_info[0], prereq_info[1]))    
        
            prereq = cursor.fetchall()
            
            if not prereq:
                flash("You do not fulfill the prerequisites for this class", "error")
                return redirect(url_for("register", id=id)) 

        # Check schedule conflict
        my_time = request.form["class_time"]
        my_class_time = _process_time(my_time)
        

         # Retrieve all class times for currently registering year and semester for each class and check
        for class_id in session["registration"]:
            cursor.execute("SELECT class_time FROM Class_section WHERE cid = %s AND csem = %s \
                           AND cyear = %s", (class_id, request.form["csem"], request.form["cyear"]))
            other_time = cursor.fetchone()['class_time']
            curr_class_time =  _process_time(other_time)

            if (my_class_time[0] > curr_class_time[0] - 0.5 and my_class_time[0] < curr_class_time[1] + 0.5) or (my_class_time[1] > curr_class_time[0] - 0.5 and my_class_time[1] < curr_class_time[1] + 0.5):
                flash("Schedule conflict, oops", "error")
                return redirect(url_for("register", id=id)) 
          

        # Now we have to check for the classes that already got checked out but for current semester/year
        cursor.execute("SELECT class_time FROM Class_section cs JOIN Enrollment e ON cs.cid = e.cid AND cs.csem = e.cid AND cs.cyear = e.cyear \
                       WHERE cs.csem = %s AND cs.cyear = %s AND stud_id = %s", (request.form["csem"], request.form["cyear"], id))
        time_list = cursor.fetchall()
        for curr_class in time_list:
            curr_class_time = _process_time(curr_class['class_time'])
            if (my_class_time[0] > curr_class_time[0] - 0.5 and my_class_time[0] < curr_class_time[1] + 0.5) or (my_class_time[1] > curr_class_time[0] - 0.5 and my_class_time[1] < curr_class_time[1] + 0.5):
                flash("Schedule conflict, oops", "error")
                return redirect(url_for("register", id=id)) 
            

        # If no issue, then add to registered class
        session["registration"].append(cid)
        session.modified = True

    return redirect(url_for("register", id=id))


@app.route('/<id>/checkout', methods=['GET', 'POST'])
def checkout(id):
    # Commit data to enrollment table
    if request.method == 'POST':
        cursor = mydb.cursor(dictionary=True)
        semester = _get_curr_semester()
        for cid in session["registration"]:
            cursor.execute("INSERT INTO Enrollment (stud_id, cid, csem, cyear) VALUES (%s, %s, %s, %s)", (id, cid, semester[0], semester[1]))
            mydb.commit()

        session["registration"] = []
        session.modified = True

        flash("You've successfully registered", "success")

    return redirect(url_for("register", id=id)) 


# Class registration page
@app.route('/<id>/register', methods=['GET', 'POST'])
def register(id):
    if 'id' in session and (id == None or id=="register" or (id.isdigit() and int(id) != session['id'])):
        return redirect(url_for("register", id=session['id']))
    elif 'id' not in session:
        return redirect(url_for('home'))
    
    
    # Connect to database
    cursor = mydb.cursor(dictionary=True)
    semester = _get_curr_semester()
    query = "SELECT * FROM Class_section cs JOIN Course_to_class cc ON cs.cid = cc.cid \
            JOIN Course_info ci ON cc.dname = ci.dname AND cc.cnum = ci.cnum WHERE \
            cs.csem = %s AND cs.cyear = %s"
    params = [semester[0], semester[1]]

    # Display the courses
    if request.method == 'POST':   # If request = POST, query based on form data (i.e search function)
        dname = request.form["dname"]
        cnum = request.form["cnum"]
        cid = request.form["cid"]
        title = request.form["title"]  

        if dname != "":
            query += " AND ci.dname LIKE  %s"
            params.append(f"%{dname}%")
        
        if cnum != "":
            query += " AND ci.cnum = %s"
            params.append(cnum)

        if cid != "":
            query += " AND cs.cid = %s"
            params.append(cid)

        if title != "":
            query += " AND ci.title LIKE %s"
            params.append(f"%{title}%")
       
    cursor.execute(query, params)
    classes = cursor.fetchall()

    instructor_list = {}
    for each_class in classes:
        cursor.execute("SELECT fname, lname FROM Users WHERE uni_id = %s", (each_class['fid'],))
        instructor_list[each_class['fid']] = cursor.fetchone()

    cursor.execute("SELECT * FROM Prerequisite p JOIN Course_info c ON p.prereq_dname = c.dname AND p.cnum = c.cnum ORDER BY p.cnum")    
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
    cursor.execute("SELECT * FROM Enrollment e JOIN Class_section c ON e.cid = c.cid AND e.csem = c.csem AND e.cyear = c.cyear \
                   JOIN Course_to_class j ON c.cid = j.cid JOIN Course_info i ON j.dname = i.dname AND j.cnum = i.cnum WHERE \
                   e.stud_id = %s AND e.csem = %s AND e.cyear = %s", (session['id'],semester[0], semester[1]))        
    schedule = cursor.fetchall()

    return render_template('registration.html', schedule=schedule, renderer=renderer, instructor_list=instructor_list, classes=classes, prereqs=prereqs, session=session, semester=semester)



# Course catalog page
@app.route('/catalog')
def catalog():
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT dname FROM Course_info GROUP BY dname ORDER BY dname ASC")
    dept = cursor.fetchall()
    course = {}
    for row in dept:
        cursor.execute("SELECT * FROM Course_info WHERE dname = %s", (row["dname"],))
        course[row["dname"]] = cursor.fetchall()

    cursor.execute("SELECT * FROM Course_info c JOIN Prerequisite p ON p.dname = c.dname AND p.cnum = c.cnum ORDER BY p.cnum")    
    prereq = cursor.fetchall()
    
    logged = False

    if 'id' in session:
        logged = True

    return render_template('catalog.html', dept=dept, course=course, prereq=prereq, logged=logged)


# Drop courses
@app.route('/drop', methods=['GET', 'POST'])
def drop():
    if request.method == 'POST':
        cursor = mydb.cursor(dictionary=True)
        stud_id = request.form['stud_id']
        cid = request.form["cid"]
        csem = request.form["csem"]
        cyear = request.form["cyear"]

        cursor.execute("DELETE FROM Enrollment WHERE stud_id = %s AND cid = %s AND csem = %s AND cyear = %s", (stud_id, cid, csem, cyear))


    return redirect(url_for('register', id=session['id']))







########################################  
#               Account
########################################





# Personal information page
# Should display current schedule + enrollment, past schedules, and transcript
@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'id' in session:
        # _refresh()
        cursor = mydb.cursor(dictionary=True) 

        if session['type'] == "student": 
            cursor.execute("SELECT * FROM Enrollment e JOIN Class_section c ON e.cid = c.cid AND e.csem = c.csem AND e.cyear = c.cyear JOIN Course_to_class j ON c.cid = j.cid JOIN Course_info i ON j.dname = i.dname AND j.cnum = i.cnum WHERE e.stud_id = %s", (session['id'],))        
            schedule = cursor.fetchall()

            cursor.execute("SELECT * FROM Users u JOIN Student s ON u.uni_id = s.uni_id WHERE u.uni_id = %s ", (session['id'],))
            student = cursor.fetchall()

            cursor.execute('''SELECT csem, cyear FROM Enrollment e WHERE e.stud_id = %s GROUP BY e.csem, e.cyear
                              ORDER BY e.cyear DESC, e.csem''', (session['id'],))
            semesters = cursor.fetchall()

            return render_template('student.html', schedule=schedule, student=student, semesters=semesters, curr=_get_curr_semester())
            
        elif session['type'] == "faculty":
            cursor.execute('''SELECT * FROM Users u JOIN Faculty f ON u.uni_id = f.uni_id JOIN Class_section c 
                              ON f.uni_id = c.fid WHERE u.uni_id = %s ''', (session['id'],))
            faculty = cursor.fetchall()

            cursor.execute("SELECT * FROM Class_section c JOIN Course_to_class i ON c.cid = i.cid JOIN Course_info o ON i.dname = o.dname AND i.cnum = o.cnum WHERE fid = %s", (session['id'],))
            course = cursor.fetchall()

            cursor.execute('''SELECT csem, cyear, fid FROM Class_section c WHERE c.fid = %s GROUP BY c.csem, c.cyear 
                              ORDER BY c.cyear DESC, c.csem''', (session['id'],))
            semesters = cursor.fetchall()   

            student = {}
            for row in course:
                cursor.execute("SELECT * FROM Enrollment e JOIN Student s ON e.stud_id = s.uni_id JOIN Users u ON s.uni_id = u.uni_id WHERE e.cid = %s", (row["cid"],))
                student[row["cid"]] = cursor.fetchall()
                print(student[row['cid']])

            return render_template('faculty.html', faculty=faculty, course=course, student=student, semesters=semesters)
            
        elif session['type'] == "secretary":      

             # Get the secretary information
            cursor.execute("SELECT * FROM Users WHERE uni_id = %s", (session['id'],))
            secretary_info = cursor.fetchone()
            
            query = '''SELECT * FROM Users u JOIN Student s ON u.uni_id = s.uni_id 
                              JOIN Enrollment e ON s.uni_id = e.stud_id
                              JOIN Class_section c ON e.cid = c.cid AND e.csem = c.csem AND e.cyear = c.cyear WHERE 1=1'''
            student_query = "SELECT * FROM Users u JOIN Student s ON u.uni_id = s.uni_id WHERE 1=1"
            params=[]
            semesters = {}
            classes = {}
            students = []

            if request.method == 'POST':
                fname = request.form['fname']
                lname = request.form['lname']
                uni_id = request.form['uni_id']

                if fname != "":
                    query += " AND u.fname LIKE %s"
                    student_query += " AND u.fname LIKE %s"
                    params.append(f"%{fname}%")

                if lname != "":
                    query += " AND u.lname LIKE %s"
                    student_query += " AND u.lname LIKE %s"
                    params.append(f"%{lname}%")
        
                if uni_id != "":
                    query += " AND u.uni_id = %s"
                    student_query += " AND u.uni_id = %s"
                    params.append(uni_id)


            # Get all students from user tables with their course information
            cursor.execute(query, params)
            studentinfo = cursor.fetchall()
            cursor.execute(student_query, params)
            students = cursor.fetchall()

            for row in studentinfo: 
                cursor.execute('''SELECT csem, cyear FROM Enrollment e WHERE e.stud_id = %s GROUP BY e.csem, e.cyear
                                ORDER BY e.cyear DESC, e.csem''', (row['uni_id'],))
                semesters[row['uni_id']] = cursor.fetchall()

            
                cursor.execute('''SELECT * FROM Enrollment e 
                                JOIN Class_section c ON e.cid = c.cid AND e.csem = c.csem AND e.cyear = c.cyear
                                JOIN Course_to_class ctc ON c.cid=ctc.cid
                                JOIN Course_info ci ON ctc.dname = ci.dname AND ctc.cnum = ci.cnum
                                WHERE e.stud_id = %s''', (row['uni_id'],))
                classes[row['uni_id']] = cursor.fetchall()
           
            return render_template('secretary.html', secretary_info=secretary_info, studentinfo = studentinfo, classes=classes, students=students, semesters=semesters)
        
        elif session['type'] == "administrator":
            semesters = {}
            classes = {}
            taught = {}
            students = []
            secretaries = []
            sections = []
            admins = []
            faculty = []

            query = '''SELECT * FROM Users u JOIN Student s ON u.uni_id = s.uni_id 
                              JOIN Enrollment e ON s.uni_id = e.stud_id
                              JOIN Class_section c ON e.cid = c.cid AND e.csem = c.csem AND e.cyear = c.cyear WHERE 1=1'''
            
            student_query = "SELECT * FROM Users u JOIN Student s ON u.uni_id = s.uni_id WHERE 1=1"
            params = []

            if request.method == 'POST':
                fname = request.form['fname']
                lname = request.form['lname']
                uni_id = request.form['uni_id']

                if fname != "":
                    query += " AND u.fname LIKE %s"
                    student_query += " AND u.fname LIKE %s"
                    params.append(fname)

                if lname != "":
                    query += " AND u.lname LIKE %s"
                    student_query += " AND u.lname LIKE %s"
                    params.append(lname)
        
                if uni_id != "":
                    query += " AND u.uni_id = %s"
                    student_query += " AND u.uni_id LIKE %s"
                    params.append(uni_id)

            cursor.execute(query, params)
            studentinfo = cursor.fetchall()
            cursor.execute(student_query, params)
            students = cursor.fetchall()

            for row in studentinfo:
                cursor.execute('''SELECT csem, cyear FROM Enrollment e WHERE e.stud_id = %s GROUP BY e.csem, e.cyear
                                  ORDER BY e.cyear DESC, e.csem''', (row['uni_id'],))
                semesters[row['uni_id']] = cursor.fetchall()

           
                cursor.execute('''SELECT * FROM Enrollment e 
                                  JOIN Class_section c ON e.cid = c.cid AND e.csem = c.csem AND e.cyear = c.cyear
                                  JOIN Course_to_class ctc ON c.cid=ctc.cid
                                  JOIN Course_info ci ON ctc.dname = ci.dname AND ctc.cnum = ci.cnum
                                  WHERE e.stud_id = %s''', (row['uni_id'],))
                classes[row['uni_id']] = cursor.fetchall()
                
            
            if request.method != 'POST':
                cursor.execute(student_query)
                students = cursor.fetchall()

                cursor.execute("SELECT * FROM Users u JOIN Faculty f ON u.uni_id = f.uni_id")
                faculty = cursor.fetchall()

                for row in faculty:
                    cursor.execute('''SELECT * FROM Class_section c
                                    JOIN Course_to_class ctc ON c.cid=ctc.cid
                                    JOIN Course_info ci ON ctc.dname = ci.dname AND ctc.cnum = ci.cnum
                                    WHERE c.fid = %s''', (row['uni_id'],))
                    taught[row['uni_id']] = cursor.fetchall()

                cursor.execute("SELECT csem, cyear FROM Class_section GROUP BY csem, cyear ORDER BY cyear DESC, csem")
                sections = cursor.fetchall()

                cursor.execute("SELECT * FROM Users u WHERE u.user_type = 'Secretary'")
                secretaries = cursor.fetchall()

                cursor.execute("SELECT * FROM Users u WHERE u.user_type = 'Administrator'")
                admins = cursor.fetchall()

            return render_template('admin.html', studentinfo = studentinfo, classes=classes, students=students, semesters=semesters,
                                   faculty=faculty, secretaries=secretaries, admins=admins, taught=taught, sections=sections)
          
    return redirect(url_for('home'))



@app.route("/update_grade", methods=['GET', 'POST'])
def update_grade():
    if request.method == 'POST':
        cursor = mydb.cursor(dictionary=True)

        grade = request.form['grade']
        student_id = request.form['student'] 
        class_id = request.form['class']
    
        cursor.execute("UPDATE Enrollment SET grade = %s WHERE stud_id = %s AND cid = %s", (grade, student_id, class_id))
        mydb.commit()
        return redirect('/account')
    
@app.route("/update_birthday", methods=['GET', 'POST'])
def update_birthday():
    if request.method == 'POST':
        cursor = mydb.cursor(dictionary=True)
        user_id = request.form['user_id'] 
        bday = request.form['birthday']  
        
        # Check if bday is entered
        if bday == "":
            return redirect('/account')
        
        # Check if the birthday makes sense
        bday_obj = date.fromisoformat(bday)
        today = date.today()
        if bday_obj >= today:
            flash("Error. Please enter a birthday before today", "error")
            return redirect('/account')
        
        # Standardize birthday input
        bday_arr = bday.split("-")
        bday_arr[0], bday_arr[-1] = bday_arr[-1], bday_arr[0]
        bday_arr[0], bday_arr[-2] = bday_arr[-2], bday_arr[0]
        bday = '/'.join(bday_arr)

        cursor.execute("UPDATE Users SET bday = %s WHERE uni_id = %s", (bday, user_id))    
        mydb.commit()
        return redirect('/account')

    return redirect('/account')
    
@app.route("/update_address", methods=['GET', 'POST'])
def update_address():
    if request.method == 'POST':
        cursor = mydb.cursor(dictionary=True)
        user_id = request.form['user_id'] 
        address = request.form['address']
        cursor.execute("UPDATE Users SET user_address = %s WHERE uni_id = %s", (address, user_id))
        mydb.commit()
        return redirect('/account')
    
    return redirect('/account')

