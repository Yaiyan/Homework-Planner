#!/usr/bin/python

import controller
import template_functions

control = controller.Controller()
control.actions = {
    0 : ["Display", "login.html"],
    1 : ["Redirect", "index.py"]
}
control.template_functions["Navbar"] = [template_functions.show_navbar, {}]
control.run_action()