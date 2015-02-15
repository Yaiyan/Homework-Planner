#!/usr/bin/python

import controller
import template_functions

control = controller.Controller()
control.actions = {
    0 : ["Display", "signup.html"],
    1 : ["Redirect", "index.py"]
}
control.template_functions["Navbar"] = [template_functions.show_navbar, {}]
control.template_functions["Sign up"] = [template_functions.show_signup_form, {}]
control.required_cgi_attributes = ["p", "name", "email"]
control.run_action()