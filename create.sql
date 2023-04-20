
use university;

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


DROP TABLE IF EXISTS courses;
CREATE TABLE courses (
  	id int(3) not null PRIMARY KEY,
  	dept_name varchar(50) not null,
	course_num int(8) not null,
	course_name varchar(50) not null,
	credit_hours int(5) not null
);

DROP TABLE IF EXISTS degree_requirements;
CREATE TABLE degree_requirements (
  degree_type int(4) not null,
  course_req varchar(50) not null, 
  GPA_req varchar(3) not null, 
  credit_hours int(3) not null, 
  other_req varchar(50) not null
);

DROP TABLE IF EXISTS suspension_check;
CREATE TABLE suspension_check (
  grade_check varchar(50) not null
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

DROP TABLE IF EXISTS students;
CREATE TABLE students (
	student_id int(8) NOT NULL,
	degree_id int(2) NOT NULL,
  	FOREIGN KEY (student_id) REFERENCES user(user_id)
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

insert into degree_requirements values (20, 'completed the courses: CSCI 6212, CSCI 6221, and CSCI 6461', '3.0', 30, 'Taken at most 2 courses outside the CS department as part of the 30 credit hours of coursework
&	No more than 2 grades below B');
insert into degree_requirements values (21, 'no required core courses', '3.5', 36, 'Taken at least 30 credits in CS, Not more than one grade below B & Pass thesis defense – approved by the advisor');

insert into suspension_check values ('can not have three grades below B');


insert into user values (00000000, 0, 'Systems', 'Administrator', 'admin', 'pass', '2121 I St NW, Washington, DC 20052', '202-994-1000', '000-00-0000', 'admin@gwu.edu');
insert into user values (55555555, 4, 'Paul', 'McCartney', 'pcartney', 'tfaghk015', '2001 G St NW, Washington, DC 20052', '202-995-1001', '123-45-6789' , 'pcartney@gwu.edu');

insert into user values (66666666, 4, 'George', 'Harrison', 'gharrison', 'ptlhik990', '2003 K St NW, Washington, DC 20052', '202-959-1000', '987-32-3454', 'gharrison@gwu.edu');
insert into user values (99999999, 5, 'Ringo', 'Starr', 'rstarr', 'tplgik245', '2002 H St NW, Washington, DC 20052', '202-955-1000', '222-11-1111', 'rstarr@gwu.edu');

insert into user values (77777777, 2, 'Eric', 'Clapton', 'eclapton', 'jkjfd098', '2031 G St NW, Washington, DC 20052', '202-222-1000', '333-12-1232', 'eclapton@gwu.edu' );

insert into user values(33333333, 3, 'Emilia', 'Schmidt', 'semilia', 'jkoplkfd03', '1290 U St NW, Washington, DC 20052', '202-222-1000', '124-86-9834', 'semilia@gwu.edu');

insert into user values (11111111, 1, 'Bhagirath', 'Narahari', 'bhagi', 'jkjfd098', '2031 G St NW, Washington, DC 20052', '202-222-1000', '342-23-9233', 'bhagi@gwu.edu');

insert into user values (22222222, 1, 'Gabriel', 'Parmer', 'gparmer', 'uofd0932', '2033 L St NW, Washington, DC 20052', '202-222-1000', '231-34-2343', 'gparmer@gwu.edu' );


insert into alumni values (77777777, 20, 2014);


insert into students values (55555555, 20);
insert into students values (66666666, 20);
insert into students values (99999999, 21);

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