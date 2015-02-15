#!/usr/bin/python

import controller
import controller_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    1 : ["Function", [controller_functions.change_settings, {}]]
}
control.required_cgi_attributes = ["email", "password", "password2"]
control.run_action()