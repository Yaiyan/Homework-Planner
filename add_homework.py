#!/usr/bin/python

import controller
import template_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    2 : ["Display", "change_homework.html"],
    3 : ["Redirect", "index.py"]
}
control.template_functions["Navbar"] = [template_functions.show_navbar, {}]
control.template_functions["Add homework"] = [template_functions.show_add_homework_form, {}]
control.template_vars["Page"] = ["constant", "Add homework"]

#Problem handling
control.required_cgi_attributes = ["p", "class", "title", "description", "due"]
control.template_vars["id"] = ["constant", ""]
control.template_vars["title"] = ["cgi attribute", "title"]
control.template_vars["description"] = ["cgi attribute", "description"]
control.template_vars["due"] = ["cgi attribute", "due"]
control.template_vars["class"] = ["function",[lambda cgi_attributes, actor : cgi_attributes["class"] if cgi_attributes["class"] != "" else "-1", {}]]
control.template_vars["TitleProblem"] = ["function",[lambda cgi_attributes, actor : "problem" if int(cgi_attributes["p"])&1 else "", {}]]
control.template_vars["DescriptionProblem"] = ["function",[lambda cgi_attributes, actor : "problem" if int(cgi_attributes["p"])&2 else "", {}]]
control.template_vars["DueProblem"] = ["function",[lambda cgi_attributes, actor : "problem" if int(cgi_attributes["p"])&4 else "", {}]]
control.template_vars["ClassProblem"] = ["function",[lambda cgi_attributes, actor : "problem" if int(cgi_attributes["p"])&8 else "", {}]]

control.run_action()