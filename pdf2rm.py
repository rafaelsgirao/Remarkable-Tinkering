from PyPDF2 import PdfFileReader
import sys
from uuid import uuid4
import tempfile
import os
import time
from shutil import rmtree
BASE_PATH = "/root/.local/share/remarkable/xochitl"


#Based on these instructions: https://www.ucl.ac.uk/~ucecesf/remarkable/#org8c08493

# Load the pdf to the PdfFileReader object with default settings
def get_nr_of_pages(file):
    with open(file, "rb") as pdf_file:
        pdf_reader = PdfFileReader(pdf_file)
        print(f"The total number of pages in the pdf document is {pdf_reader.numPages}")
        return pdf_reader.numPages


def make_uuid():
    return str(uuid4())


def get_time():
    #In epoch, in milliseconds, for whatever reason
    return int(round(time.time() * 1000))


def init_files(uuid, filename, page_count):
    tempdir = tempfile.mkdtemp()

    #This is wrong
    #files = (".cache", ".highlights", ".textconversion", ".thumbnails")
    #for ext in files:
        #fullpath = os.path.join(tempdir, uuid + ext)
        
    metadata = """{{    
    "deleted": false,
    "lastModified": "{epoch_time}",
    "lastOpenedPage": 1,
    "metadatamodified": true,
    "modified": false,
    "parent": "ebe93f67-5d7e-4e47-b29a-6b75aff60efb",
    "pinned": false,
    "synced": false,
    "type": "DocumentType",
    "version": 1,
    "visibleName": "{file_name}"
}}
"""
    content = """{{
    "extraMetadata": {{}},
    "filetype": "pdf",
    "fontname": "",
    "lastOpenedPage": 0,
    "lineHeight": -1,
    "margins": 100,
    "orientation": "portrait",
    "pageCount": {page_count},
    "pages": {pages},
    "textScale": 1,
    "transform": {{
        "m11": 1,
        "m12": 0,
        "m13": 0,
        "m21": 0,
        "m22": 1,
        "m23": 0,
        "m31": 0,
        "m32": 0,
        "m33": 1
    }}
}}
"""
    #Write (uuid).metadata
    content_path = os.path.join(tempdir, uuid + ".metadata")
    f = open(content_path, "w+")
    f.seek(0)
    f.write(metadata.format(epoch_time=get_time(), file_name=filename))
    f.close()

    #Write (uuid).content
    content_path = os.path.join(tempdir, uuid + ".content")

    #Create random uuids for pages
    pages = "[\n"
    for _ in range(0, page_count):
        pages = pages + " " * 8 + '"' + make_uuid() + '",\n'
    pages = pages[:-2] + "\n    " + "]"
     
    f = open(content_path, "w+")
    f.seek(0)
    content = content.format(page_count=page_count, pages=pages)
    f.write(content)
    f.close()

    #Write (uuid).pagedata
    content_path = os.path.join(tempdir, uuid + ".pagedata")

    with open(content_path, "w+") as f:
        f.seek(0)
        for i in range(0, page_count):
            f.write("Blank\n")



#For future reference, this is the content from the site linked at the top
#Edit: not actually deprecated (they're pretty much the same), I was just sleepy
metadata_deprecated = """{{
    "extraMetadata": {{
    }},
    "fileType": "pdf",
    "fontName": "",
    "lastOpenedPage": 0,
    "lineHeight": -1,
    "margins": 100,
    "orientation": "portrait",
    "pageCount":' ${n}',
"""