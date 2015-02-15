#!/usr/bin/python

import controller
import template_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    1 : ["Display", "settings.html"]
}
control.template_functions["Navbar"] = [template_functions.show_navbar, {}]
control.template_vars["Email"] = ["function",[lambda cgi_attributes, actor : actor.email if not cgi_attributes["email"] else cgi_attributes["email"], {}]]
control.template_vars["emailProblem"] = ["function",[lambda cgi_attributes, actor : "problem" if int(cgi_attributes["p"])&2 else "", {}]]
control.template_vars["passwordProblem"] = ["function",[lambda cgi_attributes, actor : "problem" if int(cgi_attributes["p"])&4 else "", {}]]
control.required_cgi_attributes = ["p", "email"]
control.run_action()