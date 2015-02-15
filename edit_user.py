#!/usr/bin/python

import controller
import template_functions

rightsTranslater = {"pupil" : str(1),
                    "teacher" : str(2),
                    "admin" : str(3)}

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    3 : ["Display", "indexAdmin.html"]
}
control.template_functions["Navbar"] = [template_functions.show_navbar, {}]
control.template_functions["Menubar"] = [template_functions.show_admin_menubar_form, {"page" : "Edit user"}]
control.template_functions["Admin Content"] = [template_functions.show_edit_user_form, {}]
control.required_cgi_attributes = ["p", "id", "name", "email", "rights", "year"]
control.template_vars["Page"] = ["constant","Edit user"]
control.template_vars["userID"] = ["function",[lambda cgi_attributes, actor : cgi_attributes["id"] if cgi_attributes["id"] != "" else "-1", {}]]
control.template_vars["idVal"] = ["function",[lambda cgi_attributes, actor : cgi_attributes["id"] if cgi_attributes["id"] != "" else "n/a", {}]]
control.template_vars["nameVal"] = ["function",[lambda cgi_attributes, actor : cgi_attributes["name"] if cgi_attributes["name"] != "" else "", {}]]
control.template_vars["emailVal"] = ["function",[lambda cgi_attributes, actor : cgi_attributes["email"] if cgi_attributes["email"] != "" else "", {}]]
control.template_vars["yearVal"] = ["function",[lambda cgi_attributes, actor : cgi_attributes["year"] if cgi_attributes["year"] != "" else "", {}]]
control.template_vars["rightsVal"] = ["function",[lambda cgi_attributes, actor : rightsTranslater[cgi_attributes["rights"]] if cgi_attributes["rights"] != "" else "0", {}]]
control.template_vars["nameProblem"] = ["function",[lambda cgi_attributes, actor : "problem" if int(cgi_attributes["p"])&1 else "", {}]]
control.template_vars["emailProblem"] = ["function",[lambda cgi_attributes, actor : "problem" if int(cgi_attributes["p"])&2 else "", {}]]
control.template_vars["passwordProblem"] = ["function",[lambda cgi_attributes, actor : "problem" if int(cgi_attributes["p"])&4 else "", {}]]
control.run_action()