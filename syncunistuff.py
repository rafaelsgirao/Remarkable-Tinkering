import sys
sys.path.insert(0, "./remarkable_layers/")

import json
import os
import hashlib
from pathlib import Path
from rmtklib import *
from tempfile import mkdtemp

TEMP_DIR = mkdtemp()

class UniDirs:
    def __init__(self):
        self.converted_dirs = {}
        self.normal_dirs = {}
        self.root_dir = "52d4f6fb-46f7-4f30-a83c-edf74828f994"

    def load(self):
        if not os.path.exists("dirs.json"):
            raise ValueError("dirs.json does not exist - use the dump method first!")

        with open("dirs.json", "r+", encoding="utf-8") as f:
            cfg = json.load(f)
            self.converted_dirs = cfg["converted_dirs"]
            self.normal_dirs = cfg["normal_dirs"]
            self.root_dir = cfg["root_dir"]

    def add(self, name, path, parent=None, uuid=None, convert=False):
        if name in self.converted_dirs:
            raise ValueError("Folder with that name already exists")
        if not parent:
            parent=self.root_dir
        if not uuid:
            uuid = make_uuid()

        temp_dict = {
            "path":path,
            "parent":parent,
            "uuid":uuid
        }
        if convert:
            self.converted_dirs[name] = temp_dict
        else:
            self.normal_dirs[name] = temp_dict

    def dump(self):
        temp_cfg = {
            "converted_dirs":self.converted_dirs,
            "normal_dirs":self.normal_dirs,
            "root_dir":self.root_dir

        }
        with open("dirs.json", "w+", encoding="utf-8") as f:
            f.seek(0)
            f.truncate()
            json.dump(temp_cfg, f, indent=4, ensure_ascii=False)


            print("Dumped to file 'dirs.json'")
         

    def load_dirs(self):
        if not os.path.exists("dirs.json"):
            print("dirs.json does not exist - creating.")
            with open("templates\\dirs.json", "r+", encoding="utf-8") as default_cfg:
                x = default_cfg.read()
                data = json.loads(x)
                print(data)
            with open("dirs.json", "w+", encoding="utf-8") as cfg:
                json.dump(data, cfg, indent=4, ensure_ascii=False)
            return data
        else:
            with open("dirs.json", "r+", encoding="utf-8") as f:
                return json.load(f)

def init_file_db(dirs_conf):
    file_list = []
    for folder in dirs_conf["converted_pdf_folders"]:
        folder_path = folder["path"]
        folder_name = folder["name"]
        if folder_path == "None":
            continue
        for file in os.listdir(folder_path):
            #Pdf converter only supports .pdfs
            #Note: os.listdir returns both folders and files
            #So if you have a folder that ends in .pdf
            #this will fail (and you're a pretty evil person)
            if file.endswith(".pdf"):
                newfile = {"fname": file, "md5":"", \
                    "parent": folder_name, "uuid": make_uuid()}
            #Check if file extension is supported file
                file_list.append(newfile)
    with open("files.json", "w+", encoding="utf-8") as files_cfg:
        json.dump(file_list, files_cfg, ensure_ascii=False, indent=4)
    return file_list
            
def process_files(file_list):
    return
    #Process normal PDF folders first

def main():
    return

if __name__ == "__main__":
    main()