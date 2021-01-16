#!/bin/bash

source ~/.bashrc
pdf_path=$(wslpath -au $2)
pdfconv_script=$(wslpath -au $1)
echo "pdf_path= $pdf_path"
echo "pdfconf_script = $pdfconv_script"

python3 $pdfconv_script $pdf_path --upload False

