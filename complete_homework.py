#!/usr/bin/python

import controller
import template_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    2 : ["Display", "complete_homework.html"],
    3 : ["Redirect", "index.py"]
}
control.template_functions["Navbar"] = [template_functions.show_navbar, {}]
control.template_vars["pupils"] = ["function", [template_functions.complete_homework_pupillist, {}]]
control.template_vars["id"] = ["cgi attribute", "id"]
control.required_cgi_attributes = ["id"]
control.run_action()