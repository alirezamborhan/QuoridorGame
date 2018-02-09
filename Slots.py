#! /usr/bin/python3

import requests
import json

import Gui
import Urls
import Game


class UiAndSlots(object):
    def _set_bottom_info(self, text):
        # Log.
        if len(text) > 100:
            with open("QuoridorLog1.html", "w") as f:
                f.write(text)
        self.infoBottomLabel.setText(text)

    def _set_info(self, text):
        self.infoLabel.setText(text)

    def quit(self):
        self.MainWindow.close()

    def loginButtonSlot(self):
        self.goTo("signin")

    def signupButtonSlot(self):
        self.goTo("signup")

    def exitButtonSlot(self):
        self.quit()

    def actionExitSlot(self):
        self.quit()

    def signinOkButtonSlot(self):
        username = self.signinUsernameInput.text()
        password = self.signinPasswordInput.text()
        payload = {"username": username, "password": password}
        try:
            response = self.session.post(Urls.urls["signin"], data=payload)
        except requests.exceptions.ConnectionError:
            self._set_bottom_info("Connection failed.")
            return
        if response.ok:
            self._set_info(response.text)
            self._set_bottom_info("")
            self.username = username
            if response.text != "You're already in a game.":
                self.goTo("twoOrFour")
            else:
                self.goTo("game")
                Game._wait_for_turn_thread("")
        else:
            self._set_info("")
            self._set_bottom_info(response.text)

    def signupOkButtonSlot(self):
        name = self.signupNameInput.text()
        username = self.signupUsernameInput.text()
        password = self.signupPasswordInput.text()
        payload = {"username": username, "password": password, "name": name}
        try:
            response = self.session.post(Urls.urls["signup"], data=payload)
        except requests.exceptions.ConnectionError:
            self._set_bottom_info("Connection failed.")
            self._set_info("")
            return
        if response.ok:
            self._set_info(response.text)
            self._set_bottom_info("")
            self.goTo("menu")
        else:
            self._set_info("")
            self._set_bottom_info(response.text)

    def twoButtonSlot(self):
        payload = {"players": "two"}
        try:
            response = self.session.post(Urls.urls["two_or_four"], data=payload)
        except requests.exceptions.ConnectionError:
            self._set_bottom_info("Connection failed.")
            return
        if response.ok:
            self._set_info(response.text)
            self._set_bottom_info("")
            self.goTo("game")
            Game._wait_for_turn_thread("", starting=True)
        else:
            self._set_info("")
            self._set_bottom_info(response.text)

    def fourButtonSlot(self):
        payload = {"players": "four"}
        try:
            response = self.session.post(Urls.urls["two_or_four"], data=payload)
        except requests.exceptions.ConnectionError:
            self._set_bottom_info("Connection failed.")
            return
        if response.ok:
            self._set_info(response.text)
            self._set_bottom_info("")
            self.goTo("game")
            Game._wait_for_turn_thread("", starting=True)
        else:
            self._set_info("")
            self._set_bottom_info(response.text)

    def leaveButtonSlot(self):
        if self.stopped:
            self.goTo("twoOrFour")
            return
        try:
            response = self.session.get(Urls.urls["leave"])
        except requests.exceptions.ConnectionError:
            self._set_bottom_info("Connection failed.")
            return
        if response.ok:
            result = json.loads(response.text)
            self._set_info(result["status"])
            self._set_bottom_info("")
            self.stopped = True
            self.goTo("twoOrFour")
        else:
            try:
                result = json.loads(response.text)
            except ValueError:
                self._set_info("")
                self._set_bottom_info(response.text)
                return
            self._set_info("")
            self._set_bottom_info(result["error"])
            self.goTo("twoOrFour")
