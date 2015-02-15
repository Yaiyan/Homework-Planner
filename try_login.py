#!/usr/bin/python

import controller
import controller_functions

control = controller.Controller()
control.actions = {
    0 : ["Function", [controller_functions.try_login, {}]],
    1 : ["Redirect", "index.py"]
}
control.required_cgi_attributes = ["email", "password"]
control.run_action()