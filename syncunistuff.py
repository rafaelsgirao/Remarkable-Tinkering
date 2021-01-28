import json
import os
import hashlib
from pathlib import Path
from pdf2rm import make_uuid
from tempfile import mkdtemp

TEMP_DIR = mkdtemp()


def load_dirs():
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

#From https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def init_file_db(dirs_conf):
    file_list = []
    with open("files.json", "w+", encoding="utf-8") as f:
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
            
def process_files():
    #Process normal PDF folders first

def main():
    return

if __name__ == "__main__":
    main()