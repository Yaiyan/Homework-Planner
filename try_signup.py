#!/usr/bin/python

import controller
import controller_functions

control = controller.Controller()
control.actions = {
    0 : ["Function", [controller_functions.try_adduser, {}]],
    1 : ["Redirect", "index.py"]
}
control.required_cgi_attributes = ["name", "email", "password", "password2", "year"]
control.run_action()