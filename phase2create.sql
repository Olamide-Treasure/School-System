

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS degrees;
CREATE TABLE degrees (
	degree_id int(2) not null PRIMARY KEY,
	degree_name  varchar(50) not null
);

DROP TABLE IF EXISTS user_type;
CREATE TABLE user_type (
  id int(1) NOT NULL PRIMARY KEY,
  name varchar(50) NOT NULL
);


DROP TABLE IF EXISTS applications;
CREATE TABLE applications ( 
  status varchar(30),
  UID varchar(8),
  semester varchar(10),
  s_year year,
  degree_type varchar(10),
  prior_bac_deg_name varchar(10),
  prior_bac_deg_gpa float(4),
  prior_bac_deg_major varchar(20),
  prior_bac_deg_year varchar(4),
  prior_bac_deg_university varchar(20),
  GRE_verbal int(10),
  GRE_year year,
  GRE_quatitative int(10),
  GRE_advanced_score int(10),
  GRE_advanced_subject varchar(20),
  TOEFL_score int(10),
  TOEFL_date date,
  interest varchar(50),
  experience varchar(50),
  prior_ms_deg_name varchar(10),
  prior_ms_deg_gpa float(4),
  prior_ms_deg_major varchar(20),
  prior_ms_deg_year varchar(4),
  prior__deg_university varchar(20),
  primary key(UID,semester,s_year),
  foreign key(UID) references users(ID) ON DELETE CASCADE
);


DROP TABLE IF EXISTS review;
CREATE TABLE review (
  review_id varchar(8),
  student_id varchar(8),
  p_semester varchar(10),
  p_year year,
  rev_rating varchar (10),
  deficiency_course varchar(20),
  reason_reject varchar(20),
  GAS_comment varchar(100),
  decision varchar(30),
  recom_advisor varchar(30),
  primary key(review_id,p_year,p_semester),
  foreign key(student_id) references users(ID) ON DELETE CASCADE,
  foreign key(review_id,p_semester,p_year) references applications(UID,semester,s_year) ON DELETE CASCADE
);


DROP TABLE IF EXISTS letter;
CREATE TABLE letter (
  userID varchar(8),
  letterID int(5),
  contents varchar(600),
  recommenderName varchar(20),
  recommenderAffil varchar(20),
  recommenderEmail varchar(20),
  primary key(letterID)
);


DROP TABLE IF EXISTS courses;
CREATE TABLE courses (
  	id int(3) not null PRIMARY KEY,
  	dept_name varchar(50) not null,
	course_num int(8) not null,
	course_name varchar(50) not null,
	credit_hours int(5) not null
);


DROP TABLE IF EXISTS user;
CREATE TABLE user (
	user_id int(8) NOT NULL UNIQUE PRIMARY KEY,
	user_type int(1) NOT NULL,
	fname  varchar(50) NOT NULL, 
	lname varchar(50) NOT NULL,
  	username varchar(50) NOT NULL,
	user_password varchar(50) NOT NULL, 
  	user_address varchar(50) NOT NULL,
  	user_phoneNUM varchar(50) NOT NULL,
  	ssn varchar(50) not null,
	email varchar(50) not null
);

DROP TABLE IF EXISTS student_courses;
CREATE TABLE student_courses ( 
	student_id int(8) NOT NULL,
	course_id int(3) NOT NULL,
  	grade varchar(50) NOT NULL,
    csem   VARCHAR(50) NOT NULL,
    cyear  VARCHAR(4) NOT NULL,
	FOREIGN KEY (student_id) REFERENCES user(user_id), 
 	FOREIGN KEY (course_id) REFERENCES courses(id)
);

DROP TABLE IF EXISTS student_advisors;
CREATE TABLE student_advisors (
	studentID int(8) not NULL,
	advisorID int(8) not NULL,
	FOREIGN KEY (studentID) REFERENCES user(user_id),
 	FOREIGN KEY (advisorID) REFERENCES user(user_id)
);

DROP TABLE IF EXISTS alumni;
CREATE TABLE alumni (
	student_id int(8) NOT NULL,
	degree_id int(2) NOT NULL,
	grad_year int(4) NOT NULL,
	FOREIGN KEY (student_id) REFERENCES user(user_id)
);



DROP TABLE IF EXISTS Faculty;
CREATE TABLE Faculty (
    uni_id          INT(8) NOT NULL,
    dname           VARCHAR(50) NOT NULL,
    PRIMARY KEY (uni_id),
    FOREIGN KEY (uni_id) REFERENCES Users(uni_id) ON DELETE CASCADE
);



DROP TABLE IF EXISTS students;
CREATE TABLE students (
	student_id int(8) NOT NULL,
	degree_id int(2) NOT NULL,
    admit_year   INT(4) NOT NULL,
  	FOREIGN KEY (student_id) REFERENCES user(user_id)
);


DROP TABLE IF EXISTS Prerequisite;
CREATE TABLE Prerequisite (
    dname             VARCHAR(50) NOT NULL,
    cnum              INT NOT NULL,
    prereq_type       ENUM("1", "2") NOT NULL,
    prereq_dname      VARCHAR(50) NOT NULL, 
    prereq_cnum       INT NOT NULL,
    PRIMARY KEY(dname, cnum, prereq_type),
    FOREIGN KEY (prereq_dname, prereq_cnum) REFERENCES Course_info(dname, cnum) ON DELETE CASCADE,
    FOREIGN KEY (dname, cnum) REFERENCES Course_info(dname, cnum)
);



DROP TABLE IF EXISTS Course_to_class;
CREATE TABLE Course_to_class (
    cid                 INT NOT NULL,
    dname               VARCHAR(50) NOT NULL,
    cnum                INT NOT NULL,
    class_section       INT NOT NULL,
    PRIMARY KEY (cid),
    FOREIGN KEY (dname, cnum) REFERENCES Course_info(dname, cnum) ON DELETE CASCADE
);

DROP TABLE IF EXISTS Class_section;
CREATE TABLE Class_section (
    cid                 INT NOT NULL,
    csem                VARCHAR(50) NOT NULL,
    cyear               VARCHAR(4) NOT NULL,
    day_of_week         ENUM('M', 'T', 'W', 'R', 'F') NOT NULL,
    class_time          VARCHAR(50) NOT NULL,
    fid                 INT(8) NOT NULL,
    PRIMARY KEY (cid, csem, cyear),
    FOREIGN KEY (cid) REFERENCES Course_to_class(cid) ON DELETE CASCADE,
    FOREIGN KEY (fid) REFERENCES Faculty(uni_id) ON DELETE CASCADE
); 



DROP TABLE IF EXISTS application;
CREATE TABLE application (
	gs_id  varchar(50) NOT NULL,
	app_status  varchar(50) NOT NULL,
	student_id int(8) NOT NULL,
	remarks varchar(50),
	FOREIGN KEY (student_id) REFERENCES user(user_id)
);

DROP TABLE IF EXISTS student_status;
CREATE TABLE student_status (
	student_id int(8) NOT NULL,
  	status varchar(50) NOT NULL,
   FOREIGN KEY (student_id) REFERENCES user(user_id)
);


DROP TABLE IF EXISTS phd_req;
CREATE TABLE phd_req (
	student_id int(8) NOT NULL PRIMARY KEY,
	thesisapproved varchar(5) NOT NULL
);

DROP TABLE IF EXISTS need_advisor;
CREATE TABLE need_advisor (
	student_id int(8) NOT NULL
);

DROP TABLE IF EXISTS applied_grad;
CREATE TABLE applied_grad (
	student_id int(8) NOT NULL,
	dtype int(2) NOT NULL
);


DROP TABLE IF EXISTS form1answer;
CREATE TABLE form1answer (
  student_id int(8) NOT NULL,
  courseID int(3) NOT NULL
);


SET FOREIGN_KEY_CHECKS=1;

insert into degrees values (20, 'MS Degree');
insert into degrees values (21, 'PhD Degree');

insert into user_type values (0, 'Systems Administrator');
insert into user_type values (1, 'Faculty Advisor');
insert into user_type values (2, 'Alumni');
insert into user_type values (3, 'Graduate Secretary');
insert into user_type values (4, 'MS Graduate Student');
insert into user_type values (5, 'PhD Student');

insert into courses values (100, 'CSCI', 6221, 'SW Paradigms', 3);
insert into courses values (101, 'CSCI', 6461, 'Computer Architecture', 3);
insert into courses values (102, 'CSCI', 6212, 'Algorithms', 3);
insert into courses values (103, 'CSCI', 6220, 'Machine Learning', 3);
insert into courses values (104, 'CSCI', 6232, 'Networks 1', 3);
insert into courses values (105, 'CSCI', 6233, 'Networks 2', 3);
insert into courses values (106, 'CSCI', 6241, 'Databases 1', 3);
insert into courses values (107, 'CSCI', 6242, 'Databases 2', 3);
insert into courses values (108, 'CSCI', 6246, 'Compilers', 3);
insert into courses values (109, 'CSCI', 6260, 'Multimedia', 3);
insert into courses values (110, 'CSCI', 6251, 'Cloud Computing', 3);
insert into courses values (111, 'CSCI', 6254, 'SW Engineering', 3);
insert into courses values (112, 'CSCI', 6262, 'Graphics 1', 3);
insert into courses values (113, 'CSCI', 6283, 'Security 1', 3);
insert into courses values (114, 'CSCI', 6284, 'Cryptography', 3);
insert into courses values (115, 'CSCI', 6286, 'Network Security', 3);
insert into courses values (116, 'CSCI', 6325, 'Algorithms 2', 3);
insert into courses values (117, 'CSCI', 6339, 'Embedded Systems', 3);
insert into courses values (118, 'CSCI', 6384, 'Cryptography 2', 3);
insert into courses values (119, 'ECE', 6241, 'Communication Theory', 3);
insert into courses values (120, 'ECE', 6242, 'Information Theory', 2);
insert into courses values (121, 'MATH', 6210, 'Logic', 2);



insert into user values (00000000, 0, 'Systems', 'Administrator', 'admin', 'pass', '2121 I St NW, Washington, DC 20052', '202-994-1000', '000-00-0000', 'admin@gwu.edu');
insert into user values (55555555, 4, 'Paul', 'McCartney', 'pcartney', 'tfaghk015', '2001 G St NW, Washington, DC 20052', '202-995-1001', '123-45-6789' , 'pcartney@gwu.edu');

insert into user values (66666666, 4, 'George', 'Harrison', 'gharrison', 'ptlhik990', '2003 K St NW, Washington, DC 20052', '202-959-1000', '987-32-3454', 'gharrison@gwu.edu');
insert into user values (99999999, 5, 'Ringo', 'Starr', 'rstarr', 'tplgik245', '2002 H St NW, Washington, DC 20052', '202-955-1000', '222-11-1111', 'rstarr@gwu.edu');

insert into user values (77777777, 2, 'Eric', 'Clapton', 'eclapton', 'jkjfd098', '2031 G St NW, Washington, DC 20052', '202-222-1000', '333-12-1232', 'eclapton@gwu.edu' );

insert into user values(33333333, 3, 'Emilia', 'Schmidt', 'semilia', 'jkoplkfd03', '1290 U St NW, Washington, DC 20052', '202-222-1000', '124-86-9834', 'semilia@gwu.edu');

insert into user values (11111111, 1, 'Bhagirath', 'Narahari', 'bhagi', 'jkjfd098', '2031 G St NW, Washington, DC 20052', '202-222-1000', '342-23-9233', 'bhagi@gwu.edu');

insert into user values (22222222, 1, 'Gabriel', 'Parmer', 'gparmer', 'uofd0932', '2033 L St NW, Washington, DC 20052', '202-222-1000', '231-34-2343', 'gparmer@gwu.edu' );

insert into user values (12121212, 1, 'Hyeong-Ah', 'Choi', 'hchoi', 'testpass', '2033 L St NW, Washington, DC 20052', '202-222-1000', '231-34-2346', 'hchoi@gwu.edu' );




insert into alumni values (77777777, 20, 2014);


insert into students values (55555555, 20, 2021);
insert into students values (66666666, 20, 2021);
insert into students values (99999999, 21, 2021);

insert into students values (33356333, 20, 2021);
insert into students values (36711565, 20, 2021);
insert into students values (12345678, 20, 2021);


insert into phd_req values(99999999, 'False');

insert into student_advisors values(55555555, 11111111);
insert into student_advisors values(66666666, 22222222);
insert into student_advisors values(99999999, 22222222);


insert into student_courses values(55555555, 100, 'A');
insert into student_courses values(55555555, 102, 'A');
insert into student_courses values(55555555, 101 , 'A');
insert into student_courses values(55555555, 104, 'A');
insert into student_courses values(55555555, 105, 'A');
insert into student_courses values(55555555, 106, 'B');
insert into student_courses values(55555555, 108, 'B');
insert into student_courses values(55555555, 112, 'B');
insert into student_courses values(55555555, 113, 'B');
insert into student_courses values(55555555, 107, 'B');

insert into student_courses values(66666666, 120, 'C');
insert into student_courses values(66666666, 100, 'B');
insert into student_courses values(66666666, 101, 'B');
insert into student_courses values(66666666, 102, 'B');
insert into student_courses values(66666666, 104, 'B');
insert into student_courses values(66666666, 105, 'B');
insert into student_courses values(66666666, 106, 'B');
insert into student_courses values(66666666, 107, 'B');
insert into student_courses values(66666666, 113, 'B');
insert into student_courses values(66666666, 114, 'B');

insert into student_courses values(99999999, 100, 'A');
insert into student_courses values(99999999, 102, 'A');
insert into student_courses values(99999999, 103, 'A');
insert into student_courses values(99999999, 105, 'A');
insert into student_courses values(99999999, 106, 'A');
insert into student_courses values(99999999, 107, 'A');
insert into student_courses values(99999999, 110, 'A');
insert into student_courses values(99999999, 111, 'A');
insert into student_courses values(99999999, 112, 'A');
insert into student_courses values(99999999, 115, 'A');
insert into student_courses values(99999999, 116, 'A');
insert into student_courses values(99999999, 117, 'A');

insert into student_courses values(77777777, 100, 'B');
insert into student_courses values(77777777, 102, 'B');
insert into student_courses values(77777777, 101, 'B');
insert into student_courses values(77777777, 104, 'B');
insert into student_courses values(77777777, 105, 'B');
insert into student_courses values(77777777, 106, 'B');
insert into student_courses values(77777777, 107, 'B');
insert into student_courses values(77777777, 113, 'A');
insert into student_courses values(77777777, 114, 'A');
insert into student_courses values(77777777, 115, 'A');


INSERT INTO Prerequisite VALUES ("CSCI", 6233, "1", "CSCI", 6232);
INSERT INTO Prerequisite VALUES ("CSCI", 6242, "1", "CSCI", 6241);
INSERT INTO Prerequisite VALUES ("CSCI", 6246, "1", "CSCI", 6461);
INSERT INTO Prerequisite VALUES ("CSCI", 6246, "2", "CSCI", 6212);
INSERT INTO Prerequisite VALUES ("CSCI", 6251, "1", "CSCI", 6461);
INSERT INTO Prerequisite VALUES ("CSCI", 6254, "1", "CSCI", 6221);
INSERT INTO Prerequisite VALUES ("CSCI", 6283, "1", "CSCI", 6212);
INSERT INTO Prerequisite VALUES ("CSCI", 6284, "1", "CSCI", 6212);
INSERT INTO Prerequisite VALUES ("CSCI", 6286, "1", "CSCI", 6283);
INSERT INTO Prerequisite VALUES ("CSCI", 6286, "2", "CSCI", 6232);
INSERT INTO Prerequisite VALUES ("CSCI", 6325, "1", "CSCI", 6212);
INSERT INTO Prerequisite VALUES ("CSCI", 6339, "1", "CSCI", 6461);
INSERT INTO Prerequisite VALUES ("CSCI", 6339, "2", "CSCI", 6212);
INSERT INTO Prerequisite VALUES ("CSCI", 6384, "1", "CSCI", 6284);


INSERT INTO Class_section VALUES (18, "Spring", "2023", "W", "16:00-18:30", 12121212);
INSERT INTO Class_section VALUES (19, "Spring", "2023", "T", "15:00-17:30", 12312312);
INSERT INTO Class_section VALUES (20, "Spring", "2023", "F", "16:00-18:30", 11111111);

INSERT INTO Class_section VALUES (18, "Fall", "2022", "M", "15:00-17:30", 12121212);
INSERT INTO Class_section VALUES (19, "Fall", "2022", "R", "18:00-20:30", 12312312);
INSERT INTO Class_section VALUES (20, "Fall", "2022", "T", "16:00-18:30", 11111111);


INSERT INTO Class_section VALUES (1, "Fall", "2023", "M", "15:00-17:30", 11111111);
INSERT INTO Class_section VALUES (2, "Fall", "2023", "T", "15:00-17:30", 11111111);
INSERT INTO Class_section VALUES (3, "Fall", "2023", "W", "15:00-17:30", 12121212);
INSERT INTO Class_section VALUES (4, "Fall", "2023", "M", "18:00-20:30", 11111111);
INSERT INTO Class_section VALUES (5, "Fall", "2023", "T", "18:00-20:30", 11111111);
INSERT INTO Class_section VALUES (6, "Fall", "2023", "W", "18:00-20:30", 11111111);
INSERT INTO Class_section VALUES (7, "Fall", "2023", "R", "18:00-20:30", 11111111);
INSERT INTO Class_section VALUES (8, "Fall", "2023", "T", "15:00-17:30", 11111111);
INSERT INTO Class_section VALUES (9, "Fall", "2023", "M", "18:00-20:30", 11111111);
INSERT INTO Class_section VALUES (10, "Fall", "2023", "M", "15:30-18:00", 11111111);
INSERT INTO Class_section VALUES (11, "Fall", "2023", "R", "18:00-20:30", 11111111);
INSERT INTO Class_section VALUES (12, "Fall", "2023", "W", "18:00-20:30", 11111111);
INSERT INTO Class_section VALUES (13, "Fall", "2023", "T", "18:00-20:30", 11111111);
INSERT INTO Class_section VALUES (14, "Fall", "2023", "M", "18:00-20:30", 11111111);
INSERT INTO Class_section VALUES (15, "Fall", "2023", "W", "18:00-20:30", 11111111);
INSERT INTO Class_section VALUES (16, "Fall", "2023", "W", "15:00-17:30", 11111111);
INSERT INTO Class_section VALUES (17, "Fall", "2023", "M", "18:00-20:30", 12121212);
INSERT INTO Class_section VALUES (18, "Fall", "2023", "T", "18:00-20:30", 12121212);
INSERT INTO Class_section VALUES (19, "Fall", "2023", "W", "18:00-20:30", 12312312);
INSERT INTO Class_section VALUES (20, "Fall", "2023", "R", "16:00-18:30", 11111111);


INSERT INTO Course_to_class VALUES (1, "CSCI", 6221, 1);
INSERT INTO Course_to_class VALUES (2, "CSCI", 6461, 1);
INSERT INTO Course_to_class VALUES (3, "CSCI", 6212, 1);
INSERT INTO Course_to_class VALUES (4, "CSCI", 6232, 1);
INSERT INTO Course_to_class VALUES (5, "CSCI", 6233, 1);
INSERT INTO Course_to_class VALUES (6, "CSCI", 6241, 1);
INSERT INTO Course_to_class VALUES (7, "CSCI", 6242, 1);
INSERT INTO Course_to_class VALUES (8, "CSCI", 6246, 1);
INSERT INTO Course_to_class VALUES (9, "CSCI", 6251, 1);
INSERT INTO Course_to_class VALUES (10, "CSCI", 6254, 1);
INSERT INTO Course_to_class VALUES (11, "CSCI", 6260, 1);
INSERT INTO Course_to_class VALUES (12, "CSCI", 6262, 1);
INSERT INTO Course_to_class VALUES (13, "CSCI", 6283, 1);
INSERT INTO Course_to_class VALUES (14, "CSCI", 6284, 1);
INSERT INTO Course_to_class VALUES (15, "CSCI", 6286, 1);
INSERT INTO Course_to_class VALUES (16, "CSCI", 6384, 1);
INSERT INTO Course_to_class VALUES (17, "ECE", 6241, 1);
INSERT INTO Course_to_class VALUES (18, "ECE", 6242, 1);
INSERT INTO Course_to_class VALUES (19, "MATH", 6210, 1);
INSERT INTO Course_to_class VALUES (20, "CSCI", 6339, 1);


INSERT INTO Faculty VALUES (11111111, "CSCI");
INSERT INTO Faculty VALUES (12121212, "ECE");
INSERT INTO Faculty VALUES (12312312, "MATH");


