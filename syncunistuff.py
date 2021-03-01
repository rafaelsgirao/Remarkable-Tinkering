import sys
sys.path.insert(0, "./remarkable_layers/")

import json
import os
import hashlib
from pathlib import Path
from rmtklib import *
from tempfile import mkdtemp

class UniDirs:

    def __init__(self):
        self.dirs = {}
        self.root_dir = "52d4f6fb-46f7-4f30-a83c-edf74828f994"
        self.temp_dir = mkdtemp()
        print(self.temp_dir)
         
    def load(self):
        if not os.path.exists("dirs.json"):
            raise ValueError("dirs.json does not exist - use the dump method first!")

        with open("dirs.json", "r+", encoding="utf-8") as f:
            cfg = json.load(f)
            self.dirs = cfg["dirs"]
            self.root_dir = cfg["root_dir"]

    def dump(self):
        temp_cfg = {
            "dirs":self.dirs,
            "root_dir":self.root_dir

        }
        with open("dirs.json", "w+", encoding="utf-8") as f:
            f.seek(0)
            f.truncate()
            json.dump(temp_cfg, f, indent=4, ensure_ascii=False)

        print("Dumped to file 'dirs.json'")

    def add_dir(self, name, path, parent=None, uuid=None, convert=False):

        if not parent:
            parent=self.root_dir
        if not uuid:
            uuid = make_uuid()
            
        temp_dict = {
            "path": path,
            "parent": parent,
            "uuid": uuid,
            "convert": convert,
            "files": {}   
        }

        if name in self.dirs:
            raise ValueError("Folder with that name already exists")
        self.dirs[name] = temp_dict

    def rem_dir(self, name, convert=False):
        if not name in self.dirs:
            raise ValueError("Folder does not exist in memory")
        del self.dirs[name]


    def add_file(self, fname, parent_name, uuid=None):
        if not uuid:
            uuid = make_uuid()

        temp_dict = {   
            "md5":"",
            "parent":parent_name,
            "uuid":uuid,
        }
        
        if parent_name in self.dirs:
            if fname in self.dirs[parent_name]["files"]:
                raise ValueError("File already exists")
            self.dirs[parent_name]["files"][fname] = temp_dict

    def file_exists(self, fname, parent_name):
        """"Returns 'convert' or 'normal' if file exists in store, depending on where parent is at
        False if file doesn't exist
"""
        return parent_name in self.dirs and fname in self.dirs[parent_name]["files"]

    
    def compare_hashes(self, fname, parent_name, md5):
        """Returns true if stored hash equals input hash, False otherwise.
        
        Raises ValueError if Parent or File do not exist.
"""
        if self.file_exists(fname, parent_name):
            return self.dirs[parent_name]["files"][fname]["md5"] == md5
        else:
            raise ValueError("File or parent do not exist")

    def update_file(self, fname, parent_name, md5):
        if self.file_exists(fname, parent_name):
            self.dirs[parent_name]["files"][fname][md5] = md5
        else:
            raise ValueError("File or parent do not exist")
    
    def init_files(self):
        #Normal PDF Directories
        for fldr in self.dirs:
            #make directory just in case
            temp_fldr = RMFolder(fldr.upper(), self.temp_dir, self.dirs[fldr]["uuid"], self.dirs[fldr]["parent"])
            temp_fldr.dump()

            fldr_path = self.dirs[fldr]["path"]
            for file in os.listdir(fldr_path):
                if file.endswith(".pdf"):
                    f_path = os.path.join(fldr_path, file)
                    f_hash = md5(f_path)
                    if not self.file_exists(file, fldr):
                        print(f"Processing new file '{file}'' from '{fldr}'")
                        self.add_file(file, fldr)
                    elif not self.compare_hashes(file, fldr, f_hash):
                        print(f"Processing changed file '{file}'' from '{fldr}'")
                    temp_pdf = PDFDocument(
                        f_path, 
                        self.temp_dir,
                        parent=self.dirs[fldr]["uuid"], 
                        uuid=self.dirs[fldr]["files"][file]["uuid"])
                    temp_pdf.make_all()

def main():
    return

if __name__ == "__main__":
    main()

asd = UniDirs()
asd.load()