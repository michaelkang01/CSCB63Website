CREATE TABLE IF NOT EXISTS grades (
    username TEXT NOT NULL PRIMARY KEY,
    Assignment1 REAL,
    Assignment2 REAL,
    Assignment3 REAL,
    Midterm REAL,
    Lab1 REAL,
    Lab2 REAL,
    Lab3 REAL,
    Final REAL,
    CourseMark REAL
);

CREATE TABLE IF NOT EXISTS people (
    username TEXT NOT NULL PRIMARY KEY,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    lecture INTEGER NOT NULL
);


CREATE TABLE IF NOT EXISTS anonfeedback (
    username TEXT NOT NULL,
    question TEXT NOT NULL,
    feedback TEXT NOT NULL,
    instructor TEXT NOT NULL,
    PRIMARY KEY (username, question, feedback, instructor)

);


CREATE TABLE IF NOT EXISTS remarks (
    username TEXT NOT NULL,
    request TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    status TEXT NOT NULL,
    PRIMARY KEY (username, request)
);

INSERT INTO grades VALUES("student1", 76, 68, 58, 62, 100, 100, 90, 42, 74.5);
INSERT INTO grades VALUES("ef3", 81, 63, 63, 67, 95, 100, 95, 37, 75.1);
INSERT INTO grades VALUES("student2", 42, 88.5, 90, 75, 100, 100, 100, 65.5, 82.6);
INSERT INTO grades VALUES("jc4", 35, 81.5, 83, 68, 93, 92, 91, 58.5, 75.25);
INSERT INTO grades VALUES("jc5", 55.5, 68, 58, 47, 80, 85, 80, 50, 65.4);

INSERT INTO people VALUES("student1", "student1", "John Smith", "student", 1);
INSERT INTO people VALUES("ef3", "ef3pass", "Emily Fletcher", "student", 1);
INSERT INTO people VALUES("student2", "student2", "Ashley Mason", "student", 2);
INSERT INTO people VALUES("jc4", "jc4pass", "James Cobbler", "student", 2);
INSERT INTO people VALUES("jc5", "jc5pass", "James Cobbler", "student", 2);

INSERT INTO people VALUES("instructor1", "instructor1", "Anna Bretscher", "instructor", 1);
INSERT INTO people VALUES("instructor2", "instructor2", "Notanna Notbretscher", "instructor", 2);

INSERT INTO anonfeedback VALUES("student1", "What do you like about the instructor teaching?", "Open to taking the time to explain hard concepts.", "instructor1");
INSERT INTO anonfeedback VALUES("student2", "What do you recommend the instructor to do to improve their teaching?", "Take time to explain hard concepts.", "instructor2");

INSERT INTO remarks VALUES("student1", "Final", "I believe that Question 2b was marked unfairly, and I deserved part marks for my proof.", "open");
INSERT INTO remarks VALUES("student2", "Assignment1", "The test cases ran inputs that we were told would not be tested.", "closed");