#Python module with useful libraries
import time
from uuid import uuid4
from PyPDF2 import PdfFileReader
import sys
import tempfile
import os
from shutil import rmtree
import hashlib
import zipfile
import remarkable_layers.pdf_converter as pdfconv
import remarkable_layers.rmlines as rmlines
from pathlib import Path
import json

import logging

#nOTE TO FUTURE SELF: don't forget to  export PYTHONPATH="$PWD/remarkable_layers/"

logger = logging.getLogger(__name__)

#Based on these awesome instructions: https://www.ucl.ac.uk/~ucecesf/remarkable/#org8c08493

BASE_PATH = "/root/.local/share/remarkable/xochitl"

#Zip functions adapted from #https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory-in-python

class PDFDocument:
    """class that takes in a path to a PDF file and a directory, and generates the files needed 
    to make it a PDF readable by the tablet (uploaded by e.g SFTP)

    (In syncunistuff.py , the folder passed is always a folder created with the tempfile module)
    
    This also takes in an optional parent argument (uuid of folder) - if left empty PDF will appear
    in the tablet's root folder
"""

    def __init__(self, file, folder, parent="None", convert=False, uuid=None):
        self.filepath = file
        self.parent = parent
        self.filename = os.path.basename(file)
        if uuid:
            self.uuid = uuid
        else:
            self.uuid = make_uuid()
        self.folder = folder 
        self.page_count = self.get_pagecount()
        self.parent = parent
        self.convert = convert
        
    def get_pagecount(self):
        with open(self.filepath, "rb") as pdf_file:
            pdf_reader = PdfFileReader(pdf_file)
            #print(f"The total number of pages in the pdf document is {pdf_reader.numPages}")
            return pdf_reader.numPages

    def make_pagedata(self):
        file_path = os.path.join(self.folder, self.uuid + ".pagedata")
        with open(file_path, "w+") as f:
            f.seek(0)
            for _ in range(0, self.page_count):
                f.write("Blank\n")
                
    def make_metadata(self): 
        metadata = {
            "deleted": False,
            "lastModified": get_time(),
            "lastOpenedPage": 1,
            "metadatamodified": True,
            "modified": False,
            "parent": self.parent,
            "pinned": False,
            "synced": False,
            "type": "DocumentType",
            "version": 1,
            "visibleName": self.filename
        }
 #       with open(os.path.join("templates", "template.metadata"), "r") as template_file:
 #           template = template_file.read()
        file_path = os.path.join(self.folder, self.uuid + ".metadata")
        with open(file_path, "w+") as f:
            #f.write(template.format(epoch_time=get_time(), file_name=self.filename, parent_folder=self.parent))
            json.dump(metadata, f, indent=4, ensure_ascii=False)

    def make_content(self):
        pdf_content = {
            "extraMetadata": {},
            "filetype": "pdf",
            "fontname": "",
            "lastOpenedPage": 0,
            "lineHeight": -1,
            "margins": 100,
            "orientation": "portrait",
            "pageCount": self.page_count,
            "pages": {},
            "textScale": 1,
            "transform": {
                "m11": 1,
                "m12": 0,
                "m13": 0,
                "m21": 0,
                "m22": 1,
                "m23": 0,
                "m31": 0,
                "m32": 0,
                "m33": 1
            }
        }
        #with open(os.path.join("templates", "pdf-template.content"), "r") as template_file:
        #    template = template_file.read()

        #Generate a json list with a random uuid for each PDF page
        pages = "[\n"
        for _ in range(0, self.page_count):
            pages = pages + " " * 8 + '"' + make_uuid() + '",\n'
        pages = pages[:-2] + "\n    " + "]"

        pdf_content["pages"] = pages
        file_path = os.path.join(self.folder, self.uuid + ".content")
        with open(file_path, "w+") as f:
            #f.write(template.format(page_count=self.page_count, pages=pages))
            json.dump(pdf_content, f, indent=4, ensure_ascii=False)


    def copy_pdf(self):
        os.symlink(self.filepath, os.path.join(self.folder, self.uuid + ".pdf"))
    #def copy_pdf(self):
    #    copyfile(self.filepath, os.path.join(self.folder, self.uuid + ".pdf"))
    

    #Function that triggers all other functions in one call
    def make_all(self):
        if self.convert:
            self.convert_pdf()
        else:
            self.make_content()
            self.copy_pdf()
            self.make_pagedata()
            self.make_metadata()
        print("done")
    
    #This works! (after a lot of hacky edits to the converter script and rmapy :|)
    #Edit: nope, rewrite time
    def convert_pdf(self):
        pdf_input = Path(self.filepath)
        svg_out_dir = Path(
            os.path.join(os.path.dirname(self.filepath), ".pdf_converter",
                os.path.basename(self.filepath))
        ).with_suffix("")
        svg_out_dir.mkdir(parents=True, exist_ok=True)

        for pn in range(1, self.page_count + 1):
            pdfconv.extract_svg_page(
                orig_pdf=self.filepath,
                page_no=pn,
                out_dir=svg_out_dir,
                overwrite=False,
            )
        pdfconv.generate_rmlines_and_upload(svg_out_dir, os.path.join(self.folder, self.uuid + ".zip"), exclude_grid_layers=False)

    def unpack_converted_pdf(self):
        return
        #with zipfile.ZipFile((os.path.join(folder, uuid + ".zip")) as f:
        #    if not zipfile.is_zipfile(f):
        #        raise ValueError("I don't know what error to raise, but this is not a valid ZIP file!")
    


class RMFolder:
    def __init__(self, name, folder, uuid=None, parent=None):

        if uuid:
            self.uuid = uuid
        else:
            self.uuid = make_uuid()
        if parent:
            self.parent = parent
        else:
            self.parent = ""

        self.name = name
        self.folder = folder
        
        self.template = {
            "deleted": False,
            "lastModified": get_time(),
            "metadatamodified": False,
            "modified": False,
            "parent": self.parent,
            "pinned": False,
            "synced": False,
            "type": "CollectionType",
            "version": 2,
            "visibleName": name
        }

    def dump(self):
        file_path = os.path.join(self.folder, self.uuid + ".metadata")
        with open(file_path, "w+") as f:
            json.dump(self.template, f, indent=4, ensure_ascii=False)

#Class to handle PDFs that are to be converted by remarkable-layers' pdf_converter.py
#Fortunately that script generates all the necessary files for us
class ConvertedDocument:
    def __init__(self):
        return
        
def get_time():
    #In epoch, in milliseconds, for whatever reason
    return int(round(time.time() * 1000))

def make_uuid():
    return str(uuid4())

#From https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()



#    tempdir = tempfile.mkdtemp(


