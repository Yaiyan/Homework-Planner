def signin(session, actor):
    """Signs the user in by setting the user id into the
    session, and saving the session value into the cookie
    """
    session.startNewSession(actor.email)
    session.setSessionValue("UID",actor.email)
    session.setCookie()


def try_login(cgi_attributes, actor, session):
    """Attempt to log the user in"""
    #Get the email and password the user sent
    email = cgi_attributes["email"]
    password = cgi_attributes["password"]
    
    #Try loading the user with the given email
    actor.email = email
    actor.load()
    #Attempt logging in with the sent password
    success = actor.try_login(password)
    
    if success:
        #Set the sessions and cookies to logged in
        signin(session, actor)
        return "index.py", {}
    else:
        #Login failed, return to login form
        del cgi_attributes["password"]
        return "login.py", cgi_attributes


def try_adduser(cgi_attributes, actor_, session):
    """Try to add a new user to the database"""
    from model import actor
    
    #Get new user values from the user
    name = cgi_attributes["name"]
    email = cgi_attributes["email"]
    password = cgi_attributes["password"]
    password2 = cgi_attributes["password2"]
    #Default rights to a pupil
    rights = 1
    
    if actor_.rights == 3:
        #If the adding actor is an admin, we allow them to
        #set the new user rights
        rights = cgi_attributes["rights"]
        
        rightsTranslater = {"pupil" : 1,
                            "teacher" : 2,
                            "admin" : 3}
        
        #Convert from text rights to integer rights
        if rights in rightsTranslater:
            rights = rightsTranslater[rights]
        else:
            rights = 0
    
    #Create a new actor, and send it all needed information
    new_actor = actor.Actor()
    new_actor.name = name
    new_actor.email = email
    new_actor.password = password
    new_actor.rights = rights
    if rights == 1:
        #If the user is a pupil we need to set them a year
        year = cgi_attributes["year"]
        new_actor.additional_info["Year"] = year
    
    #Check whether there is any issues with actor details
    problems = new_actor.check_details()
    
    #Check that the passwords exist and are equal
    password_problems = False
    if not password:
        password_problems = True
    if password != password2:
        password_problems = True
    
    more_chrs = False
    for i in password:
        if ord(i) not in range(65,91) and ord(i) not in range(97,123):
            more_chrs = True
    if not more_chrs:
        password_problems = True
    
    if password_problems:
        problems += 4
    
    #If there was nothing wrong, add the actor to the
    #database
    if not problems:
        new_actor.generate()
        #If logged out, sign the user in
        if actor_.rights == 0:
            logout(cgi_attributes, actor_, session)
            signin(session, new_actor)
        
        return "index.py", {}
    else:
        #Send the problems to the next page
        cgi_attributes["p"] = str(problems)
        #Don't send the email plaintext across the internet
        del cgi_attributes["password"]
        del cgi_attributes["password2"]
        return "add_user.py" if actor_.rights == 3 else "signup.py", cgi_attributes


def change_settings(cgi_attributes, actor, session):
    """Change the user settings"""
    #Get user settings from the user
    email = cgi_attributes["email"]
    password = cgi_attributes["password"]
    password2 = cgi_attributes["password2"]
    
    #If the email has been changed, update user email
    if email:
        actor.email = email
    
    #Check if there is any issues
    problems = actor.check_details()
    
    #Check passwords exist and are equal
    if password:
        actor.password = password
        if not password:
            problems += 4
        if password != password2:
            problems += 4
    
    #If there are no issues then update the actor
    if not problems:
        actor.update()
        session.setSessionValue("UID",actor.email)
        
        return "index.py", {}
    else:
        #Send the problems to the next page
        cgi_attributes["p"] = str(problems)
        #Don't send the email plaintext across the internet
        del cgi_attributes["password"]
        del cgi_attributes["password2"]
        return "settings.py", cgi_attributes


def try_edituser(cgi_attributes, actor_, session):
    """Try to edit the user"""
    from model import actor
    
    #Get the actor id from the user
    actor_id = cgi_attributes["id"]
    
    #If the user has opted to delete the user, delete
    if cgi_attributes["delete"] == "1":
        new_actor = actor.Actor()
        new_actor.id = actor_id
        #You need to load before deleting
        new_actor.load()
        new_actor.delete()
        
        #Return now so we don't cause errors
        return "edit_user.py", {}
    
    #Get the rest of the user details
    name = cgi_attributes["name"]
    email = cgi_attributes["email"]
    password = cgi_attributes["password"]
    password2 = cgi_attributes["password2"]
    rights = cgi_attributes["rights"]
    
    rightsTranslater = {"pupil" : 1,
                        "teacher" : 2,
                        "admin" : 3}
    
    #Convert string rights to integer
    if rights in rightsTranslater:
        rights = rightsTranslater[rights]
    else:
        rights = 0
    
    #Create a new actor with the given details
    new_actor = actor.Actor()
    new_actor.id = actor_id
    new_actor.load()
    new_actor.name = name
    new_actor.email = email
    new_actor.rights = rights
    if rights == 1:
        #If a pupil, we need to set a year
        year = cgi_attributes["year"]
        if not year:
            #Default to year 7
            year = "7"
        new_actor.additional_info["Year"] = year
    
    problems = new_actor.check_details()
    
   #Ensure passwords exist and are equal 
    if password != "":
        if password == password2:
            new_actor.password = password
        else:
            problems += 4
    
    #If no issues, edit the actor in the database
    if not problems:
        new_actor.update()
        return "edit_user.py", {}
    else:
        #Delete passwords, and send problems
        del cgi_attributes["password"]
        del cgi_attributes["password2"]
        cgi_attributes["p"] = problems
        return "edit_user.py", cgi_attributes


def try_addclass(cgi_attributes, actor, session):
    """Try to add a class to the database"""
    from model import schoolclass
    
    #Get the class attributes from the user
    name = cgi_attributes["name"]
    description = cgi_attributes["description"]
    pupils = cgi_attributes["pupils"]
    
    problems = 0
    
    #Make sure there was a name set
    if not name:
        problems += 1
    
    #Pupils are comma delimited
    pupils = pupils.split(",")[:-1]
    
    try:
        if not problems:
            #Convention says trailing _ as class is a built in function
            class_ = schoolclass.Class()
            class_.teacher = actor
            class_.teacher_id = actor.id
            class_.name = name
            class_.description = description
            class_.memberIds = pupils
            #Generate the class
            class_.generate()
        else:
            #Send problems back to the user
            cgi_attributes["p"] = problems
            return "add_class.py", cgi_attributes
    except:
        #If we get some weird error, then just catch it and silently fail
        #Silently failing is the python convention, rather than display an ugly error
        problems += 2
        
        cgi_attributes["p"] = problems
        return "add_class.py", cgi_attributes
    
    return "index.py", {}

def try_editclass(cgi_attributes, actor, session):
    """Try to edit a class"""
    from model import schoolclass
    
    #Get class data from the user
    class_id = cgi_attributes["id"]
    name = cgi_attributes["name"]
    description = cgi_attributes["description"]
    pupils = cgi_attributes["pupils"]
    
    problems = 0
    
    #If no name, we have a problem
    if not name:
        problems += 1
    
    #Pupils are comma delimited
    pupils = pupils.split(",")[:-1]
    
    try:
        if not problems:
            #Set up the class and write to the database
            class_ = schoolclass.Class()
            class_.id = class_id
            class_.load()
            class_.load_members()
            class_.name = name
            class_.description = description
            #We need to send the old pupil ids to the class
            oldPupils = [i.id for i in list(class_.members)]
            class_.memberIds = pupils
            class_.update(oldPupils)
        else:
            cgi_attributes["p"] = problems
            return "edit_class.py", cgi_attributes
    except:
        #If we get some weird error, then just catch it and silently fail
        #Silently failing is the python convention, rather than display an ugly error
        problems += 2
        
        cgi_attributes["p"] = problems
        return "edit_class.py", cgi_attributes
    
    return "index.py", {}

def try_deleteclass(cgi_attributes, actor, session):
    """Try to delete a class from the database"""
    from model import schoolclass
    
    #Get the class id from the user
    class_id = cgi_attributes["class"]
    #Delete hte class
    class_ = schoolclass.Class()
    class_.id = class_id
    class_.delete()
    
    return "index.py", {}


def try_addhomework(cgi_attributes, actor, session):
    """Try to add homework for a class"""
    from model import homework
    import time
    
    #Get homework details
    title = cgi_attributes["title"]
    description = cgi_attributes["description"]
    class_id = cgi_attributes["class"]
    due = cgi_attributes["due"]
    problems = 0
    
    #If there is no title, description or id, set problems
    if not title:
        problems += 1
    if not description:
        problems += 2
    if not class_id:
        problems += 8
    
    due_problems = False
    try:
        #If this throws an error they've likely used the wrong format for the date
        due = time.mktime(time.strptime(due, "%H:%M %d/%m/%Y"))
        
        #Don't let them set a date in the past
        if due < time.time():
            due_problems = True
    except:
        due_problems = True
    
    if due_problems:
        problems += 4
    
    #Check there are no problems
    if not problems:
        #Set up the homework and save it
        homework_ = homework.Homework()
        homework_.teacher_id = actor.id
        homework_.title = title
        homework_.description = description
        homework_.due = due
        homework_.class_id = class_id
        homework_.generate()
    else:
        #Send problems back again
        cgi_attributes["p"] = problems
        return "add_homework.py", cgi_attributes
    
    return "index.py", {}

def try_edithomework(cgi_attributes, actor, session):
    """Try to edit homework"""
    from model import homework
    import time
    
    #Get homework details
    homework_id = cgi_attributes["id"]
    title = cgi_attributes["title"]
    description = cgi_attributes["description"]
    class_id = cgi_attributes["class"]
    due = cgi_attributes["due"]
    problems = 0
    
    #If no title, problems or id, set problem flags
    if not title:
        problems += 1
    if not description:
        problems += 2
    if not class_id:
        problems += 8
    
    try:
        #If this throws an error they've likely used the wrong format for the date
        due = time.mktime(time.strptime(due, "%H:%M %d/%m/%Y"))
    except:
        problems += 4
    
    #Assume the class didn't change
    class_changed = False
    
    if not problems:
        #If no problems, set up a new homework
        homework_ = homework.Homework()
        homework_.id = homework_id
        homework_.load()
        homework_.title = title
        homework_.description = description
        homework_.due = due
        #If a different class id, the class has changed
        if homework_.class_id != class_id: class_changed = True
        homework_.class_id = class_id
        #Update the class
        homework_.update(class_changed)
    else:
        #Send the problems back
        cgi_attributes["p"] = problems
        return "edit_homework.py", cgi_attributes
    
    return "index.py", {}


def bulk_add(cgi_attributes, actor, session):
    """Bulk add to the database"""
    from model import adminFunctions
    
    #Find out if we're adding a user or a class
    csvType = cgi_attributes["type"]
    try:
        if csvType == "user":
            #Insert users function if a user type
            adminFunctions.insertUsersFromCSV(cgi_attributes["file"].file.read())
        if csvType == "class":
            #Insert class function if a class type
            adminFunctions.insertClassesFromCSV(cgi_attributes["file"].file.read())
        return "bulk_operations.py", {}
    except:
        #If there is an error adding the user then return
        #an error to the user
        cgi_attributes["error"] = "true"
        return "bulk_operations.py", cgi_attributes

def forwardYear(cgi_attributes, actor, session):
    """Increment the school year forward by one"""
    from model import adminFunctions
    
    #Call the forward year function
    adminFunctions.forwardYear()
    
    return "index.py", {}


def restore(cgi_attributes, actor, session):
    """Restore the database from a backup"""
    from model import adminFunctions
    #Save the uploaded file as restore.tar.gz
    open("restore.tar.gz","wb").write(cgi_attributes["file"].file.read())
    
    try:
        #Attempt to restore from the backup
        adminFunctions.restoreFromCSV()
        return "backup.py", {}
    except:
        #Failing that return an error
        cgi_attributes["error"] = "restore"
        return "backup.py", cgi_attributes


def try_backup(cgi_attributes, actor, session):
    """Try to back the database up"""
    from model import adminFunctions
    
    try:
        #Call the backup function
        adminFunctions.backupToCSV()
        #Redirect to the backup download
        return "backup.tar.gz", {}
    except:
        #They may have been an error, tell the user
        cgi_attributes["error"] = "backup"
        return "backup.py", cgi_attributes


def change_homework_flag(cgi_attributes, actor, session):
    """Redirects to the correct homework action page"""
    from model import databaseHandler, homework
    
    #Get the action the user wishes to do and the id
    page = cgi_attributes["flag"]
    homework_id = cgi_attributes["id"]
    
    if page == "edit":
        #If edit a homework, redirect to edit page
        return "edit_homework.py", {"id" : homework_id}
    if page == "delete":
        #If delete homework, delete the homework
        homework_ = homework.Homework()
        homework_.id = homework_id
        
        homework_.delete()
    
    #Otherwise redirect back to index
    return "index.py", {}


def try_completehomework(cgi_attributes, actor, session):
    """Try to set homework as complete"""
    from model import databaseHandler
    
    #Pupils that have finished the homework
    pupils = cgi_attributes["pupils"]
    homework_id = cgi_attributes["id"]
    
    #Stored as comma delimited array
    pupils = pupils.split(",")[:-1]
    
    #Wipe all completed homework, and then set homework as
    #completed for applicable users
    databaseHandler.clearCompletedHomework(homework_id)
    databaseHandler.finishHomework(homework_id, pupils)
    
    return "index.py", {}



def redirect_class_action(cgi_attributes, actor, session):
    """Redirect to the correct page for editing classes"""
    
    #If a class has been selected, and edit pressed
    #Redirect to edit class page
    if cgi_attributes["edit"] and cgi_attributes["class"]:
        #Move class attribute to id attribute
        #As this is accepted by edit_class.py
        cgi_attributes["id"] = cgi_attributes["class"]
        del cgi_attributes["class"]
        
        return "edit_class.py", cgi_attributes
    #If delete selected, move to delete class form
    if cgi_attributes["delete"]:
        return "try_deleteclass.py", cgi_attributes
    #If a class has been selected default to edit page
    if cgi_attributes["class"]:
        cgi_attributes["id"] = cgi_attributes["class"]
        del cgi_attributes["class"]
        
        return "edit_class.py", cgi_attributes
    return "list_classes.py", {}



def logout(cgi_attributes, actor, session):
    """Logs the user out"""
    session.logout()
    session.setCookie()
    
    return "index.py", {}