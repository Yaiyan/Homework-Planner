#!/usr/bin/python

import controller
import controller_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "index.py"],
    3 : ["Function", [controller_functions.forwardYear, {}]]
}
control.run_action()