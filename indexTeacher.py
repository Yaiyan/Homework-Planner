#!/usr/bin/python

import controller
import template_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "login.py"],
    2 : ["Display", "indexShared.html"],
    3 : ["Redirect", "index.py"]
}
control.template_functions["Navbar"] = [template_functions.show_navbar, {}]
control.template_functions["Homework"] = [template_functions.show_due_homework, {}]
control.template_functions["Subjects"] = [template_functions.show_subjects, {}]
control.run_action()