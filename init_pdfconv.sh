#!/bin/bash

source ~/.bashrc
pdfconv_script=$(wslpath -au $1)
pdf_path=$(wslpath -au $2)
dest_folder=$(wslpath -au $3)
uuid=$4
parent=$5
DISPLAY=$(awk '/nameserver / {print $2; exit}' /etc/resolv.conf 2>/dev/null):0
export DISPLAY=$(awk '/nameserver / {print $2; exit}' /etc/resolv.conf 2>/dev/null):0

echo "pdf_path= $pdf_path"
echo "pdfconf_script = $pdfconv_script"
echo "dest-folder = $dest_folder"
echo "uuid = $uuid"
echo "parent = $parent"

python3 $pdfconv_script $pdf_path --dest-folder $dest_folder --uuid $uuid --parent $parent --upload False

