import json
import os

class FileJson:
    def __init__(self, filename: str, base_file):
        self.filename = filename
        self.base_file = base_file

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                return json.load(f)
        else:
            with open(self.filename, "w") as f:
                if self.base_file != None:
                    json.dump(self.base_file, f, indent=4)
                return self.base_file

    def save(self, data):
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=4)

class File:
    def __init__(self, filename: str):
        self.filename = filename

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                return f.readlines()
        else:
            with open(self.filename, "w") as f:
                return ""

    def save(self, txt):
        with open(self.filename, "w") as f:
            f.write(txt)