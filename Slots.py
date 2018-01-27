#! /usr/bin/python3

import Gui


class UiAndSlots(object):
    def quit(self):
        self.MainWindow.close()

    def loginButtonSlot(self):
        self.goTo("signin")

    def signupButtonSlot(self):
        self.goTo("signup")

    def exitButtonSlot(self):
        self.quit()

    def signinOkButtonSlot(self):
        pass

    def signupOkButtonSlot(self):
        pass

    def twoButtonSlot(self):
        pass

    def fourButtonSlot(self):
        pass

    def leaveButtonSlot(self):
        pass
