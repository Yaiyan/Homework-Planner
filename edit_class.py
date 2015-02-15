#!/usr/bin/python

import controller
import template_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    2 : ["Display", "edit_class.html"],
    3 : ["Redirect", "index.py"]
}
control.template_functions["Navbar"] = [template_functions.show_navbar, {}]
control.template_functions["Edit Class"] = [template_functions.show_edit_class_form, {}]
control.required_cgi_attributes = ["p", "name", "description", "pupils", "id"]
control.template_vars["selectedOnly"] = ["constant", "1"]
control.template_vars["NameProblem"] = ["function",[lambda cgi_attributes, actor : "problem" if int(cgi_attributes["p"])&1 else "", {}]]
control.run_action()