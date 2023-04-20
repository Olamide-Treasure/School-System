-- Active: 1681246787759@@regs-team15.crdbforhxr2l.us-east-1.rds.amazonaws.com@3306@uni

DROP DATABASE IF EXISTS uni;
CREATE DATABASE uni

    DEFAULT CHARACTER SET = 'utf8mb4';
use uni;

SET FOREIGN_KEY_CHECKS=0;

DROP TABLE IF EXISTS Users;
CREATE TABLE Users (
    uni_id          INT(8) NOT NULL,
    user_pass       VARCHAR(50) NOT NULL,
    fname           VARCHAR(50) NOT NULL,
    lname           VARCHAR(50) NOT NULL,
    bday            VARCHAR(10) NOT NULL,
    user_address    VARCHAR(100) NOT NULL,
    user_type       ENUM('student', 'faculty', 'secretary', 'administrator') NOT NULL,
    PRIMARY KEY (uni_id)
);

DROP TABLE IF EXISTS Faculty;
CREATE TABLE Faculty (
    uni_id          INT(8) NOT NULL,
    dname           VARCHAR(50) NOT NULL,
    PRIMARY KEY (uni_id),
    FOREIGN KEY (uni_id) REFERENCES Users(uni_id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS Student;
CREATE TABLE Student (
    uni_id             INT(8) NOT NULL,
    admit_year         INT(4) NOT NULL,
    stud_program       ENUM ("master's", "phd") NOT NULL,
    PRIMARY KEY (uni_id),
    FOREIGN KEY (uni_id) REFERENCES Users(uni_id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS Course_info;
CREATE TABLE Course_info (
    dname       VARCHAR(50) NOT NULL,
    cnum        INT NOT NULL,
    title       VARCHAR(100) NOT NULL,
    credits     INT NOT NULL,
    PRIMARY KEY (dname, cnum)
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

DROP TABLE IF EXISTS Enrollment;
CREATE TABLE Enrollment (
    stud_id         INT(8) NOT NULL,
    cid             INT NOT NULL,
    csem            VARCHAR(50) NOT NULL,
    cyear           VARCHAR(4) NOT NULL,
    grade           VARCHAR(2),
    PRIMARY KEY (stud_id, cid, csem, cyear),
    FOREIGN KEY (stud_id) REFERENCES Student(uni_id) ON DELETE CASCADE,
    FOREIGN KEY (cid, csem, cyear) REFERENCES Class_section(cid, csem, cyear) ON DELETE CASCADE
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


SET FOREIGN_KEY_CHECKS=1;





-- Row statements

-- Users
INSERT INTO Users VALUES (33356333, "testpass", "Elaine", "Ly", "09/09/2003", "6430 South St", "student");
INSERT INTO Users VALUES (36711565, "testpass", "Oliver", "Krisetya", "02/27/2003", "South 303", "student");
INSERT INTO Users VALUES (12345678, "testpass", "Son", "Nguyen", "01/01/2003", "South 303", "student");
INSERT INTO Users VALUES (11111111, "testpass", "Bhagi", "Narahari", "01/01/1960", "Gelman B2", "faculty");
INSERT INTO Users VALUES (12121212, "testpass", "Hyeong-Ah", "Choi", "03/21/1957", "Gelman B1", "faculty");
INSERT INTO Users VALUES (12312312, "testpass", "Dr.", "Teacher", "01/01/1950", "Gelman 2nd", "faculty");
INSERT INTO Users VALUES (55555555, "testpass", "Mr.", "Secretary", "01/01/1980", "Gelman 3rd", "secretary");
INSERT INTO Users VALUES (77777777, "testpass", "Ms.", "Admin", "01/01/1980", "Gelman 4th", "administrator");
INSERT INTO Users VALUES(88888888, "testpass", "Billie", "Holiday","01/01/2003", "Gelman 4th", "student");
INSERT INTO Users VALUES(99999999 , "testpass", "Diana", "Krall","01/01/2004", "Gelman 4th", "student");




-- STUDENTS
INSERT INTO Student VALUES (33356333, "2021", "master's");
INSERT INTO Student VALUES (36711565, "2021", "master's");
INSERT INTO Student VALUES (12345678, "2021", "master's");

-- FACULTY
INSERT INTO Faculty VALUES (11111111, "CSCI");
INSERT INTO Faculty VALUES (12121212, "ECE");
INSERT INTO Faculty VALUES (12312312, "MATH");

-- COURSE INFO
INSERT INTO Course_info VALUES ("CSCI", 6221, "SW Paradigms", 3);
INSERT INTO Course_info VALUES ("CSCI", 6461, "Computer Architecture", 3);
INSERT INTO Course_info VALUES ("CSCI", 6212, "Algorithms", 3);
INSERT INTO Course_info VALUES ("CSCI", 6220, "Machine Learning", 3);
INSERT INTO Course_info VALUES ("CSCI", 6232, "Networks 1", 3);
INSERT INTO Course_info VALUES ("CSCI", 6233, "Networks 2", 3);
INSERT INTO Course_info VALUES ("CSCI", 6241, "Database 1", 3);
INSERT INTO Course_info VALUES ("CSCI", 6242, "Database 2", 3);
INSERT INTO Course_info VALUES ("CSCI", 6246, "Compilers", 3);
INSERT INTO Course_info VALUES ("CSCI", 6260, "Multimedia", 3);
INSERT INTO Course_info VALUES ("CSCI", 6251, "Cloud Computing", 3);
INSERT INTO Course_info VALUES ("CSCI", 6254, "SW Engineering", 3);
INSERT INTO Course_info VALUES ("CSCI", 6262, "Graphics 1", 3);
INSERT INTO Course_info VALUES ("CSCI", 6283, "Security 1", 3);
INSERT INTO Course_info VALUES ("CSCI", 6284, "Cryptography", 3);
INSERT INTO Course_info VALUES ("CSCI", 6286, "Network Security", 3);
INSERT INTO Course_info VALUES ("CSCI", 6325, "Algorithms 2", 3);
INSERT INTO Course_info VALUES ("CSCI", 6339, "Embedded Systems", 3);
INSERT INTO Course_info VALUES ("CSCI", 6384, "Cryptography 2", 3);
INSERT INTO Course_info VALUES ("ECE", 6241, "Communication Theory", 3);
INSERT INTO Course_info VALUES ("ECE", 6242, "Information Theory", 2);
INSERT INTO Course_info VALUES ("MATH", 6210, "Logic", 2);

-- Course to class
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



-- Class section
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

-- FALL 2022
INSERT INTO Class_section VALUES (18, "Fall", "2022", "M", "15:00-17:30", 12121212);
INSERT INTO Class_section VALUES (19, "Fall", "2022", "R", "18:00-20:30", 12312312);
INSERT INTO Class_section VALUES (20, "Fall", "2022", "T", "16:00-18:30", 11111111);
-- SPRING 2023
INSERT INTO Class_section VALUES (18, "Spring", "2023", "W", "16:00-18:30", 12121212);
INSERT INTO Class_section VALUES (19, "Spring", "2023", "T", "15:00-17:30", 12312312);
INSERT INTO Class_section VALUES (20, "Spring", "2023", "F", "16:00-18:30", 11111111);


-- FALL 2022 ENROLLMENT
INSERT INTO Enrollment VALUES (33356333, 18, "Fall", "2022", "A");
INSERT INTO Enrollment VALUES (33356333, 19, "Fall", "2022", "A");
INSERT INTO Enrollment VALUES (33356333, 20, "Fall", "2022", "A");
INSERT INTO Enrollment VALUES (12345678, 18, "Fall", "2022", "A");
INSERT INTO Enrollment VALUES (12345678, 19, "Fall", "2022", "A");
INSERT INTO Enrollment VALUES (12345678, 20, "Fall", "2022", "A");
INSERT INTO Enrollment VALUES (36711565, 18, "Fall", "2022", "A");
INSERT INTO Enrollment VALUES (36711565, 19, "Fall", "2022", "A");
INSERT INTO Enrollment VALUES (36711565, 20, "Fall", "2022", "A");
-- SPRING 2023 ENROLLMENT 
INSERT INTO Enrollment VALUES (33356333, 18, "Spring", "2023", "A");
INSERT INTO Enrollment VALUES (33356333, 19, "Spring", "2023", "A");
INSERT INTO Enrollment VALUES (33356333, 20, "Spring", "2023", "A");
INSERT INTO Enrollment VALUES (12345678, 18, "Spring", "2023", "A");
INSERT INTO Enrollment VALUES (12345678, 19, "Spring", "2023", "A");
INSERT INTO Enrollment VALUES (12345678, 20, "Spring", "2023", "A");
INSERT INTO Enrollment VALUES (36711565, 18, "Spring", "2023", "A");
INSERT INTO Enrollment VALUES (36711565, 19, "Spring", "2023", "A");
INSERT INTO Enrollment VALUES (36711565, 20, "Spring", "2023", "A");
-- FALL 2023 ENROLLMENT
INSERT INTO Enrollment VALUES (33356333, 1, "Fall", "2023", NULL);
INSERT INTO Enrollment VALUES (12345678, 2, "Fall", "2023", NULL);
INSERT INTO Enrollment VALUES (12345678, 4, "Fall", "2023", NULL);
INSERT INTO Enrollment VALUES (12345678, 11, "Fall", "2023", NULL);
INSERT INTO Enrollment VALUES (36711565, 3, "Fall", "2023", NULL);

-- PREREQUISITES
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

