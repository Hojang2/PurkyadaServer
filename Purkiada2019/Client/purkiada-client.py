from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, gethostname
from json import dumps
# -*- encoding: utf-8 -*-

manual = {
        "ls": "  Prints all files and directories in current directory",
        "help": "  Shows this help",
        "ssh": """  Secure Shell - connects you to target server 
                    usage ssh <username>@<target_ip>:<target_port>""",
        "cd": """   Change working directory 
                    usage: cd <target>  parametrs: 
                        cd /            - moves you to root directory
                        cd ..            - moves you to directory above 
                        cd <target_directory>    - moves you to target directory
                    errors:  DirectoryDoesNotExist - target directory doesn't exist""",
        "rename": """ change name of file or directory
            usage: rename <input_file.txt> <output_file.txt>""",
        "su": " Change your user to root",
        "exit": """ If you are connected to server you will be disconnect,
                else close the application""",
        "read": "   Read the content of the file"
}


class Client:

    def __init__(self, commands):
        self.commands = commands
        self.connected = False
        self.port = 0
        self.starter = "{}@{}:{}$"
        self.args = []
        self.action = ""
        self.__password = ""
        self.sock = None

        # Setting default values
        self.default_path = "/home/guest"
        self.path = self.default_path
        self.default_address = gethostbyname(gethostname())
        self.address = self.default_address
        self.default_name = "guest"
        self.name = self.default_name

    def sock_init(self):

        self.sock = socket(AF_INET, SOCK_STREAM)
        return True

    def run(self):
        while True:

            self.action = input(self.starter.format(self.name, self.address, self.path))
            self.action, *self.args = self.action.split(" ")

            if self.action in self.commands.keys():
                if self.connected:
                    self.run_connected()
                else:
                    self.run_local()
            else:
                print("Command not found")

    def connect(self):
        if self.sock_init():
            # Syntax of ssh will be 'ssh username@address:port
            tmp = self.args[0].split("@")
            self.name = tmp[0]
            tmp = tmp[1]
            self.address, self.port = tmp.split(":")

            try:
                self.sock.connect((self.address, self.port))
                self.connected = True
                print("new connection with {} on port: {}".format(self.address,
                                                                  self.port))
            except:

                print("Target {}:{} address and port doesn't exists")

            self.run_connected()

        else:
            print("Problem with socket initialization")

    def validate(self):
        self.__password = input("password: ")
        self.sock.send(self.validate_data(dumps({"name": self.name, "password": self.__password}).decode()))
        answer = self.sock.recv(1024).decode("utf8")
        if answer == "True":
            self.connected = True
            self.path = self.sock.recv(1024).decode("utf8")
        else:
            print("Invalid username or password")

    def run_local(self):
        if self.action == "ssh":
            self.connect()

        if self.action == "exit":
            exit()

    def show_help(self):
        for key in self.commands:
            print(key + "\t - " + self.commands[key])

    def help_command(self, command):
        print(command + "\t - " + self.commands[command])

    def run_connected(self):

        if self.action == "ssh":

            print(self.sock.recv(4024).decode("utf8"))

            for _ in range(1):
                self.validate()

        elif self.action == "help":
            self.show_help()

        elif self.action == "exit":
            self.path = self.default_path
            self.name = self.default_name
            self.address = self.default_address
            self.connected = False
            self.sock.send(self.validate_data("disconnect"))
            self.sock.close()

        else:
            self.validate_data(self.action)
            self.validate_data(dumps(self.args))

    def validate_data(self, data: str) -> bool:

        try:
            length = len(self.action)
            self.sock.send(str(length).encode())
            assert (self.sock.recv().decode("utf-8") == length), "error with sending length"
            self.sock.send(data.encode())
            assert (self.sock.recv().decode("utf-8") == "True"), "Problem with answer from server"
            time = self.sock.recv().decode("utf-8")
            print("Data transfer complete in {}".format(time))
            return True
        except AssertionError as e:
            print(e)
            return False