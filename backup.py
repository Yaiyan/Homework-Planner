#!/usr/bin/python

import controller
import template_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    3 : ["Display", "indexAdmin.html"]
}
control.required_cgi_attributes = ["error"]
control.template_functions["Navbar"] = [template_functions.show_navbar, {}]
control.template_functions["Menubar"] = [template_functions.show_admin_menubar_form, {"page" : "Backup"}]
control.template_functions["Admin Content"] = [template_functions.show_backup_form, {}]
control.template_vars["Page"] = ["constant","Backup/restore"]
control.template_vars["Error"] = ["cgi attribute","error"]
control.run_action()