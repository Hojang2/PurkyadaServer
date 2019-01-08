# -*- coding: utf-8 -*-

import structures
from time import clock, sleep
import json

class Group:

    def __init__(self, name):
        self.name = name
        self.__users = []

    def add(self, u):
        self.__users.append(u)

    def remove(self, u):
        self.__users.remove(u)

    def list(self):
        return self.__users


class User:

    def __init__(self, name, group, default_directory):
        self.name = name
        self.group = group
        self.group.add(self)
        self.remote_address = None
        self.default_directory = default_directory
        self.path = default_directory.path
        self.connected = False
        self.__connection = None
        self.data = False
        self.action = None
        self.argv = None
        self.cwd = default_directory
        self.answer = None
        self.root = False

    def cd(self):

        if self.argv[0] == "..":

            self.cwd = self.cwd.upper_directory

        elif self.argv[0] == "/":

            self.cwd = self.default_directory

        else:
            if len(self.cwd.ls(self)) == 1:
                self.enter_directory(self.cwd.ls(self)[0])
            else:
                for obj in self.cwd.ls(self):
                    self.enter_directory(obj)

        self.path = self.cwd.path

    def enter_directory(self, obj):
        if obj.name == self.argv[0]:
            if obj.type == "directory":
                self.cwd = obj
            else:
                print("Target is not Directory")

    def do_action(self):

        self.answer = False

        if self.action == "exit":
            self.answer = "Exiting"
            exit()

        if self.action == "cd":
            self.cd()
            self.answer = self.path

        if self.action == "ls":
            tmp = ""
            for obj in self.cwd.ls(self):
                tmp += obj.name + "\n"
            self.answer = tmp

        if self.action == "pwd":
            self.answer = self.path

        if self.action == "read":
            for obj in self.cwd.ls(self):
                if obj.name == self.argv:
                    if obj.type == "file":
                        self.answer = obj.read()
                    else:
                        self.answer = "Target is directory"

        if self.action == "disconnect":
            self.connected = False
            self.answer = "True"

    def run_connected(self):
        self.connected = True
        while self.connected:
            try:
                self.receive_data()
                self.data = json.loads(self.data)

                self.action, self.argv = self.data["action"], self.data["argv"]

                self.do_action()
                sleep(0.1)
                self.send_data(self.answer)
            except OSError as e:
                print("disconnecting user {} from server".format(self.name))
                break

    def run(self):
        while True:
            self.action, *self.argv = input(self.path + "$:").split(" ")

            self.do_action()
            print(self.answer)

    def set_connection(self, connection):
        self.__connection = connection

    def receive_data(self):
        length = int(self.__connection.recv(1024).decode("utf-8"))
        t = clock()
        self.__connection.send(str(length).encode())
        self.data = self.__connection.recv(2048).decode("utf-8")
        if len(self.data) == length:
            answer = True
        else:
            answer = False

        self.__connection.send(str(answer).encode())
        self.__connection.send(str(clock() - t).encode())

    def send_data(self, data: str) -> bool:
        if len(data) < 1:
            data = "Nothing"
        try:
            length = len(data)
            self.__connection.send(str(length).encode())
            assert (int(self.__connection.recv(1024).decode("utf-8")) == length), "error with sending length"
            self.__connection.send(data.encode())
            assert (self.__connection.recv(1024).decode("utf-8") == "True"), "Problem with answer from server"
            t = self.__connection.recv(1024).decode("utf-8")
            print("Data transfer complete in {}".format(t))
            return True
        except AssertionError as e:
            print(e)
            return False

    def disconnect(self):
        self.__connection.close()


"""
folder_names = ["bin", "boot", "dev", "etc", "home", "lib", "mnt", "opt", "root", "sbin", "tmp",
                "usr", "var"]

folder2_names = ["bin", "games", "include", "lib", "local", "sbin", "share", "src"]

g = Group("root")
main = structures.Directory("", ["rwx", "rwx", "rwx"], None, "root", g)
folders = [structures.Directory(name, ["rwx", "rwx", "rwx"], main, "root", g) for name in folder_names]

for folder in folders:
    main.add(folder)

users_group = Group("users_group")
user = User("user", users_group, main)
user.run()
"""