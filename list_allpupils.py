#!/usr/bin/python

import controller
import template_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    2 : ["Display", "list_allpupils.html"],
    3 : ["Redirect", "index.py"]
}
control.template_vars["pupils"] = ["function", [template_functions.list_all_pupils, {}]]
control.required_cgi_attributes = ["id"]
control.run_action()