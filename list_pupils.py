#!/usr/bin/python

import controller
import template_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    2 : ["Display", "list_pupils.html"],
    3 : ["Redirect", "index.py"]
}
control.template_functions["Navbar"] = [template_functions.show_navbar, {}]
control.template_vars["pupils"] = ["function", [template_functions.list_pupils, {}]]
control.run_action()