#!/usr/bin/python

import controller
import template_functions

control = controller.Controller()
control.actions = {
    0 : ["Redirect", "home.py"],
    1 : ["Redirect", "indexStudent.py"],
    2 : ["Redirect", "indexTeacher.py"],
    3 : ["Redirect", "indexAdmin.py"]
}
control.run_action()