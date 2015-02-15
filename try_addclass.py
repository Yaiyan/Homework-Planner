#!/usr/bin/python

import controller
import controller_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    2 : ["Function", [controller_functions.try_addclass, {}]],
    3 : ["Redirect", "index.py"]
}
control.required_cgi_attributes = ["name", "description", "pupils", "teacher"]
control.run_action()