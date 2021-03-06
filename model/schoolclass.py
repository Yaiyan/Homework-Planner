import databaseHandler
import actor

class Class:
    """Schoolclass class. This class contains the model for
    a school class and is used for loading, generating and
    updating a schoolclass.
    
    Note: As per project consistency, no getters or setters
    exist, variables are accessed directly and where extra
    logic is necessary a property is used."""
    
    def __init__(self):
        """Constructor for Class, sets up all the default
        values needed for correct functioning of the class.
        
        Note: saving with these default values will cause
        unpredictable results"""
        self.id = 0
        self.teacher_id = 0
        self.name = ""
        self.description = ""
        
        self.memberIds = []
        self.members = []
        self.teacher = actor.Actor()
    
    
    def generate(self):
        """Creates a new schoolclass in the database with
        the values provided. All class members given are
        associated with the class in this method."""
        
        conn = databaseHandler.openConnection()
        c = conn.cursor()
        
        c.execute("INSERT INTO classes (teacher_id, name, description) VALUES (?,?,?)", (self.teacher_id, self.name, self.description))
        
        self.id = c.lastrowid
        
        #Iterate through members of the class and add them
        #to the database
        for i in self.memberIds:
            c.execute("INSERT INTO class_members (class_id, actor_id) VALUES (?,?)", (self.id, i))
        
        conn.commit()
        conn.close()
        
        #Reload the class to update all values
        self.load()
    
    def load(self):
        """Loads the class with the id - self.id
        Returns 0 if successful, 1 if class does not exist and 2 if class is
        corrupt (hopefully should never occur)"""
        
        conn = databaseHandler.openConnection()
        c = conn.cursor()
        
        #Retrieve the classes information from the database
        c.execute("SELECT * FROM classes WHERE class_id=?",[self.id])
        
        alldetails = list(c.fetchall())
        
        conn.commit()
        conn.close()
        
        #If the number of details is over 0 then class exists to load; otherwise load fails
        if len(alldetails) > 0:
            """
            0 - ID
            1 - Teacher ID
            2 - Name
            3 - Description
            """
            details = alldetails[0]
            
            try:
                self.id = details[0]
                self.teacher_id = details[1]
                self.name = details[2]
                self.description = details[3]
            except IndexError:
                #IndexError means that a column doesn't
                #exist, probably means corruption
                return 2
        else:
            return 1
        
        #Finally load the teacher if not already loaded
        if not self.teacher.loaded:
            self.teacher.id = self.teacher_id
            self.teacher.load()
        
        return 0
    
    def load_members(self):
        """Load the members to the class. Be careful when
        calling this method as it can cause recursive
        errors under some circumstances."""
        conn = databaseHandler.openConnection()
        c = conn.cursor()
        
        #Retrieve the class to actor association table
        c.execute("SELECT * FROM class_members WHERE class_id=?",[self.id])
        
        alldetails = list(c.fetchall())
        
        #Load all actors and place them in members array
        for i in alldetails:
            actor_ = actor.Actor()
            actor_.id = i[1]
            actor_.load()
            self.members.append(actor_)
        
        conn.commit()
        conn.close()
    
    
    def update(self, oldMemberIds=[]):
        """Updates the class with id - self.id
        If changing the members of the class, provide the
        members before the update as an argument to this
        function so they can be updated correctly."""
        
        conn = databaseHandler.openConnection()
        c = conn.cursor()
        
        c.execute("UPDATE classes SET teacher_id=?, name=?, description=? WHERE class_id=?",(self.teacher_id, self.name, self.description, self.id))
        
        #Ensure the member id's are an int array instead of
        #strings
        self.memberIds = [int(i) for i in self.memberIds]
        
        if sorted(oldMemberIds) != sorted(self.memberIds):
            #Now check that the members of the class have
            #actually changed
            
            #Get the users that exist in the old array, but
            #not the new one - and as such are deleted
            deletedUsers = [(i,) for i in list(set(oldMemberIds) - set(self.memberIds))]
            #Get the users that exist in the new array, but
            #not the ikd one - and as such are being added
            newUsers = [(i,) for i in list(set(self.memberIds) - set(oldMemberIds))]
            
            if deletedUsers:
                #Delete the users from the database
                c.executemany("DELETE FROM class_members WHERE actor_id=?", deletedUsers)
                
                #Get all homework that needs to be removed
                c.execute("SELECT homework_id FROM homework WHERE class_id=?",(self.id,))
                homework_ids = list(c.fetchall())
                
                #Generate all possible combinations of
                #pupils and set homework
                args = [(i[0],j[0]) for j in homework_ids for i in deletedUsers]
                
                c.executemany("DELETE FROM homework_set WHERE actor_id=(?) AND homework_id=(?) AND completed=0", args)
            if newUsers:
                #Merge pupil id's with class id's ready for
                #insertion into database
                class_members = [(self.id, i[0]) for i in newUsers]
                
                #Insert into class member association and
                #get all homework assigned to the class
                c.executemany("INSERT INTO class_members (class_id, actor_id) VALUES (?,?)", class_members)
                c.execute("SELECT homework_id FROM homework WHERE class_id=?",(self.id,))
                
                #Generate all possible combinations of
                #pupils and set homework, arg[2] is whether
                #or not the homework is completed (assume
                #false)
                homework_ids = list(c.fetchall())
                args = [(j[0],i[0],0) for j in homework_ids for i in newUsers]
                
                c.executemany("INSERT INTO homework_set (homework_id, actor_id, completed) VALUES (?,?,?)", args)
        
        conn.commit()
        conn.close()
    
    def delete(self):
        """Deletes the homework from the database. CANNOT
        BE UNDONE! Deletes the class with the id - self.id.
        Also deletes any homework set for that class"""
        conn = databaseHandler.openConnection()
        c = conn.cursor()
        
        if id != -1:
            c.execute("DELETE FROM classes WHERE class_id=?",[self.id])
            c.execute("DELETE FROM class_members WHERE class_id=?",[self.id])
            
            c.execute("SELECT homework_id FROM homework WHERE class_id=?",(self.id,))
            
            homework_ids = list(c.fetchall())
            args = [(j[0],) for j in homework_ids]
            
            c.executemany("DELETE FROM homework WHERE homework_id=?", args)
            c.executemany("DELETE FROM homework_set WHERE homework_id=?", args)
        
        conn.commit()
        conn.close()
