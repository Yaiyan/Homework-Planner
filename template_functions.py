def show_navbar(cgi_attributes, actor, session):
    """Shows the navbar that appears at the top of each page.
    Requires a copy of the session class in order to execute properly.
    
    Depending on a users rights shows different outputs"""
    
    #Load the navbar
    navBarFile = open("navbar.html","r")
    navBar = navBarFile.read()
    if not session.newSession:
        #If the user is logged in then we have to set their
        #name and email address
        navBar = navBar.replace("$name", actor.name)
        navBar = navBar.replace("$email", actor.email)
    
    return navBar


def show_subjects(cgi_attributes, actor, session):
    """Shows the subjects studied by a pupil/taught by the
    teacher"""
    
    #Load the actors associated with the class
    actor.load_classes()
    #The classes are stored in a additional info dictionary
    subjects = actor.additional_info["Classes"]
    #Append 'All' class to start
    subjects = [[0,"All"]]+[[i.id,i.name] for i in subjects]
    
    #Create the return buffer
    to_return = "<p>\n"
    
    for i in subjects:
        #Iterate through subjects and add to the buffer
        to_return += "<a id=\"subject"+str(i[0])+"\" "
        
        if i[0] == 0:
            #Set the 'All' subject to selected
            to_return +=  "class=\"selected\""
        
        #Javascript hook
        to_return +=  "onClick=\"changeSubject("+str(i[0])+")\">"+i[1]+"</a>\n"
        to_return +=  "<br />\n"
    
    to_return +=  "</p>\n"
    
    #Add all the subjects to a javascript array
    to_return += "<script>"
    to_return += "classes = ["
    for i in subjects:
        to_return += "["+str(i[0])+",\""+i[1]+"\"],"
    to_return += "]</script>"
    
    return to_return

###############################################################################

def show_due_homework(cgi_attributes, actor, session):
    """Displays all homework due in to the template.
    Either homework set to pupil, or set by teacher"""
    #Import libraries needed by function
    import datetime
    import time
    
    #Load all homework associated with the actor
    actor.load_homework()
    
    #We are going to sort the homework into a few time
    #categories, so we can say due 'next week'
    homework_set = []
    for i in actor.additional_info["Homework"]:
        #Iterate through the homework and put into a dict
        #which goes into an array
        homework = {
            "ID" : i.id,
            "Title" : i.title,
            "Subject" : i.class_.name,
            "Due" : i.due,
            "Set by" : i.class_.teacher.name,
            "Class id" : i.class_.id,
            "Completed" : i.completed,
            "Description" : i.description.replace("\n","<br />") #Make linebreaks appear correctly
        }
        homework_set.append(homework)
    
    #Create empty arrays for each of the time splits
    dateSplits = [["Late", []],
                  ["Tomorrow", []],
                  ["Two days", []],
                  ["This week", []],
                  ["Next week", []],
                  ["Next month", []],
                  ["Ages", []],
                  ["Old", []]]
    
    #Set the maximum time period for each time category
    dateSplitLimits = [[-86400, "Old"],
                       [0, "Late"],
                       [86400, "Tomorrow"],
                       [86400*2, "Two days"],
                       [86400*7, "This week"],
                       [86400*14, "Next week"],
                       [86400*30, "Next month"],
                       [123456789, "Ages"]]
    
    #Get the current time so we can work out time deltas
    currentTime = time.time()
    
    for i in homework_set:
        timeTillDue = int(i["Due"] - currentTime)
        
        for j in dateSplitLimits:
            #Find the correct time period to put the
            #homework in
            if timeTillDue <= j[0]:
                for k in dateSplits:
                    if k[0] == j[1]:
                        k[1].append(i)
                #Break so it doesn't go in multiple arrays
                break
    
    for i in dateSplits[0][1]:
        #Iterate through the homeworks and remove completed
        #homeworks from the arrays (to put in a new array)
        if int(i["Due"] - currentTime) <= 0:
            if i["Completed"]:
                dateSplits[-1][1].append(i)
                dateSplits[0][1].remove(i)
    
    #To switch boolean value into a string
    text_completed = ["No", "Yes"]
    
    to_return = ""
    
    if actor.rights == 1:
        #If the user is a pupil, show their completion
        #percentage at the top
        if actor.additional_info["Homework Count"] > 0:
            to_return += "You have completed %d%% of set homework." % int(round(actor.additional_info["Homework Completed"]/float(actor.additional_info["Homework Count"])*100,0))
        else:
            to_return += "No set homework!<br /><br />"
    
    for i in dateSplits:
        #Go through homeworks and add them to the page
        if i[1]:
            #Remove spaces to avoid breaking the css classes
            to_return += "<div id=\"due-"+i[0].replace(" ","")+"\" class=\"indent\">\n"
            to_return += "\t<strong>"+i[0]+"</strong>\n"
            for j in i[1]:
                #Use datetime module to translate UNIX time
                due = datetime.datetime.fromtimestamp(j["Due"]).strftime(
                       "%H:%M, %d/%m/%Y")
                
                to_return += "\t<div class=\"homeworkItem class-"+str(j["Class id"])+"\">\n"
                to_return += "\t\t<span class=\"homeworkTitle\">"+j["Title"]+" ("+j["Subject"]+")</span>\n"
                to_return += "\t\t<br />\n"
                to_return += "\t\t<div class=\"homeworkInformation\">\n"
                to_return += "\t\t\t<p>Due: "+due+"</p>\n"
                to_return += "\t\t\t<p>Set by "+j["Set by"]+"</p>\n"
                to_return += "\t\t\t<p>"+j["Description"]+"</p>\n"
                to_return += "\t\t\t<p>Finished: "+text_completed[j["Completed"]]+"</p>\n" if actor.rights == 1 else ""
                to_return += "\t\t</div>\n"
                if actor.rights == 2:
                    #If it's a teacher we should show some
                    #extra links
                    to_return += "\t<br /><a href=\"flag_homework.py?flag=edit&id=%s\">Edit</a> / " % j["ID"]
                    to_return += "<a href=\"flag_homework.py?flag=delete&id=%s\">Delete</a>\n" % j["ID"]
                    to_return += "<a href=\"complete_homework.py?id=%s\" style=\"float:right;margin-right:10px\">Finished by?</a>\n" % j["ID"]
                to_return += "\t</div>\n<br />\n"
            to_return +=  "</div>\n"
    #Add array of dates to the javascript to allow
    #toggling of time periods
    to_return += "<script>"
    to_return += "dateSplits = ["
    for i in dateSplits:
        #Remove spaces to avoid breaking the css classes
        to_return += "[\""+i[0].replace(" ","")+"\","
        for j in i[1]:
            to_return += str(j["Class id"])+","
        to_return += "],"
    to_return += "]</script>"
    
    return to_return


def show_signup_form(cgi_attributes, actor, session):
    """Displays the signup form to the template"""
    
    formFile = open("signupForm.html","r")
    form = formFile.read()
    problems = 0
    #Get the problems from the cgi attributes
    try:
        problems = int(cgi_attributes["p"])
    except:
        pass
    
    name = cgi_attributes["name"]
    email = cgi_attributes["email"]
    
    #If there are problems we display this to the screen
    #And substitute in the old values
    #& is bitwise operation so we can take the flags from
    #the problems number
    if problems&1 == 1:
        form = form.replace("$nameProblem", "problem")
        form = form.replace("$name", "")
    else:
        form = form.replace("$nameProblem", "")
        form = form.replace("$name", name)
    if problems&2 == 2 or problems&8 == 8:
        form = form.replace("$emailProblem", "problem")
        
        if problems&8 == 8:
            form = form.replace("$email", "Already registered!")
            
        form = form.replace("$email", "")
    else:
        form = form.replace("$emailProblem", "")
        form = form.replace("$email", email)
    if problems&4 == 4:
        form = form.replace("$passwordProblem", "problem")
    else:
        form = form.replace("$passwordProblem", "")
    
    return form

def show_add_user_form(cgi_attributes, actor, session):
    """Show the add user form to the template"""
    formFile = open("addUserForm.html","r")
    form = formFile.read()
    problems = 0
    #Get the problems from the cgi attributes
    try:
        problems = int(cgi_attributes["p"])
    except:
        pass
    
    name = cgi_attributes["name"]
    email = cgi_attributes["email"]
    rights = cgi_attributes["rights"]
    
    if rights == "":
        form = form.replace("$pupil", "checked")
    
    #Toggle the correct rights box based off the user right
    if rights == "pupil":
        form = form.replace("$pupil", "checked")
    elif rights == "teacher":
        form = form.replace("$teacher", "checked")
    elif rights == "admin":
        form = form.replace("$admin", "checked")
    else:
        form = form.replace("$pupil", "checked")
    
    
    #If there are problems we display this to the screen
    #And substitute in the old values
    #& is bitwise operation so we can take the flags from
    #the problems number
    if problems&1 == 1:
        form = form.replace("$nameProblem", "problem")
        form = form.replace("$name", "")
    else:
        form = form.replace("$nameProblem", "")
        form = form.replace("$name", name)
    
    if problems&2 == 2 or problems&8 == 8:
        form = form.replace("$emailProblem", "problem")
        
        if problems&8 == 8:
            form = form.replace("$email", "Already registered!")
            
        form = form.replace("$email", "")
    else:
        form = form.replace("$emailProblem", "")
        form = form.replace("$email", email)
    if problems&4 == 4:
        form = form.replace("$passwordProblem", "problem")
    else:
        form = form.replace("$passwordProblem", "")
    
    return form

def show_edit_user_form(cgi_attributes, actor, session):
    """Show the edit user form the template"""
    from model import databaseHandler
    
    #Load template file
    formFile = open("editUserForm.html","r")
    form = formFile.read()
    
    #Get all data relevant to pupils and staff
    pupils = databaseHandler.getAllPupilData()
    staff = databaseHandler.getAllStaffData()
    
    #Join the two arrays together
    users = pupils + staff
    
    #We use this to turn integer rights into a string
    rightsTranslater = {1 : "pupil",
                        2 : "teacher",
                        3 : "admin"}
    
    #Generate a list of users to put into the javascript
    userList = ""
    for i in users:
        if i[3] in rightsTranslater:
            rights = rightsTranslater[i[3]]
        else:
            #Some sort of corruption, silently ignore
            rights = ""
        
        #Build the array
        element = "["
        element += str(i[0])
        element += ",'"
        element += i[1]
        element += "','"
        element += i[2]
        element += "',"
        element += str(i[3])
        element += ",'"
        element += rights
        element += "'"
        if len(i) > 6:
            #Pupils gives two merged tables, so has a longer length than staff
            #Otherwise this line would give an index out of bounds error
            element += ","
            element += str(i[7])
        element += "],"
        userList += element
    
    #Sub the userlist into the javascript
    form = form.replace("$users",userList)
    
    
    return form


def show_bulk_operations_form(cgi_attributes, actor, session):
    """Display the bullk operations form to the template"""
    formFile = open("bulkOperationsForm.html","r")
    form = formFile.read()
    
    return form


def show_add_homework_form(cgi_attributes, actor, session):
    """Display the add homework form to the template"""
    formFile = open("homeworkForm.html","r")
    form = formFile.read()
    
    #Load all classes associated with the actor
    actor.load_classes()
    classes = actor.additional_info["Classes"]
    
    #Build the array of classes to give to the javascript
    classList = ""
    for i in classes:
        element = "["
        element += str(i.id)
        element += ",'"
        element += i.name
        element += "'],"
        classList += element
    
    #Substitute in the action form and other variables
    form = form.replace("$action","try_addhomework.py")
    form = form.replace("$DoneText","Add")
    form = form.replace("$classes",classList)
    
    #Add in some set up javascript
    form += "<script>"
    jsFile = open("edit_homework.js","r")
    form += jsFile.read()
    form += "</script>"
    
    return form

def show_edit_homework_form(cgi_attributes, actor, session):
    """Display the edit homework form to the template"""
    from model import homework
    import datetime
    
    formFile = open("homeworkForm.html","r")
    form = formFile.read()
    
    #Load classes associated with the actor
    actor.load_classes()
    classes = actor.additional_info["Classes"]
    
    #Build array of classes taught
    classList = ""
    for i in classes:
        element = "["
        element += str(i.id)
        element += ",'"
        element += i.name
        element += "'],"
        classList += element
    
    #Set action variable and a few other variables
    form = form.replace("$DoneText","Edit")
    form = form.replace("$action","try_edithomework.py")
    form = form.replace("$classes",classList)
    
    #Load set homework from cgi attributes
    homework_ = homework.Homework()
    homework_.id = cgi_attributes["id"]
    homework_.load()
    
    #Turn the date from UNIX time to a string
    due = datetime.datetime.fromtimestamp(homework_.due).strftime("%H:%M %d/%m/%Y")
    
    #Substitute in the set up javascript
    #Fill the javascript with cgi attributes as page
    #default values
    form += "<script>"
    jsFile = open("edit_homework.js","r")
    js = jsFile.read()
    js = js.replace("$id", str(homework_.id))
    js = js.replace("$title", homework_.title if cgi_attributes["title"] == "" else cgi_attributes["title"])
    js = js.replace("$description", (homework_.description if cgi_attributes["description"] == "" else cgi_attributes["description"]))
    js = js.replace("$due", due if cgi_attributes["due"] == "" else cgi_attributes["due"])
    js = js.replace("$class", str(homework_.class_id) if cgi_attributes["class"] == "" else cgi_attributes["class"])
    form += js
    form += "</script>"
    
    form = form.replace("$DoneText","Edit")
    
    return form


def show_add_class_form(cgi_attributes, actor, session):
    """Display add class form to the template"""
    from model import databaseHandler
    
    formFile = open("classForm.html","r")
    form = formFile.read()
    
    #Get the list of pupils from the database
    pupils = databaseHandler.getAllPupilData()
    
    #Build up array of pupils
    pupilList = ""
    for i in pupils:
        element = "["
        element += str(i[0])
        element += ",'"
        element += i[1]
        element += "',"
        element += str(i[7])
        element += "],"
        pupilList += element
    
    #Substitute pupil list into page
    form = form.replace("$pupils",pupilList)
    form = form.replace("$action","try_addclass.py")
    
    #Add in script to set up default values
    form += "<script>"
    jsFile = open("edit_class.js","r")
    form += jsFile.read()
    form += "</script>"
    
    form = form.replace("$DoneText","Add")
    
    return form

def show_edit_class_form(cgi_attributes, actor, session):
    """Display the edit class form to the template"""
    from model import databaseHandler, schoolclass
    
    formFile = open("classForm.html","r")
    form = formFile.read()
    
    #Get all of the pupils from the database
    pupils = databaseHandler.getAllPupilData()
    
    #Build up list of pupils
    pupilList = ""
    for i in pupils:
        element = "["
        element += str(i[0])
        element += ",'"
        element += i[1]
        element += "',"
        element += str(i[7])
        element += "],"
        pupilList += element
    
    #Substitute the list of pupils into the javascript
    form = form.replace("$pupils",pupilList)
    form = form.replace("$DoneText","Edit")
    form = form.replace("$action","try_editclass.py")
    
    #Load class from database
    class_ = schoolclass.Class()
    class_.id = cgi_attributes["id"]
    class_.load()
    class_.load_members()
    
    #Build list of class members to put in javascript
    class_members = ""
    for i in class_.members:
        class_members += str(i.id)
        class_members += ","
    
    #Set up javascript to set default values and put in
    #values of class being edited (if not cgi attributes)
    form += "<script>"
    jsFile = open("edit_class.js","r")
    js = jsFile.read()
    js = js.replace("$id", str(class_.id))
    js = js.replace("$name", class_.name if cgi_attributes["name"] == "" else cgi_attributes["name"])
    js = js.replace("$description", class_.description if cgi_attributes["description"] == "" else cgi_attributes["description"])
    js = js.replace("$classMembers", class_members if cgi_attributes["pupils"] == "" else cgi_attributes["pupils"])
    form += js
    form += "</script>"
    
    return form

def show_backup_form(cgi_attributes, actor, session):
    """Display the backup form to the template"""
    formFile = open("backupForm.html","r")
    form = formFile.read()
    
    return form




def list_classes(cgi_attributes, actor, session):
    """Display the class list to the template"""
    from model import databaseHandler
    
    #Load all classes taught by the teacher from database
    classes = databaseHandler.getAllClassData(actor.id)
    
    formFile = open("listClassForm.html","r")
    form = formFile.read()
    
    #Build array of classes
    classList = ""
    for i in classes:
        element = "["
        element += str(i[0])
        element += ",'"
        element += i[2]
        element += "','"
        element += i[5]
        element += "'],"
        classList += element
    
    #Substitute the array into the javascript
    form = form.replace("$classes",classList)
    
    return form

def list_pupils(cgi_attributes, actor):
    """Display list of pupils to the template"""
    from model import databaseHandler
    
    #Get all pupils out of database
    pupils = databaseHandler.getAllPupilData()
    
    #Build up array of pupils
    pupilList = ""
    for i in pupils:
        element = "["
        element += str(i[0])
        element += ",'"
        element += str(i[1])
        element += "',"
        element += str(i[7])
        element += "],"
        pupilList += element
    
    return pupilList


def get_homework_percentage(cgi_attributes, actor):
    """Display the homework percentage to the template"""
    from model import actor
    
    #Load the actor from the database
    actor_ = actor.Actor()
    actor_.id = cgi_attributes["id"]
    actor_.load()
    
    #We need to make sure homework has been set to avoid
    #divide by 0 errors
    if actor_.additional_info["Homework Count"] > 0:
        #Calculate the percentage by dividing homework
        #completed by homework set
        #We need to make one a float to avoid integer
        #division
        percentage = "%d%%" % int(round(actor_.additional_info["Homework Completed"]/float(actor_.additional_info["Homework Count"])*100,0))
    else:
        percentage = "100%"
    
    return percentage

def list_all_pupils(cgi_attributes, actor):
    """Lists all the pupils and their percentage of
    complete homework"""
    
    from model import actor
    from model import databaseHandler
    
    #Get all pupils out of database
    pupils = databaseHandler.getAllPupilData()
    
    to_write = ""
    #Build up array of pupils
    data = []
    for i in pupils:
        actor_ = actor.Actor()
        actor_.id = i[0]
        actor_.load()
        
        if actor_.additional_info["Homework Count"] > 0:
            #Calculate the percentage by dividing homework
            #completed by homework set
            #We need to make one a float to avoid integer
            #division
            percentage = int(round(actor_.additional_info["Homework Completed"]/float(actor_.additional_info["Homework Count"])*100,0))
        else:
            percentage = 100
        
        #Append the data to an array
        data.append([percentage, actor_.name])
    
    #Sort data and make from highest to lowest
    data = sorted(data)[::-1]
    
    #Go through data and output it
    for i in data:
        to_write += i[1]
        to_write += ": "
        to_write += str(i[0])
        to_write += "%<br />\n"
    
    return to_write


def complete_homework_pupillist(cgi_attributes, actor):
    """Display list of pupils having completed homework"""
    from model import databaseHandler
    
    #Get all pupils who have set the homework with given id
    pupils = databaseHandler.getAllPupilsForHomework(cgi_attributes["id"])
    
    #Build up array of pupils and whether complete
    pupilList = ""
    for i in pupils:
        element = "["
        element += str(i[4])
        element += ",'"
        element += str(i[5])
        element += "',"
        element += str(i[3])
        element += "],"
        pupilList += element
    
    return pupilList


def show_admin_menubar_form(cgi_attributes, actor, session, page):
    """Show admin menubar"""
    formFile = open("adminMenubar.html","r")
    form = formFile.read()
    
    #Set up values to be substituted into the class
    addUser = "selected" if page == "Add user" else ""
    editUser = "selected" if page == "Edit user" else ""
    bulkOps = "selected" if page == "Bulk operations" else ""
    backup = "selected" if page == "Backup" else ""
    
    #Substitute set values into the class
    form = form.replace("$add_user_selected", addUser)
    form = form.replace("$edit_user_selected", editUser)
    form = form.replace("$bulk_ops_selected", bulkOps)
    form = form.replace("$backup_selected", backup)
    
    return form