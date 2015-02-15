#!/usr/bin/python

import cgi
import session
import urllib

from model import actor

#Comment when live!
#import cgitb
#cgitb.enable()

#Uncomment for super debug
#print "Content-Type: text/html\n"

class Controller(object):
    """Controller class is used to handle all communication
    between the model and the browser.
    
    Set all required cgi values, variables, functions and
    actions in the class so the controller can act
    consistently across all pages as well as handle
    rights management"""
    
    def __init__(self):
        """Initialise default variables and load the actor
        to handle rights management"""
        self.load_actor()
        
        #Populated by cgi attributes once display method
        #is called
        self.cgi_attributes = {}
        
        #If a file is being uploaded, set true
        self.cgi_file = False
        #Cgi attributes are data sent of post/get
        self.required_cgi_attributes = []
        #Functions that need to be called on the template
        self.template_functions = {}
        #Variables that need to be added to the template
        self.template_vars = {}
        #Any actions that should be carried out on the page
        self.actions = {
            0 : ["None", []]
        }
    
    
    def run_action(self):
        """Internal function for running an action set to
        the controller"""
        
        #Load cgi attributes on the page
        self.load_cgi_attributes()
        
        #Get the current user rights
        user_rights = self.actor.rights
        
        #Work out which action to do for the given user
        #rights
        action = self.select_action(user_rights)
        
        action_type = action[0]
        args = action[1]
        
        if action_type == "None":
            #If action type is none, pass
            pass
        
        if action_type == "Function":
            #Calls a function passed in as the action
            #**array unzips a dictionary, which is very
            #nice as we can deal with all sorts of required function parameters!!!
            
            #Redirects to output from function with cgi
            #attributes from output
            args, self.cgi_attributes = args[0](self.cgi_attributes, self.actor, self.session, **args[1])
            action_type = "Redirect"
        
        if action_type == "Redirect":
            #They need to be sent to another page
            new_address = args
            
            if "file" in self.cgi_attributes:
                #We don't want to send this via get or we'll get crashes
                del self.cgi_attributes["file"]
            
            #Send all cgi attributes to the new page
            #via GET
            params = "?"
            it = 0
            for i in self.cgi_attributes:
                #First attribute is denoted by ?, only
                #subsequent ones are by &
                if it != 0:
                    params += "&"
                #Percent encode the parameters
                params += i + "=" + urllib.quote(str(self.cgi_attributes[i]))
                it += 1
            
            #Sent the new location in the page headers -
            #headers delimted by \n
            print "Location:"+new_address+params+"\n"
        
        if action_type == "Display":
            #Display the given page to the browser
            
            #We need to send the page headers first
            print "Content-Type: text/html\n"
            #Call the templater on the page, and send it
            print self.templater(args)
    
    
    def templater(self, template_filename):
        """Opens the template file for the page and
        prepares the page for display"""
        template_file = open(template_filename,"r")
        template = template_file.read()
        
        #Create an empty template buffer to write to
        templated = ""
        
        for i in template.split("\n"):
            #Iterate through each line in the template and
            #carry out rights management and templating for
            #this line
            stripped_line = i.strip()
            
            #If the line is entirely a comment, check if we
            #need to swap it for a functions output
            if stripped_line[:4] == "<!--" and stripped_line[-3:] == "-->":
                #Get the content of the comment
                template_id = stripped_line[4:][:-3].strip()
                
                #Check if the id is in our list of
                #templated id's
                if template_id in self.template_functions:
                    #If so, we know the function and call
                    #it passing over the various variables
                    #(including unzipping a dictionary)
                    function = self.template_functions[template_id]
                    #Append functions output to template
                    templated += function[0](self.cgi_attributes, self.actor, self.session, **function[1])
            else:
                #If it's not, append the line to the outline
                templated += i
            #Add a newline character
            templated += "\n"
        
        #Swap all variables for their values
        templated = self.template_variables(templated)
        
        #Carry out rights management
        templated = self.rights_templater(templated, self.actor.rights)
        
        #Return the templated file
        return templated
    
    def template_variables(self, template):
        """Assigns variables in template"""
        
        for i in self.template_vars:
            #Iterate through variables to assign and split
            #variable up to it's type and it's arguments
            var_type = self.template_vars[i][0]
            var_args = self.template_vars[i][1]
            #The variable name is prefixed with a $ in the
            #template
            var_name = "$"+i
            
            if var_type == "constant":
                #If a constant, we just replace with the
                #first argument
                template = template.replace(var_name, var_args)
            if var_type == "cgi attribute":
                #If a cgi attribute, just replace with the
                #specified attribute
                template = template.replace(var_name, self.cgi_attributes[var_args])
            if var_type == "function":
                #If it's a function, call the function and
                #assign to variable
                #If error, fail silently
                try:
                    template = template.replace(var_name, var_args[0](self.cgi_attributes, self.actor, **var_args[1]))
                except:
                    #If problems aren't set, lambda functions might raise issues
                    #Standard style for python is to ignore exceptions when we know they
                    #aren't serious
                    pass
        
        #Return templated file
        return template
    
    def rights_templater(self, template, user_rights):
        """"Carries out rights templating on file"""
        
        #Create template buffer
        to_return = ""
        
        #Assume no rights
        rightsRequired = 0
        for i in template.split("\n"):
            #Iterate through each line, check if the line
            #starts with [, if so we get the number
            #following and take that to be the minimum
            #rights to display until the next line
            #starting with ]
            if len(i):
                if i[0] == "[":
                    #Set required rights
                    rightsRequired = int(i[1])
                    continue
                if i[0] == "]":
                    #Assume no rights again
                    rightsRequired = 0
                    continue
            #If the user rights are greater than or equal
            #to the required rights, append the line
            if rightsRequired <= user_rights:
                to_return += i+"\n"
        
        #Return rights templated file
        return to_return
    
    
    
    def load_actor(self):
        """Load actor from session values"""
        self.session = session.Session()
        self.session.load()
        
        self.actor = actor.Actor()
        #Check that the user is already signed in
        if not self.session.newSession:
            #If so, we can load the actor
            self.actor.email = self.session.getSessionValue("UID")
            self.actor.load()
        #No need to check otherwise - default for actor
        #is enough to ensure security
    
    def load_cgi_attributes(self):
        """Load all requested cgi attributes into dict"""
        
        #Prepare form for loading
        form = cgi.FieldStorage()
        
        for i in self.required_cgi_attributes:
            #Iterate through the required attributes and
            #sanitise them, before replacing in dictionary
            self.cgi_attributes[i] = form.getfirst(i,"").replace(">","&gt;").replace("<","&lt;").replace("\"","'")
        
        if self.cgi_file:
            #If it's a file, then we need to treat it a
            #bit differently to get a file object
            self.cgi_attributes["file"] = form["file"]
    
    def select_action(self, user_rights):
        """Select the appropriate action for current user
        rights"""
        #Default to no acceptable action
        action = ["None", []]
        
        #If the action for the user rights given has been
        #set, it's easy and we can just choose those rights
        if user_rights in self.actions:
            action = self.actions[user_rights]
        else:
            #Otherwise, count down from maximum rights and
            #choose the highest acceptable rights for the
            #page
            for i in range(user_rights,-1,-1):
                if i in self.actions:
                    action = self.actions[i]
                    #Break to avoid choosing lower rights
                    break
        
        return action