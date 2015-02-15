#!/usr/bin/python

import controller
import controller_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    1 : ["Function", [controller_functions.logout, {}]]
}
control.run_action()