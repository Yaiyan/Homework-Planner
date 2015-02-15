#!/usr/bin/python

import controller
import controller_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    1 : ["Function", [controller_functions.change_homework_flag, {}]]
}
control.required_cgi_attributes = ["flag", "id"]
control.run_action()