#!/usr/bin/python

import controller
import template_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    2 : ["Display", "add_class.html"],
    3 : ["Redirect", "index.py"]
}
control.template_functions["Navbar"] = [template_functions.show_navbar, {}]
control.template_functions["Add class"] = [template_functions.show_add_class_form, {}]

#Problem handling
control.required_cgi_attributes = ["p", "name", "description", "pupils"]
control.template_vars["selectedOnly"] = ["constant", "0"]
control.template_vars["id"] = ["constant", ""]
control.template_vars["name"] = ["cgi attribute", "name"]
control.template_vars["description"] = ["cgi attribute", "description"]
control.template_vars["classMembers"] = ["cgi attribute", "pupils"]
control.template_vars["NameProblem"] = ["function",[lambda cgi_attributes, actor : "problem" if int(cgi_attributes["p"])&1 else "", {}]]
control.run_action()