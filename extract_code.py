# importing required modules
from zipfile import ZipFile
import os, glob
  
# specifying the zip file name
file_name = "/out/code.zip"
path="/usr/src/app"
pattern="*.py"



# opening the zip file in READ mode
with ZipFile(file_name, 'w') as zip:
    for file in glob.glob(os.path.join(path, pattern)):
        print(file) 
        zip.write(file)
    print('All files zipped successfully!')      
