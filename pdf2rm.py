from PyPDF2 import PdfFileReader
import sys
import uuid
import tempfile
import os

BASE_PATH = "/root/.local/share/remarkable/xochitl"
#Based on these instructions: https://www.ucl.ac.uk/~ucecesf/remarkable/#org8c08493

# Load the pdf to the PdfFileReader object with default settings
def get_nr_of_pages(file):
    with open(file, "rb") as pdf_file:
        pdf_reader = PdfFileReader(pdf_file)
        print(f"The total number of pages in the pdf document is {pdf_reader.numPages}")
        return pdf_reader.numPages

def make_uuid():
    return str(uuid.uuid4())

def gen_files(uuid):
    tempdir = tempfile.tempdir.mkdtemp()
    files = (".cache", ".highlights", ".textconversion", ".thumbnails")
    for ext in files:
        os.mknod