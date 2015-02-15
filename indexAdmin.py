#!/usr/bin/python

import controller
import template_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "login.py"],
    3 : ["Redirect", "add_user.py"] #Admins don't have an index page
}
control.run_action()