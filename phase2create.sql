use integration;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS students;
CREATE TABLE students (
	student_id int(8) NOT NULL,
	degree_id int(2) NOT NULL,
  admit_year   INT(4) NOT NULL,
  PRIMARY KEY (student_id),
  FOREIGN KEY (student_id) REFERENCES user(user_id)
);

DROP TABLE IF EXISTS degrees;
CREATE TABLE degrees (
	degree_id int(2) not null,
	degree_name  varchar(50) not null,
  primary key(degree_id)
);


DROP TABLE IF EXISTS user_type;
CREATE TABLE user_type (
  id int(1) NOT NULL,
  name varchar(50) NOT NULL,
  primary key(id)
);


DROP TABLE IF EXISTS applications;
CREATE TABLE applications ( 
  status varchar(30),
  student_id int(8),
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
  primary key(student_id,semester,s_year),
  foreign key(student_id) references students(student_id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS faculty;
CREATE TABLE faculty (
  faculty_id      INT(8) NOT NULL,
  department      VARCHAR(50) NOT NULL,
  instructor      BOOLEAN,
  advisor         BOOLEAN,
  reviewr         BOOLEAN,
  PRIMARY KEY (faculty_id),
  FOREIGN KEY (faculty_id) REFERENCES user(user_id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS review;
CREATE TABLE review (
  review_id int(8),
  student_id int(8),
  p_semester varchar(10),
  p_year year,
  rev_rating varchar (10),
  deficiency_course varchar(20),
  reason_reject varchar(20),
  GAS_comment varchar(100),
  decision varchar(30),
  recom_advisor varchar(30),
  primary key(review_id,p_year,p_semester),
  foreign key(student_id) references students(student_id) ON DELETE CASCADE,
  foreign key(review_id) references faculty(faculty_id) ON DELETE CASCADE,
  foreign key(review_id,p_semester,p_year) references applications(student_id,semester,s_year) ON DELETE CASCADE
);


DROP TABLE IF EXISTS letter;
CREATE TABLE letter (
  user_id int(8),
  letter_id int(5),
  contents varchar(600),
  recommenderName varchar(20),
  recommenderAffil varchar(20),
  recommenderEmail varchar(20),
  primary key(letter_id),
  foreign key(user_id) references students(student_id) ON DELETE CASCADE
);


DROP TABLE IF EXISTS course;
CREATE TABLE course (
  id int(3) not null,
  dept_name varchar(50) not null,
	course_num int(8) not null,
	course_name varchar(50) not null,
	credit_hours int(5) not null,
  primary key(id)
);


DROP TABLE IF EXISTS user;
CREATE TABLE user (
	user_id int(8) NOT NULL UNIQUE,
	user_type int(1) NOT NULL,
	fname  varchar(50) NOT NULL, 
	lname varchar(50) NOT NULL,
  username varchar(50) NOT NULL,
	user_password varchar(50) NOT NULL, 
  user_address varchar(50) NOT NULL,
  user_phoneNUM varchar(50) NOT NULL,
  ssn varchar(50) not null,
	email varchar(50) not null,
  primary key(user_id),
  foreign key(user_type) references user_type(id)
);

DROP TABLE IF EXISTS student_courses;
CREATE TABLE student_courses ( 
	student_id int(8) NOT NULL,
	class_id   int(3) NOT NULL,
  grade varchar(50) NOT NULL,
  csem   VARCHAR(50) NOT NULL,
  cyear  VARCHAR(4) NOT NULL,
  PRIMARY KEY (student_id, class_id, csem, cyear),
	FOREIGN KEY (student_id) REFERENCES students(student_id), 
 	FOREIGN KEY (class_id, csem, cyear) REFERENCES class_section(class_id, csem, cyear)
);

DROP TABLE IF EXISTS student_advisors;
CREATE TABLE student_advisors (
	studentID int(8) not NULL,
	advisorID int(8) not NULL,
  Primary Key (studentID),
	FOREIGN KEY (studentID) REFERENCES students(student_id),
 	FOREIGN KEY (advisorID) REFERENCES faculty(faculty_id)
);

DROP TABLE IF EXISTS alumni;
CREATE TABLE alumni (
	student_id int(8) NOT NULL,
	degree_id int(2) NOT NULL,
	grad_year int(4) NOT NULL,
  PRIMARY KEY (student_id)
);


DROP TABLE IF EXISTS application;
CREATE TABLE application (
	gs_id  varchar(50) NOT NULL,
	app_status  varchar(50) NOT NULL,
	student_id int(8) NOT NULL,
	remarks varchar(50),
	FOREIGN KEY (student_id) REFERENCES user(user_id)
);



DROP TABLE IF EXISTS prerequisite;
CREATE TABLE prerequisite (
    course_id         INT(6) NOT NULL,
    prereq_type       ENUM("1", "2") NOT NULL,
    prereq_id         INT(6) NOT NULL,
    PRIMARY KEY(course_id, prereq_type),
    FOREIGN KEY (prereq_id) REFERENCES course(id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS class_section;
CREATE TABLE class_section (
    class_id            INT(6) NOT NULL,
    csem                VARCHAR(50) NOT NULL,
    cyear               VARCHAR(4) NOT NULL,
    day_of_week         ENUM('M', 'T', 'W', 'R', 'F') NOT NULL,
    class_time          VARCHAR(50) NOT NULL,
    course_id           INT(6) NOT NULL,
    faculty_id          INT(8) NOT NULL,
    PRIMARY KEY (class_id, csem, cyear),
    FOREIGN KEY (course_id) REFERENCES course(id) ON DELETE CASCADE,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE
); 

DROP TABLE IF EXISTS graduation;
CREATE TABLE graduation (
	gs_id  int(8) NOT NULL,
	app_status  varchar(50) NOT NULL,
	student_id int(8) NOT NULL,
	remarks varchar(50),
	FOREIGN KEY (student_id) REFERENCES students(student_id),
  Foreign Key (gs_id) REFERENCES user(user_id)
);

DROP TABLE IF EXISTS phd_req;
CREATE TABLE phd_req (
	student_id int(8) NOT NULL,
	thesisapproved varchar(5) NOT NULL,
  Primary Key(student_id),
  Foreign Key (student_id) REFERENCES students(student_id)
);

DROP TABLE IF EXISTS applied_grad;
CREATE TABLE applied_grad (
	student_id int(8) NOT NULL,
	dtype int(2) NOT NULL,
  PRIMARY KEY (student_id)
);

DROP TABLE IF EXISTS need_advisor;
CREATE TABLE need_advisor (
	student_id int(8) NOT NULL
);


DROP TABLE IF EXISTS form1answer;
CREATE TABLE form1answer (
  student_id int(8) NOT NULL,
  courseID int(6) NOT NULL,
  Primary Key(student_id),
  Foreign Key (courseID) REFERENCES course(id)
);

DROP TABLE IF EXISTS student_status;
CREATE TABLE student_status (
	student_id int(8) NOT NULL,
  	status varchar(50) NOT NULL,
   FOREIGN KEY (student_id) REFERENCES user(user_id)
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

insert into course values (100, 'CSCI', 6221, 'SW Paradigms', 3);
insert into course values (101, 'CSCI', 6461, 'Computer Architecture', 3);
insert into course values (102, 'CSCI', 6212, 'Algorithms', 3);
insert into course values (103, 'CSCI', 6220, 'Machine Learning', 3);
insert into course values (104, 'CSCI', 6232, 'Networks 1', 3);
insert into course values (105, 'CSCI', 6233, 'Networks 2', 3);
insert into course values (106, 'CSCI', 6241, 'Databases 1', 3);
insert into course values (107, 'CSCI', 6242, 'Databases 2', 3);
insert into course values (108, 'CSCI', 6246, 'Compilers', 3);
insert into course values (109, 'CSCI', 6260, 'Multimedia', 3);
insert into course values (110, 'CSCI', 6251, 'Cloud Computing', 3);
insert into course values (111, 'CSCI', 6254, 'SW Engineering', 3);
insert into course values (112, 'CSCI', 6262, 'Graphics 1', 3);
insert into course values (113, 'CSCI', 6283, 'Security 1', 3);
insert into course values (114, 'CSCI', 6284, 'Cryptography', 3);
insert into course values (115, 'CSCI', 6286, 'Network Security', 3);
insert into course values (116, 'CSCI', 6325, 'Algorithms 2', 3);
insert into course values (117, 'CSCI', 6339, 'Embedded Systems', 3);
insert into course values (118, 'CSCI', 6384, 'Cryptography 2', 3);
insert into course values (119, 'ECE', 6241, 'Communication Theory', 3);
insert into course values (120, 'ECE', 6242, 'Information Theory', 2);
insert into course values (121, 'MATH', 6210, 'Logic', 2);



insert into user values (00000000, 0, 'Systems', 'Administrator', 'admin', 'pass', '2121 I St NW, Washington, DC 20052', '202-994-1000', '000-00-0000', 'admin@gwu.edu');
insert into user values (55555555, 4, 'Paul', 'McCartney', 'pcartney', 'tfaghk015', '2001 G St NW, Washington, DC 20052', '202-995-1001', '123-45-6789' , 'pcartney@gwu.edu');

insert into user values (66666666, 4, 'George', 'Harrison', 'gharrison', 'ptlhik990', '2003 K St NW, Washington, DC 20052', '202-959-1000', '987-32-3454', 'gharrison@gwu.edu');
insert into user values (99999999, 5, 'Ringo', 'Starr', 'rstarr', 'tplgik245', '2002 H St NW, Washington, DC 20052', '202-955-1000', '222-11-1111', 'rstarr@gwu.edu');

insert into user values (77777777, 2, 'Eric', 'Clapton', 'eclapton', 'jkjfd098', '2031 G St NW, Washington, DC 20052', '202-222-1000', '333-12-1232', 'eclapton@gwu.edu' );

insert into user values(33333333, 3, 'Emilia', 'Schmidt', 'semilia', 'jkoplkfd03', '1290 U St NW, Washington, DC 20052', '202-222-1000', '124-86-9834', 'semilia@gwu.edu');

insert into user values (11111111, 1, 'Bhagirath', 'Narahari', 'bhagi', 'jkjfd098', '2031 G St NW, Washington, DC 20052', '202-222-1000', '342-23-9233', 'bhagi@gwu.edu');

insert into user values (22222222, 1, 'Gabriel', 'Parmer', 'gparmer', 'uofd0932', '2033 L St NW, Washington, DC 20052', '202-222-1000', '231-34-2343', 'gparmer@gwu.edu' );


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


insert into student_courses values(55555555, 100, 'A', 'Fall', '2021');
insert into student_courses values(55555555, 102, 'A', 'Fall', '2021');
insert into student_courses values(55555555, 101 , 'A', 'Fall', '2021');
insert into student_courses values(55555555, 104, 'A', 'Fall', '2021');
insert into student_courses values(55555555, 105, 'A', 'Fall', '2021');
insert into student_courses values(55555555, 106, 'B', 'Fall', '2021');
insert into student_courses values(55555555, 108, 'B', 'Fall', '2021');
insert into student_courses values(55555555, 112, 'B', 'Fall', '2021');
insert into student_courses values(55555555, 113, 'B', 'Fall', '2021');
insert into student_courses values(55555555, 107, 'B', 'Fall', '2021');

insert into student_courses values(66666666, 120, 'C', 'Fall', '2021');
insert into student_courses values(66666666, 100, 'B', 'Fall', '2021');
insert into student_courses values(66666666, 101, 'B', 'Fall', '2021');
insert into student_courses values(66666666, 102, 'B', 'Fall', '2021');
insert into student_courses values(66666666, 104, 'B', 'Fall', '2021');
insert into student_courses values(66666666, 105, 'B', 'Fall', '2021');
insert into student_courses values(66666666, 106, 'B', 'Fall', '2021');
insert into student_courses values(66666666, 107, 'B', 'Fall', '2021');
insert into student_courses values(66666666, 113, 'B', 'Fall', '2021');
insert into student_courses values(66666666, 114, 'B', 'Fall', '2021');

insert into student_courses values(99999999, 100, 'A', 'Fall', '2021');
insert into student_courses values(99999999, 102, 'A', 'Fall', '2021');
insert into student_courses values(99999999, 103, 'A', 'Fall', '2021');
insert into student_courses values(99999999, 105, 'A', 'Fall', '2021');
insert into student_courses values(99999999, 106, 'A', 'Fall', '2021');
insert into student_courses values(99999999, 107, 'A', 'Fall', '2021');
insert into student_courses values(99999999, 110, 'A', 'Fall', '2021');
insert into student_courses values(99999999, 111, 'A', 'Fall', '2021');
insert into student_courses values(99999999, 112, 'A', 'Fall', '2021');
insert into student_courses values(99999999, 115, 'A', 'Fall', '2021');
insert into student_courses values(99999999, 116, 'A', 'Fall', '2021');
insert into student_courses values(99999999, 117, 'A', 'Fall', '2021');

insert into student_courses values(77777777, 100, 'B', 'Fall', '2021');
insert into student_courses values(77777777, 102, 'B', 'Fall', '2021');
insert into student_courses values(77777777, 101, 'B', 'Fall', '2021');
insert into student_courses values(77777777, 104, 'B', 'Fall', '2021');
insert into student_courses values(77777777, 105, 'B', 'Fall', '2021');
insert into student_courses values(77777777, 106, 'B', 'Fall', '2021');
insert into student_courses values(77777777, 107, 'B', 'Fall', '2021');
insert into student_courses values(77777777, 113, 'A', 'Fall', '2021');
insert into student_courses values(77777777, 114, 'A', 'Fall', '2021');
insert into student_courses values(77777777, 115, 'A', 'Fall', '2021');


INSERT INTO prerequisite VALUES ("CSCI", 6233, "1", "CSCI", 6232);
INSERT INTO prerequisite VALUES ("CSCI", 6242, "1", "CSCI", 6241);
INSERT INTO prerequisite VALUES ("CSCI", 6246, "1", "CSCI", 6461);
INSERT INTO prerequisite VALUES ("CSCI", 6246, "2", "CSCI", 6212);
INSERT INTO prerequisite VALUES ("CSCI", 6251, "1", "CSCI", 6461);
INSERT INTO prerequisite VALUES ("CSCI", 6254, "1", "CSCI", 6221);
INSERT INTO prerequisite VALUES ("CSCI", 6283, "1", "CSCI", 6212);
INSERT INTO prerequisite VALUES ("CSCI", 6284, "1", "CSCI", 6212);
INSERT INTO prerequisite VALUES ("CSCI", 6286, "1", "CSCI", 6283);
INSERT INTO prerequisite VALUES ("CSCI", 6286, "2", "CSCI", 6232);
INSERT INTO prerequisite VALUES ("CSCI", 6325, "1", "CSCI", 6212);
INSERT INTO prerequisite VALUES ("CSCI", 6339, "1", "CSCI", 6461);
INSERT INTO prerequisite VALUES ("CSCI", 6339, "2", "CSCI", 6212);
INSERT INTO prerequisite VALUES ("CSCI", 6384, "1", "CSCI", 6284);


INSERT INTO class_section VALUES (18, "Spring", "2023", "W", "16:00-18:30", 12121212);
INSERT INTO class_section VALUES (19, "Spring", "2023", "T", "15:00-17:30", 12312312);
INSERT INTO class_section VALUES (20, "Spring", "2023", "F", "16:00-18:30", 11111111);

INSERT INTO class_section VALUES (18, "Fall", "2022", "M", "15:00-17:30", 12121212);
INSERT INTO class_section VALUES (19, "Fall", "2022", "R", "18:00-20:30", 12312312);
INSERT INTO class_section VALUES (20, "Fall", "2022", "T", "16:00-18:30", 11111111);


INSERT INTO class_section VALUES (1, "Fall", "2023", "M", "15:00-17:30", 11111111);
INSERT INTO class_section VALUES (2, "Fall", "2023", "T", "15:00-17:30", 11111111);
INSERT INTO class_section VALUES (3, "Fall", "2023", "W", "15:00-17:30", 12121212);
INSERT INTO class_section VALUES (4, "Fall", "2023", "M", "18:00-20:30", 11111111);
INSERT INTO class_section VALUES (5, "Fall", "2023", "T", "18:00-20:30", 11111111);
INSERT INTO class_section VALUES (6, "Fall", "2023", "W", "18:00-20:30", 11111111);
INSERT INTO class_section VALUES (7, "Fall", "2023", "R", "18:00-20:30", 11111111);
INSERT INTO class_section VALUES (8, "Fall", "2023", "T", "15:00-17:30", 11111111);
INSERT INTO class_section VALUES (9, "Fall", "2023", "M", "18:00-20:30", 11111111);
INSERT INTO class_section VALUES (10, "Fall", "2023", "M", "15:30-18:00", 11111111);
INSERT INTO class_section VALUES (11, "Fall", "2023", "R", "18:00-20:30", 11111111);
INSERT INTO class_section VALUES (12, "Fall", "2023", "W", "18:00-20:30", 11111111);
INSERT INTO class_section VALUES (13, "Fall", "2023", "T", "18:00-20:30", 11111111);
INSERT INTO class_section VALUES (14, "Fall", "2023", "M", "18:00-20:30", 11111111);
INSERT INTO class_section VALUES (15, "Fall", "2023", "W", "18:00-20:30", 11111111);
INSERT INTO class_section VALUES (16, "Fall", "2023", "W", "15:00-17:30", 11111111);
INSERT INTO class_section VALUES (17, "Fall", "2023", "M", "18:00-20:30", 12121212);
INSERT INTO class_section VALUES (18, "Fall", "2023", "T", "18:00-20:30", 12121212);
INSERT INTO class_section VALUES (19, "Fall", "2023", "W", "18:00-20:30", 12312312);
INSERT INTO class_section VALUES (20, "Fall", "2023", "R", "16:00-18:30", 11111111);

INSERT INTO faculty VALUES (11111111, "CSCI");
INSERT INTO faculty VALUES (12121212, "ECE");
INSERT INTO faculty VALUES (12312312, "MATH");