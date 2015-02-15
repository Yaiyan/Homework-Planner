import sqlite3
import os

#The path to the database from the working directory
databasePath = "homeworkDB.db"

def openConnection():
    """Returns a connection to the database"""
    conn = sqlite3.connect(databasePath)
    return conn


def incrementSchoolYear():
    """Increases the schoolyear of all pupils by one"""
    conn = openConnection()
    
    c = conn.cursor()
    c.execute("UPDATE pupils SET year=year+1")
    
    conn.commit()
    conn.close()

def deleteYear14():
    """Delete's all pupils in year 14"""
    conn = openConnection()
    
    c = conn.cursor()
    #Get all pupils in year 14
    c.execute("SELECT actor_id FROM pupils WHERE year >= 14")
    pupilIds = list(c.fetchall())
    
    #Delete them from any tables they're involved in
    #This includes all associations
    c.executemany("DELETE FROM actors WHERE actor_id=?", pupilIds)
    c.executemany("DELETE FROM pupils WHERE actor_id=?", pupilIds)
    c.executemany("DELETE FROM class_members WHERE actor_id=?", pupilIds)
    c.executemany("DELETE FROM homework_set WHERE actor_id=?", pupilIds)
    
    conn.commit()
    conn.close()


def getAllPupilData():
    """Gets all pupil data from the database, this merges
    the actor and pupil table"""
    conn = openConnection()
    
    c = conn.cursor()
    #This appends the pupil table to the end of the actors
    #table for each row. Then sort by name
    c.execute("SELECT * FROM actors INNER JOIN pupils ON actors.actor_id=pupils.actor_id ORDER BY name ASC")
    allpupils = list(c.fetchall())
    
    conn.commit()
    conn.close()
    
    return allpupils

def getAllRawPupilData():
    """Gets all pupil data from the pupils table, does not
    join with actors table"""
    conn = openConnection()
    
    c = conn.cursor()
    c.execute("SELECT * FROM pupils")
    alldetails = list(c.fetchall())
    
    conn.commit()
    conn.close()
    
    return alldetails

def getAllRawHomeworkData():
    """Gets all homework data from the database"""
    conn = openConnection()
    
    c = conn.cursor()
    c.execute("SELECT * FROM homework")
    alldetails = list(c.fetchall())
    
    conn.commit()
    conn.close()
    
    return alldetails

def getAllRawHomeworkSetData():
    """Gets all homework association data from the
    database"""
    conn = openConnection()
    
    c = conn.cursor()
    c.execute("SELECT * FROM homework_set")
    alldetails = list(c.fetchall())
    
    conn.commit()
    conn.close()
    
    return alldetails

def getAllStaffData():
    """Gets all staff data from the actors table (this is
    admins and teachers)"""
    conn = openConnection()
    
    c = conn.cursor()
    #Check the rights are greater than 1, and hence more
    #than a pupil
    c.execute("SELECT * FROM actors WHERE rights > 1")
    alldetails = list(c.fetchall())
    
    conn.commit()
    conn.close()
    
    return alldetails

def getAllPupilsForHomework(homework_id):
    """Gets all actors that a homework has been set to,
    and is joined onto the homework information"""
    conn = openConnection()
    
    c = conn.cursor()
    #Get the homework for the association table, then load
    #all pupils and append this to the end of the row
    c.execute("SELECT * FROM homework_set INNER JOIN actors ON actors.actor_id=homework_set.actor_id WHERE homework_id=?",(homework_id,))
    
    alldetails = list(c.fetchall())
    
    conn.commit()
    conn.close()
    
    return alldetails

def getAllRawClassData():
    """Get's all the class data from the database"""
    conn = openConnection()
    
    c = conn.cursor()
    c.execute("SELECT * FROM classes")
    alldetails = list(c.fetchall())
    
    conn.commit()
    conn.close()
    
    return alldetails

def getAllRawClassMemberData():
    """Gets the class member association table from the
    database"""
    conn = openConnection()
    
    c = conn.cursor()
    c.execute("SELECT * FROM class_members")
    alldetails = list(c.fetchall())
    
    conn.commit()
    conn.close()
    
    return alldetails

def getAllClassData(teacher_id=-1):
    """Gets all the class data, or all the classes for a
    given teacher. Also merges the teacher information to
    the class"""
    conn = openConnection()
    
    c = conn.cursor()
    if teacher_id == -1:
        #Select all classes from the table, and then merge
        #the teachers information into the row
        c.execute("SELECT * FROM classes INNER JOIN actors ON actors.actor_id=classes.teacher_id ORDER BY class_id ASC")
    else:
        #Select all classes with a given teacher, and then
        #merge the teachers information into the row
        c.execute("SELECT * FROM classes INNER JOIN actors ON actors.actor_id=classes.teacher_id WHERE teacher_id=? ORDER BY class_id ASC",(teacher_id,))
    alldetails = list(c.fetchall())
    
    conn.commit()
    conn.close()
    
    return alldetails

def getAllUserData():
    """Gets all of the data from the actors table from the
    database"""
    conn = openConnection()
    
    c = conn.cursor()
    c.execute("SELECT * FROM actors ORDER BY name ASC")
    alldetails = list(c.fetchall())
    
    conn.commit()
    conn.close()
    
    return alldetails


def clearCompletedHomework(homework_id):
    """Sets all homework with the given homework id is set
    as being uncomplete"""
    conn = openConnection()
    
    c = conn.cursor()
    c.execute("UPDATE homework_set SET completed=0 WHERE homework_id=?", (homework_id))
    
    conn.commit()
    conn.close()


def finishHomework(homework_id, actor_ids):
    """Set the homework with the given id, and given actor
    id to being complete"""
    conn = openConnection()
    
    args = [(homework_id, i) for i in actor_ids]
    
    c = conn.cursor()
    c.executemany("UPDATE homework_set SET completed=1 WHERE homework_id=? AND actor_id=?", args)
    
    conn.commit()
    conn.close()


"""INSERTS"""

def insertIntoActors(values):
    """Inserts given array values into actors table"""
    conn = openConnection()
    
    c = conn.cursor()
    c.executemany("INSERT INTO actors (actor_id, name, email, rights, password, salt) VALUES (?,?,?,?,?,?)", (values))
    
    conn.commit()
    conn.close()

def insertIntoClasses(values):
    """Inserts given array values into classes table"""
    conn = openConnection()
    
    c = conn.cursor()
    c.executemany("INSERT INTO classes (class_id, teacher_id, name, description) VALUES (?,?,?,?)", (values))
    
    conn.commit()
    conn.close()

def insertIntoPupils(values):
    """Inserts given array values into pupils table"""
    conn = openConnection()
    
    c = conn.cursor()
    c.executemany("INSERT INTO pupils (actor_id, year, email_notifications) VALUES (?,?,?)", (values))
    
    conn.commit()
    conn.close()

def insertIntoHomework(values):
    """Inserts given array values into homework table"""
    conn = openConnection()
    
    c = conn.cursor()
    c.executemany("INSERT INTO homework (homework_id, teacher_id, class_id, title, description, due) VALUES (?,?,?,?,?,?)", (values))
    
    conn.commit()
    conn.close()

def insertIntoHomeworkset(values):
    """Inserts given array values into homework association
    table"""
    conn = openConnection()
    
    c = conn.cursor()
    c.executemany("INSERT INTO homework_set (homework_set_id, homework_id, actor_id, completed) VALUES (?,?,?,?)", (values))
    
    conn.commit()
    conn.close()

def insertIntoClassmembers(values):
    """Inserts given array values into class members
    association table"""
    conn = openConnection()
    
    c = conn.cursor()
    c.executemany("INSERT INTO class_members (class_id, actor_id) VALUES (?,?)", (values))
    
    conn.commit()
    conn.close()


def rebuildDB():
    """WARNING! UNDOABLE!
    Wipes and rebuilds a clean database
    ALL DATA WILL BE LOST - DOES NOT BACK UP"""
    
    try:
        conn = sqlite3.connect("homeworkDB.db")
        c = conn.cursor()
        c.executescript("""
            DROP TABLE actors;
            DROP TABLE pupils;
            DROP TABLE classes;
            DROP TABLE homework;
            DROP TABLE homework_set;
            DROP TABLE class_members;
                        """)
        
        conn.commit()
    except:
        pass
    finally:
        conn.close()
    
    buildDB()


def buildDB():
    """Builds a clean database and all the tables - expects
    database to not exist, otherwise refuses to run"""
    
    conn = sqlite3.connect("homeworkDB.db")
    
    c = conn.cursor()
    
    c.executescript("""
        CREATE TABLE actors (
            actor_id INTEGER PRIMARY KEY NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            rights INTEGER NOT NULL,
            password TEXT NOT NULL,
            salt TEXT NOT NULL);
            
        
        CREATE TABLE pupils (
            actor_id INTEGER PRIMARY KEY NOT NULL,
            year INTEGER NOT NULL,
            email_notifications INTEGER NOT NULL);
        
        
        CREATE TABLE classes (
            class_id INTEGER PRIMARY KEY NOT NULL,
            teacher_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT);
        
        
        CREATE TABLE homework (
            homework_id INTEGER PRIMARY KEY NOT NULL,
            teacher_id INTEGER NOT NULL,
            class_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due INTEGER NOT NULL);
        
        
        CREATE TABLE class_members (
            class_id INTEGER NOT NULL,
            actor_id INTEGER NOT NULL);
        
        
        CREATE TABLE homework_set (
            homework_set_id INTEGER PRIMARY KEY NOT NULL,
            homework_id INTEGER NOT NULL,
            actor_id INTEGER NOT NULL,
            completed INTEGER NOT NULL);""")
    
    conn.commit()
    conn.close()
    
    return 1