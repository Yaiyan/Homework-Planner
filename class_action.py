#!/usr/bin/python

import controller
import controller_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    2 : ["Function", [controller_functions.redirect_class_action, {}]],
    3 : ["Redirect", "index.py"]
}
control.required_cgi_attributes = ["class", "edit", "delete"]
control.run_action()