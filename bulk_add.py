#!/usr/bin/python

import controller
import controller_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    3 : ["Function", [controller_functions.bulk_add, {}]]
}
control.required_cgi_attributes = ["type","file"]
control.cgi_file = True
control.run_action()