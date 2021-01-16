from PyPDF2 import PdfFileReader
import sys
from uuid import uuid4
import tempfile
import os
import time
from shutil import rmtree, copyfile
import zipfile

BASE_PATH = "/root/.local/share/remarkable/xochitl"
PDFCONV_PATH = "D:\\remarkable\\remarkable-layers\\pdf_converter.py"
#Zip functions adapted from #https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory-in-python

def zipdir(path, zipfpath):
    # zipfpath = path to zip file
    zipf = zipfile.ZipFile(zipfpath, "w", zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
        for file in files:
            if not file.endswith(".zip"):
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))
    zipf.close()
    return zipfpath

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

def convert_pdf(pdf_path):
    #Static paths are bad :(
    x = os.system("/mnt/d/git/Remarkable Tinkering/init_pdfconv.sh '{}' '{}'".format(
        PDFCONV_PATH, pdf_path
    ))

def init_files(uuid, pdf_path, page_count):
    tempdir = tempfile.mkdtemp()

    filename = os.path.basename(pdf_path)
    pdf_path = copyfile(pdf_path, os.path.join(tempdir, uuid + ".pdf"))

    #Read templates
    metadata = open(os.path.join("templates", "metadata.txt"), "r").read()
    content = open(os.path.join("templates", "content.txt"), "r").read()

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
        for _ in range(0, page_count):
            f.write("Blank\n")

    return tempdir

def main():
    pdf_path = sys.argv[1]
    uuid = make_uuid()  
    tempdir = init_files(uuid, pdf_path, get_nr_of_pages(pdf_path))

    zipf = zipdir(tempdir, os.path.join(tempdir, uuid + ".zip"))
    print(tempdir)
    print(zipf)

if __name__ == "__main__":
    main()

