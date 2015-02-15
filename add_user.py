#!/usr/bin/python

import controller
import template_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    3 : ["Display", "indexAdmin.html"]
}
control.template_functions["Navbar"] = [template_functions.show_navbar, {}]
control.template_functions["Menubar"] = [template_functions.show_admin_menubar_form, {"page" : "Add user"}]
control.template_functions["Admin Content"] = [template_functions.show_add_user_form, {}]
control.required_cgi_attributes = ["p", "name", "email", "rights", "year"]
control.template_vars["Page"] = ["constant","Add user"]
control.run_action()