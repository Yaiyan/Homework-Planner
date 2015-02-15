#!/usr/bin/python

import controller
import controller_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    3 : ["Function", [controller_functions.try_adduser, {}]]
}
control.required_cgi_attributes = ["name", "email", "password", "password2", "rights", "year"]
control.run_action()