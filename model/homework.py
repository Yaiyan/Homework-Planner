import databaseHandler
import actor
import schoolclass

class Homework:
    """Homework class. This class contains the model for a
    set piece of homework. Useful for loading, generating
    or updating a piece of homework.
    
    Note: As per project consistency, no getters or setters
    exist, variables are accessed directly and where extra
    logic is necessary a property is used."""
    
    def __init__(self):
        """Constructor for Homework class, sets up all
        default values needed for correct functioning of
        the class.
        
        Note: saving with these values will cause
        unpredicatable results."""
        
        self.id = 0
        self.teacher_id = 0
        self.class_id = 0
        self.title = ""
        self.description = ""
        self.due = 0
        
        self.class_ = None
        self.completed = False
    
    
    def generate(self):
        """Saves the homework into the database. Auto
        increments homework ID.
        
        Also assigns the hoemwork"""
        
        conn = databaseHandler.openConnection()
        c = conn.cursor()
        
        c.execute("INSERT INTO homework (teacher_id, class_id, title, description, due) VALUES (?,?,?,?,?)", (self.teacher_id, self.class_id, self.title, self.description, self.due))
        
        self.id = c.lastrowid
        
        conn.commit()
        conn.close()
        
        #Reload to ensure all values are up to date with the database
        self.load()
        
        #Create an empty list of class members - this will
        #be populated below
        class_member_ids = []
        
        self.class_.load_members()
        for i in self.class_.members:
            #We populate this via a loop in order to avoid
            #ugly lambda syntax
            class_member_ids.append(i.id)
        
        conn = databaseHandler.openConnection()
        c = conn.cursor()
        
        for i in class_member_ids:
            c.execute("INSERT INTO homework_set (homework_id, actor_id, completed) VALUES (?,?,?)", (self.id, i, 0))
        
        conn.commit()
        conn.close()
    
    def load(self):
        """Loads the homework with the id - self.id
        Returns 0 if successful, 1 if homework does not
        exist and 2 if homework is corrupt (hopefully
        should never occur)"""
        
        conn = databaseHandler.openConnection()
        c = conn.cursor()
        
        #Retrieve the homeworks information from the database
        c.execute("SELECT * FROM homework WHERE homework_id=?",[self.id])
        
        alldetails = list(c.fetchall())
        
        conn.commit()
        conn.close()
        
        #If the number of details is over 0 then homework exists to load; otherwise load fails
        if len(alldetails) > 0:
            """
            0 - ID
            1 - Teacher ID
            2 - Class ID
            3 - Title
            4 - Description
            5 - Due
            """
            details = alldetails[0]
            
            try:
                self.id = details[0]
                self.teacher_id = details[1]
                self.class_id = details[2]
                self.title = details[3]
                self.description = details[4]
                self.due = details[5]
            except IndexError:
                #This happens if we try accessing a column
                #that doesn't exist - likely caused by
                #corruption
                return 2
        else:
            return 1
        
        #Load the class and store it in class_ variable
        #(Actual expected way of doing this is to create
        #variable, and then load it)
        self.class_ = schoolclass.Class()
        self.class_.id = self.class_id
        self.class_.load()
        
        return 0
    
    def update(self, changed_class=False):
        """Updates the homework with id - self.id.
        If the class the homework has been set to is
        changed, pass changed_class as true so that we can
        update the relationships table to reflect this."""
        conn = databaseHandler.openConnection()
        c = conn.cursor()
        
        c.execute("UPDATE homework SET teacher_id=?, class_id=?, title=?, description=?, due=? WHERE homework_id=?",(self.teacher_id,
                                                                                                                     self.class_id,
                                                                                                                     self.title,
                                                                                                                     self.description,
                                                                                                                     self.due,
                                                                                                                     self.id))
        
        if changed_class:
            #The class has changed, this means that we need
            #to delete this homework from any pupils it has
            #already been set to,
            c.execute("DELETE FROM homework_set WHERE homework_id=?",[self.id])
            
            conn.commit()
            conn.close()
            
            self.class_ = schoolclass.Class()
            self.class_.id = self.class_id
            self.class_.load()
            #Manually load the class members, as this can
            #cause recursive errors at times
            self.class_.load_members()
            
            class_member_ids = []
            for i in self.class_.members:
                #As above, iteratively append id's to avoid
                #ugly lambda syntax
                class_member_ids.append(i.id)
            
            conn = databaseHandler.openConnection()
            c = conn.cursor()
            
            #Finally update the relationship table again so
            #the homework is set to members of the class
            for i in class_member_ids:
                c.execute("INSERT INTO homework_set (homework_id, actor_id, completed) VALUES (?,?,?)", (self.id,
                                                                                                         i,
                                                                                                         0))
        
        conn.commit()
        conn.close()
    
    def delete(self):
        """Deletes the homework from the database. CANNOT
        BE UNDONE! Deletes the homework with the id -
        self.id. Also deletes any homework associations"""
        conn = databaseHandler.openConnection()
        c = conn.cursor()
        
        if id != -1:
            #Don't try deleting the class if it hasn't been
            #properly loaded
            c.execute("DELETE FROM homework WHERE homework_id=?",[self.id])
            c.execute("DELETE FROM homework_set WHERE homework_id=?",[self.id])
        
        conn.commit()
        conn.close()