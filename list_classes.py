#!/usr/bin/python

import controller
import template_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    2 : ["Display", "list_classes.html"]
}
control.template_functions["Navbar"] = [template_functions.show_navbar, {}]
control.template_functions["List Classes"] = [template_functions.list_classes, {}]
control.template_vars["Page"] = ["constant","Class list"]
control.run_action()