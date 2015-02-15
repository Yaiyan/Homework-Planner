#!/usr/bin/python

import controller
import template_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    2 : ["Display", "homeworkpercentage.html"],
    3 : ["Redirect", "index.py"]
}
control.template_vars["percentage"] = ["function", [template_functions.get_homework_percentage, {}]]
control.required_cgi_attributes = ["id"]
control.run_action()