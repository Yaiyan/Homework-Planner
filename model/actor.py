import databaseHandler
import schoolclass
import homework
import hashlib
import time

class Actor(object):
    """Actor class. This class contains a user as recognised
    by the system and allows for easy user data loading,
    saving, and generation. Information that is specific to
    a certain group of users (ie, pupils or teachers) is
    stored in the additional_rights dictionary. Also contains
    methods for validating user data.
    
    Note: As per project consistency, no getters or setters
    exist, variables are accessed directly and where extra
    logic is necessary a property is used."""
    
    def __init__(self):
        """Constructor method for actor class
        Sets up all data to default values"""
        
        self.id = 0 #Unique identifier for actor in database
        self.name = ""
        self.email = ""
        self._password = "" #_ prefix as accessed via a property
        self.salt = ""
        self.rights = 0 #0 - None
                        #1 - Pupil
                        #2 - Teacher
                        #3 - Admin
        
        self.loaded = False #Used to prevent some recursion errors
        #Any right specific variables are stored in this dictionary
        self.additional_info = {"Email Notifications" : False}
    
    
    def generate(self):
        """Saves the actor into the database. Auto
        increments user ID"""
        conn = databaseHandler.openConnection()
        c = conn.cursor()
        
        c.execute("INSERT INTO actors (name, email, rights, password, salt) VALUES (?,?,?,?,?)", (self.name, self.email, self.rights, self._password, self.salt))
        
        if self.rights == 1:
            #Save all pupil specific data into the database
            c.execute("INSERT INTO pupils (actor_id, year, email_notifications) VALUES (?,?,?)", (c.lastrowid, self.additional_info["Year"], 1))
        
        conn.commit()
        conn.close()
        
        #Reload all data from the database so the user ID
        #is retrieved, and to update to sql-sanitised
        #inputs
        self.load()
    
    def load(self):
        """Loads the actor with the email - self.email, or id - self.id
        Returns 0 if successful, 1 if user does not exist and 2 if user is
        corrupt (hopefully should never occur)"""
        
        conn = databaseHandler.openConnection()
        c = conn.cursor()
        
        #Retrieve the user information from the database
        if self.email != "":
            #If the email is set try to load from the email
            c.execute("SELECT * FROM actors WHERE email=?",[self.email])
        elif self.id != -1:
            #If the id is set try loading from the id
            c.execute("SELECT * FROM actors WHERE actor_id=?",[self.id])
        else:
            #Unable to load the user, so return 1 (error)
            return 1
        
        alldetails = list(c.fetchall())
        
        conn.commit()
        conn.close()
        
        #If the number of details is over 0 then user exists to load; otherwise load fails
        if len(alldetails) > 0:
            """
            0 - ID
            1 - Name
            2 - Email
            3 - Rights
            4 - Password
            5 - Salt
            """
            details = alldetails[0]
            
            try:
                self.id = details[0]
                self.name = details[1]
                self.email = details[2]
                self.rights = details[3]
                self._password = details[4]
                self.salt = details[5]
            except IndexError:
                #This means not enough information was
                #stored in the database to be collected
                #Unfortunately probably means corruption
                return 2
        else:
            return 1
        
        #Set loaded to true to avoid later recursion errors
        self.loaded = True
        
        if self.rights == 1:
            self._load_pupil()
        
        #Safeguard against corruption!
        if self.rights not in range(1,4):
            self.rights = 0
        
        return 0
    
    def _load_pupil(self):
        """If the actor is a pupil they have some extra
        information that must be loaded separately.
        Internal function, shouldn't be called outside of
        actor class"""
        conn = databaseHandler.openConnection()
        c = conn.cursor()
        
        #Retrieve additional pupil information from the database
        c.execute("SELECT * FROM pupils WHERE actor_id=?",[self.id])
        alldetails = list(c.fetchall())
        
        #Retrieve all associated homework
        c.execute("SELECT * FROM homework_set WHERE actor_id=?",[self.id])
        all_homework_details = list(c.fetchall())
        
        conn.commit()
        conn.close()
        
        #Pull any additional information out of the database
        self.additional_info["Year"] = alldetails[0][1]
        self.additional_info["Email Notifications"] = alldetails[0][2]
        #We can increment and append to these variables in the loop below
        self.additional_info["Homework"] = []
        self.additional_info["Homework Count"] = 0
        self.additional_info["Homework Completed"] = 0
        
        for i in all_homework_details:
            #Create an instance of the homework in the database
            #We can then more easily look at information associated
            #with this homework
            homework_ = homework.Homework()
            homework_.id = i[1]
            homework_.completed = i[3]
            self.additional_info["Homework Count"] += 1
            if homework_.completed:
                self.additional_info["Homework Completed"] += 1
            else:
                #Store the homework into our homework array
                self.additional_info["Homework"].append(homework_)
    
    def load_classes(self):
        """Loads all classes associated with the actor,
        whether they be a member of the class or the
        teacher and store it against the actor.
        This must be called manually to avoid any nasty
        recursion errors"""
        conn = databaseHandler.openConnection()
        c = conn.cursor()
        
        #Retrieve all associated classes
        all_classes = []
        if self.rights == 2:
            #If actor is a teacher we merely need to grab classes associated with their id
            c.execute("SELECT * FROM classes WHERE teacher_id=?",[self.id])
            all_classes = list(c.fetchall())
        if self.rights == 1:
            #We grab all pupils class ids from the association table
            c.execute("SELECT * FROM class_members WHERE actor_id=?",[self.id])
            class_members = list(c.fetchall())
            for i in class_members:
                #Next load all the classes with the id
                c.execute("SELECT * FROM classes WHERE class_id=?",[i[0]])
                all_classes += list(c.fetchall())
        
        conn.commit()
        conn.close()
        
        self.additional_info["Classes"] = []
        for i in all_classes:
            #Class is a protected keyboard in python, so preface it with _
            _class = schoolclass.Class()
            _class.id = i[0]
            _class.teacher = self #We do this to avoid recursive errors - doesn't let the pupil have any teaching rights
            _class.load()
            self.additional_info["Classes"].append(_class)
    
    def load_homework(self):
        """Loads all classes associated with the actor,
        whether they be set to member of the class or the
        teacher set it and store it against the actor.
        This must be called manually to avoid any nasty
        recursion errors"""
        conn = databaseHandler.openConnection()
        c = conn.cursor()
        
        #Retrieve all associated homework
        if self.rights == 1:
            #If the user is a pupil, we look for homework relationships
            c.execute("SELECT * FROM homework_set WHERE actor_id=?",[self.id])
        if self.rights == 2:
            #If a teacher it's a bit easier as we are able to
            #look for homeworks with them as the teacher
            c.execute("SELECT * FROM homework WHERE teacher_id=?",[self.id])
        all_homework_details = list(c.fetchall())
        
        conn.commit()
        conn.close()
        
        #Set empty as we are about to populate it
        self.additional_info["Homework"] = []
        for i in all_homework_details:
            #Iterate through homework, load each piece and
            #append loaded homework to homework array
            homework_ = homework.Homework()
            if self.rights == 1:
                #If looking in the relationships table, the id is stored in the second column
                homework_.id = i[1]
            if self.rights == 2:
                #If looking in the homework table, the id is the first column
                homework_.id = i[0]
            #Only relevant for pupils, so no harm in just taking the third column
            homework_.completed = i[3]
            homework_.load()
            self.additional_info["Homework"].append(homework_)
    
    def update(self):
        """Updates the user with id - self.id
        Must load user before updating!"""
        conn = databaseHandler.openConnection()
        c = conn.cursor()
        
        c.execute("UPDATE actors SET name=?, email=?, rights=?, password=? WHERE actor_id=?",(self.name, self.email, self.rights, self._password, self.id))
        
        if self.rights == 1:
            #If the user is a pupil, we need to update the pupils table as well
            c.execute("UPDATE pupils SET year=?, email_notifications=? WHERE actor_id=?",(self.additional_info["Year"], self.additional_info["Email Notifications"], self.id))
        
        conn.commit()
        conn.close()
    
    def delete(self):
        """Deletes the user from the database. CANNOT BE UNDONE!
        Only acts on user ID set to class"""
        conn = databaseHandler.openConnection()
        c = conn.cursor()
        
        if self.id != -1:
            c.execute("DELETE FROM actors WHERE actor_id=?",[self.id])
            if self.rights == 1:
                #If the user is a pupil we also need to delete them from
                #the pupils table, the class members table and also any
                #homework that has been set to them
                c.execute("DELETE FROM pupils WHERE actor_id=?",[self.id])
                c.execute("DELETE FROM homework_set WHERE actor_id=?",[self.id])
                c.execute("DELETE FROM class_members WHERE actor_id=?",[self.id])
                conn.commit()
                conn.close()
            if self.rights == 2:
                #If the user is a teacher we need to delete any classes that they teach
                c.execute("SELECT class_id FROM classes WHERE teacher_id=?",[self.id])
                class_ids = list(c.fetchall())
                conn.commit()
                conn.close()
                for i in class_ids:
                    #We delete them via the schoolclass Class as it ensures
                    #that the class is deleted cleanly (all pupils and homework
                    #are removed, etc.)
                    class_ = schoolclass.Class()
                    class_.id = i[0]
                    class_.load()
                    class_.delete()
    
    
    def check_details(self):
        """Checks the legality of provided variables, returns problems as binary flags
        1 - Name
        2 - Email
        4 - Password"""
        
        #We start off with the assumption there is no problems
        #as problems arise then we document them
        #- only at the end convert this into binary flags
        #If we set the binary flags as problems are being
        #discovered then we could end up inadvertantly
        #changing other flags through carelessness
        problems = {
            "Name" : False,
            "Email" : False,
            "Password" : False
        }
        
        #If they have no name set, or the length of the
        #name is over 40 characters, then we have a problem
        if not self.name:
            problems["Name"] = True
        if len(self.name) > 40:
            problems["Name"] = True
        #Make sure there are no numbers in the name
        for i in self.name:
            if i in ["1","2","3","4","5","6","7","8","9","0"]:
                problems["Name"] = True
        
        #If they have no email set, or the length of the
        #email is over 40 characters, there's a problem
        if not self.email:
            problems["Email"] = True
        if len(self.email) > 60:
            problems["Email"] = True
        
        
        #TEST FOR EMAIL COMPLIANCE
        #Note: the actual email specification is massive,
        #as such we are doing more of a sanity test - some
        #legal emails will be disallowed, but they are
        #unlikely to be in use
        
        #We require at least 1 @ and . (as per the email
        #secification, 2 @'s is, in fact, allowed
        #As such we can keep a tally of how many times
        #each appears
        symbol_count = {"@":0,".":0}
        
        for i in self.email:
            if i == "@":
                symbol_count["@"] += 1
            if i == ".":
                #We only want to count .'s if there is
                #already an @ - .'s before the @ do not
                #interest us in checking for compliance
                if symbol_count["@"] > 0:
                    symbol_count["."] += 1
        
        #If there is no @ or ., the email fails sanity test
        if symbol_count["@"] == 0 or symbol_count["."] == 0:
            problems["Email"] = True
        
        conn = databaseHandler.openConnection()
        c = conn.cursor()
        
        #See if there are already any users in the database with their email
        c.execute("SELECT * FROM actors WHERE email=?",[self.email])
        users  = c.fetchall()
        if len(users) > 0:
            #There is already a user in the database with this email
            if users[0][0] != self.id:
                #Check that it is a different user, it may not be a big deal
                #if the user is trying to (eg) change other settings
                problems["Email"] = True
        
        conn.commit()
        conn.close()
        
        problems_flags = 0
        
        #Set the flags, we are transfering the errors as a
        #series of binary flags, packed in a single number
        #Smallest bit is a name problem, then email, and
        #most significant of the three is password. More
        #bits that are bigger can additionally be set by
        #parts of code if necessary later on
        if problems["Name"]:
            problems_flags += 1
        if problems["Email"]:
            problems_flags += 2
        if problems["Password"]:
            problems_flags += 4
        
        return problems_flags
    
    
    def hash_password(self, password):
        """Returns the given password in hashed and salted form. The hashing mechanism is
        SHA512 and it is salted with the current Unix time."""
        
        #If there is no salt already existing then we need
        #to create our own one - we're using the current
        #Unix time as our hash, but this can be changed at
        #a later point with no issues at all
        if self.salt == "":
            self.salt = str(time.time())
        
        #Concatenate password and salt, before hashing with
        #sha512. We add the salt as a string to the
        #password to increase entropy
        return hashlib.sha512(password+self.salt).hexdigest()
    
    def try_login(self, password):
        """Takes an unhashed password and returns true if
        the password is correct - otherwise false"""
        #Check that our current password in the class is
        #the same as the password passed to us, hashed
        if self.hash_password(password) == self._password:
            return True
        else:
            #Passwords don't match
            return False
    
    
    #Properties are a neat feature in python that allows
    #you to run a function when a variable is modified
    #without the need for a setter like in Java
    
    @property
    def password(self):
        """There is never a need to return the password to
        the user, if if it's hashed. This doesn't provide
        full 'private' protection, as in C or Java, but
        it's enough to prevent programmer error"""
        return ""
    
    @password.setter
    def password(self, password):
        """Sets the password of the user in this instance
        of the class. The password is automatically stored
        in salted and hashed form. Not even this class
        stores the password in unhashed form for security."""
        
        self._password = self.hash_password(password)