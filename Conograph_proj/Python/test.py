import os
import shutil

workSpace = '../PeakSearch'
for fname in os.listdir (workSpace):
    print (fname)
    if 'PeakSearch.exe' in fname: continue
            
    path = os.path.join (workSpace, fname)
        
    if os.path.isdir (path):
        shutil.rmtree (path)
    else:
        os.remove (path)

