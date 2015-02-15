#!/usr/bin/python

import controller
import controller_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    2 : ["Function", [controller_functions.try_editclass, {}]],
    3 : ["Redirect", "index.py"]
}
control.required_cgi_attributes = ["id", "name", "description", "pupils"]
control.run_action()