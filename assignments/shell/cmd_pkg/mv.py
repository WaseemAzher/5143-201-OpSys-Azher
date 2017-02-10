
#!/usr/bin/env python
import shutil
import os.path
import os
import sys

def mv(self,src,dest):
        if os.path.isfile(src):
        #checks whether source file exists or not
            if os.path.isfile(dest): #checks whether destination file exists or not.       
                shutil.copyfile('src','dest')#if both files exists then copies source to destination file.
            else:
                print("destination file not found")
        else:
            print("source file not found")