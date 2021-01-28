#Python module with useful libraries
import time
from uuid import uuid4
from PyPDF2 import PdfFileReader
import sys
import tempfile
import os
from shutil import rmtree, copyfile
#import zipfile

#Based on these awesome instructions: https://www.ucl.ac.uk/~ucecesf/remarkable/#org8c08493

BASE_PATH = "/root/.local/share/remarkable/xochitl"
PDFCONV_PATH = "D:\\remarkable\\remarkable-layers\\pdf_converter.py"

#Zip functions adapted from #https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory-in-python

class PDFDocument:
    """class that takes in a path to a PDF file and a directory, and generates the files needed 
    to make it a PDF readable by the tablet (uploaded by e.g SFTP)

    (In syncunistuff.py , the folder passed is always a folder created with the tempfile module)
    
    This also takes in an optional parent argument (uuid of folder) - if left empty PDF will appear
     in the tablet's root folder
"""

    def __init__(self, file, folder, parent=""):
        self.filepath = file
        self.parent = parent
        self.filename = os.path.basename(file)
        self.uuid = make_uuid()
        self.folder = folder 
        self.page_count = self.get_pagecount()

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
        with open(os.path.join("templates", "template.metadata"), "r") as template_file:
            template = template_file.read()
        file_path = os.path.join(self.folder, self.uuid + ".metadata")
        with open(file_path, "w+") as f:
            f.write(template.format(epoch_time=get_time(), file_name=self.filename, parent_folder=self.parent))

    def make_content(self):
        with open(os.path.join("templates", "pdf-template.content"), "r") as template_file:
            template = template_file.read()

        #Generate a json list with a random uuid for each PDF page
        pages = "[\n"
        for _ in range(0, self.page_count):
            pages = pages + " " * 8 + '"' + make_uuid() + '",\n'
        pages = pages[:-2] + "\n    " + "]"

        file_path = os.path.join(self.folder, self.uuid + ".content")
        with open(file_path, "w+") as f:
            f.write(template.format(page_count=self.page_count, pages=pages))
    def copy_pdf(self):
        copyfile(self.filepath, os.path.join(self.folder, self.uuid + ".pdf"))
    
    #Function that triggers all other functions in one call
    def make_all(self):
        self.make_content()
        self.copy_pdf()
        self.make_pagedata()
        self.make_metadata()

def get_time():
    #In epoch, in milliseconds, for whatever reason
    return int(round(time.time() * 1000))

def make_uuid():
    return str(uuid4())



#Class to handle PDFs that are to be converted by remarkable-layers' pdf_converter.py
#Fortunately that script generates all the necessary files for us
class ConvertedDocument:
    def __init__(self):
        return

#Might remove later
#def zipdir(path, zipfpath):
    # zipfpath = path to zip file
#    zipf = zipfile.ZipFile(zipfpath, "w", zipfile.ZIP_DEFLATED)
#    for root, _, files in os.walk(path):
#        for file in files:
#            if not file.endswith(".zip"):
#                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))
#    zipf.close()
#    return zipfpath



# Load the pdf to the PdfFileReader object with default settings



#def init_files(uuid, pdf_path, page_count):
#    tempdir = tempfile.mkdtemp()
#    return tempdir

#def main():
    #pdf_path = sys.argv[1]
    #uuid = make_uuid()  
    #tempdir = init_files(uuid, pdf_path, get_nr_of_pages(pdf_path))

    #zipf = zipdir(tempdir, os.path.join(tempdir, uuid + ".zip"))
    #print(tempdir)
    #print(zipf)

#if __name__ == "__main__":
#    main()

