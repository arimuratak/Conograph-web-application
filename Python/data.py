import os
import shutil
import subprocess
from dataIO import read_cntl_inp_xml, read_inp_xml,\
                    read_output_file, show_graph, change_inp_xml

class PeakSearchProcess:
    def __init__ (self, lang, folder = '../PeakSearch'):
        self.folder = folder
        self.lang = lang
        self.param_file = None
        self.histogram_file = None
        self.output_file = None
        self.exe_path = '../PeakSearch/PeakSearch.exe'

        self.params = None
        self.read_cntl ()

    def read_cntl (self,):
        path = os.path.join (self.folder, 'cntl.inp.xml')
        print (path)
        param_file, histogram_file, output_file = read_cntl_inp_xml (path)
        self.param_file = param_file
        self.histogram_file = histogram_file
        self.output_file = output_file
        self.putOutputFolder ()
        #print ('output fuile!!!', self.output_file)

    def putOutputFolder (self,):
        outFolder = os.path.dirname (self.output_file)
        outFolder = os.path.join (self.folder, outFolder)
        os.makedirs (outFolder, exist_ok=True)

    def read_params (self,):
        path = os.path.join (self.folder, self.param_file)
        self.params = read_inp_xml (path)

    def update_params (self, params):
        path = os.path.join (self.folder, self.param_file)
        change_inp_xml (params, path)
    
    def exec_peak_search (self,):
        cwd = os.getcwd()
        #dst = os.path.join (self.folder, 'PeakSearch.exe')
        #shutil.copyfile (self.exe_path, dst)
        os.chdir (self.folder)

        result = subprocess.run ('PeakSearch.exe')
        print ('result !!!!!!!!!!!!!!!!!!!!!!',result)
        #os.remove ('PeakSearch.exe')
        os.chdir (cwd)

    def graph (self,):
        df, peakDf = self.put_result ()
        print (df.head())
        print (peakDf.head())
        path_graph = os.path.join (self.folder, 'graph.html')
        show_graph (df, peakDf, path_graph)

    def put_result (self,):
        path = os.path.join (self.folder, self.output_file)
        print (path)
        df, peakDf = read_output_file (path)
        return df, peakDf

if __name__ == '__main__':
    folder = '../sample/sample1(CharacteristicXrays)'
    
    obj = PeakSearchProcess ('jpn', '../PeakSearch')
    obj.exec_peak_search ()
    obj.graph()