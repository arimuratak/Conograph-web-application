import os
import shutil
import numpy as np
import streamlit as st
from messages import messages as mess
from dataIO import read_cntl_inp_xml, read_inp_xml,\
                    show_graph, change_inp_xml
from data import PeakSearchProcess

class PeakSearchMenu:
    def __init__ (self, lang):
        self.workSpace = '../PeakSearch'
        
        self.lang = lang
        self.folder = None
        self.mess = mess[lang]['peaksearch']
        self.param_path = None
        self.hist_path = None
        self.out_path = None
        self.params = None
        self.objPeakSearch = None
        self.path_cntl_inp = None
        self.path_param = None
        
        self.cntl_work_path = None
        self.param_work_path = None
        self.hist_work_path = None
        self.out_work_path = None

    def setObjPeakSearch (self, folder):
        
        self.folder = folder
        self.path_cntl_inp = os.path.join (folder, 'cntl.inp.xml')
        param_path, hist_path, out_path \
            = read_cntl_inp_xml (self.path_cntl_inp)

        self.param_path = os.path.join (folder, param_path)
        self.hist_path = os.path.join (folder, hist_path)
        self.out_path = os.path.join (folder, out_path)
        self.out_work_path = os.path.join (self.workSpace, out_path)
        self.params = read_inp_xml (self.param_path)
        #print (self.params)
        self.move2workSpace (out_path)
        self.objPeakSearch = PeakSearchProcess (self.lang)
        #print (self.params)

    def reset_workspace (self,):
        for fname in os.listdir (self.workSpace):
            if 'PeakSearch.exe' in fname: continue

            path = os.path.join (self.workSpace, fname)
        
            if os.path.isdir (path):
                shutil.rmtree (path)
            else:
                os.remove (path)

    def move2workSpace (self, out_path):
        self.reset_workspace ()
        self.cntl_work_path = self.to_workspace (self.path_cntl_inp)
        self.param_work_path = self.to_workspace (self.param_path)
        self.hist_work_path = self.to_workspace (self.hist_path)
        self.out_work_path = os.path.join (self.workSpace, out_path)

    def to_workspace (self, src):
        dst = os.path.basename (src)
        dst = os.path.join (self.workSpace, dst)
        shutil.copyfile (src, dst)
        return dst

    def smthParams (self,):
        col1,col2 = st.columns (2)
        nPointsDefault = self.params[0]['NumberOfPoints'][0]
        endRegionDefault = self.params[0]['EndOfRegion'][0] 
        with col1:
            nPoints = st.text_input (
                self.mess['tbl_col1'],
                nPointsDefault)
        with col2:
            endRegion = st.text_input (
                self.mess['tbl_col2'],
                endRegionDefault)
            
        return (nPoints, endRegion)
    
    def rangeParam (self,):
        col1,col2 = st.columns (2)
        rangeMin, rangeMax = self.params[1]
        if rangeMin == 'MIN': rangeMin = 0.0
        with col1:
            minRange = st.text_input ('min', rangeMin)
        with col2:
            maxRange = st.text_input ('max', rangeMax)

        return minRange, maxRange
    
    def thresholdParam (self,):
        col1, col2 = st.columns ([2,8])
        c_def, use_error_flg = self.params[2]
        useErrDict = {
            1 : self.mess['th_sel_1'],
            0 : self.mess['th_sel_2']}
        use_error_def = useErrDict [use_error_flg]
        
        with col1:
            c_fixed = st.text_input ('c : ', c_def)
        
        with col2:
            use_error = st.selectbox (
                {'eng' : 'select','jpn' : '選択'}[self.lang],
                options = list (useErrDict.values()))

        return c_fixed, use_error

    def kalpha2Select (self,):
        yes = self.mess['exec_sel_1']
        no = self.mess['exec_sel_2']
        select = st.radio (self.mess['delpk_mes'],
                           [yes, no], horizontal = True)
        return select

    def kaplha2Param (self,):
        mat = np.array ([
            [0.5594075, 0.563798],
            [0.709300, 0.713590],
            [1.540562, 1.544398],
            [1.788965, 1.792850],
            [1.936042, 1.939980],
            [2.289700, 2.293606]])
        kalpha1, kalpha2 = self.params[-1]
        kalphas = np.array ([[kalpha1, kalpha2]])
        dist = np.sqrt (np.power (mat - kalphas, 2).sum(axis = 1))
        idx = np.argmin (dist)

        params = [
            'Ag / 0.5594075 / 0.563798',
            'Mo / 0.709300 / 0.713590',
            'Cu / 1.540562 / 1.544398',
            'Co / 1.788965 / 1.792850',
            'Fe / 1.936042 / 1.939980',
            'Cr / 2.289700 / 2.293606']
        
        sel = st.selectbox (
            self.mess['wavelen_mes'],
            params, index = int (idx))
        
        kalpha1, kalpha2 = sel.split (' / ')[1:]
        #st.write (kalpha1, kalpha2)
        return kalpha1, kalpha2

    def search_folder_cntl (self, folder = '../sample'):
        folders = []
        for dir, _, fnames in os.walk (folder):
            if 'cntl.inp.xml' in fnames:
                folders.append (dir)
        return folders

    def peaksearch (self,):
        self.objPeakSearch.exec_peak_search ()
        df, peakDf = self.objPeakSearch.put_result ()
        return df, peakDf

    def operationParam (self, params, savePath):
        #nPoins = params['nPoints']; endRegion = params['endRegion']
        minRange = params['minRange'] #; maxRange = params['maxRange']
        #c_fixed = params['c_fixed'];
        useErr = params['useErr']
        select = params['select']
        kalpha1 = params['kalpha1']; kalpha2 = params['kalpha2']
        if str (minRange) == '0.0': params['minRange'] = 'MIN'
        params['useErr'] = int (useErr == self.mess['th_sel_1'])
        params['select'] = int (select == self.mess['exec_sel_1'])
        if (kalpha1 == None) | (kalpha2 == None):
            params['kalpha1'], params['kalpha2'] = self.params[-1]

        change_inp_xml (params, savePath)

    def readDefaultParam (self,):
        params = read_inp_xml (self.param_path)
        text = ''
        smoothing_params = params[0]
        nPoints = smoothing_params['NumberOfPoints'][0]
        endRegion = smoothing_params['EndOfRegion'][0]
        range_begin, range_end = params[1]
        threshold, useErr = params[2]
        alpha2_correction = params[3]
        kalpha1, kalpha2 = params[4]

        text += {'eng':'Smoothing / ', 'jpn' : '平滑化 / '}[self.lang]
        text += self.mess['tbl_col1'] + ' : {}, '.format (nPoints)
        text += self.mess['tbl_col2'] + ' : {}  \n'.format (endRegion)

        text += self.mess['area_mes'] + ' / '
        text += 'min : {}, max : {}  \n'.format (range_begin, range_end)
        text += {'eng':'threshold', 'jpn' : 'しきい値'}[self.lang] + ' / '
        text += 'c : {}, '.format (threshold)
        text += {0 : self.mess['th_sel_2'],
                 1 : self.mess['th_sel_1']
                 }[int (useErr)] + '  \n'

        text += self.mess['delpk_mes'] + ' / '
        text += {0 : self.mess['exec_sel_2'],
                 1 : self.mess['exec_sel_1']
                 }[int (alpha2_correction)] + '  \n'
        
        text += 'kα1 : {}, kα2 : {}'.format (kalpha1, kalpha2)
        return text

    def updateParamFile (self, ans):
        saveParam = st.button (
            {'eng' : 'Save parameters',
             'jpn':'パラメータ保存'}[self.lang])
        if saveParam:
            change_inp_xml (ans, self.param_path)

    def menu (self,):
        #st.write (self.mess['param'])
        ans = {k : None for k in [
            'defaultParam', 'df', 'peakDf', 'nPoints', 'endRegion',
            'minRange, maxRange, c_fixed', 'useErr','select',
            'kalpha1', 'kalpha2', 'folder']}
        base_folder = st.text_input (
            {'eng' : 'Sample folder name',
            'jpn' : 'サンプルフォルダ'}[lang],
            '../sample')

        folders = self.search_folder_cntl (base_folder)
        folder = st.selectbox (
            {'eng' : 'select', 'jpn' : '選択'}[lang],
            folders,
            accept_new_options = False,
            placeholder = {'eng' : 'pls. select',
                           'jpn':"選択してください"}[lang])
        ans['folder'] = folder
        self.setObjPeakSearch (folder)


        dispDefaultParam = st.toggle ({
            'eng' : 'Default Parameter',
            'jpn' : 'パラメータ初期値'}[self.lang])
        if dispDefaultParam:
            text = self.readDefaultParam ()
            st.write (text)

        st.write (self.mess['smth_mes'])
        ans['nPoints'], ans['endRegion'] = self.smthParams ()

        st.write (self.mess['area_mes'])
        ans['minRange'], ans['maxRange'] = self.rangeParam()
        st.write (self.mess['th_mes'])
        ans['c_fixed'],  ans['useErr'] = self.thresholdParam()
        select = self.kalpha2Select ()
        ans['select'] = select
        
        if select == self.mess['exec_sel_1']:
            ans['kalpha1'], ans['kalpha2'] = self.kaplha2Param ()

        self.operationParam (ans, self.param_work_path)
        ans['df'], ans['peakDf'] = self.peaksearch ()

        self.updateParamFile (ans)

        return ans

class IndexingMenu:
    def __init__(self,lang):
        self.mess = mess[lang]

    def menu (self,):
        mes_idx = self.mess['indexing']
        st.write (mes_idx['main'])

if __name__ == '__main__':
    with st.sidebar:
        title = st.empty()
        lang_sel = st.radio ('langage', ['English', 'Japanese'],
                             horizontal = True)
        if lang_sel == 'English': lang = 'eng'
        else: lang = 'jpn'

        with title:
            st.title (mess[lang]['main_title'])
    
        select_menu = st.radio ('menu',
                [mess[lang]['peaksearch']['main'],
                 mess[lang]['indexing']['main']],
                horizontal = True)
    
        objPeakSearch = PeakSearchMenu (lang)
        objIndexing = IndexingMenu (lang)

        if select_menu == mess[lang]['peaksearch']['main']:
            out_pk_menu = objPeakSearch.menu()
        else:
            objIndexing.menu()

    #----------------------------------------------------
    #   グラフ表示、ピークサーチ結果表示
    #----------------------------------------------------
    df, peakDf = out_pk_menu['df'], out_pk_menu['peakDf']
  
    mes = mess[lang]['graph']
    df.columns = [ 'xphase', 'yphase', 'err_yphase', 'smth_yphase']

    sel_graph = st.radio (
            {'eng' : 'select graph or log',
            'jpn' : 'グラフ・ログ選択'}[lang],
            [mes['diffPattern'], mes['log']],
                      horizontal = True)
    graph_area = st.empty()


    dispDf = peakDf
    dispDf.columns = [{'eng' : 'Peak', 'jpn' : 'ピーク'}[lang],
                 mes['pos'], mes['peakH'], mes['fwhm'], mes['sel']]


    st.write (mess[lang]['graph']['result'])
    edited_df = st.data_editor (
        dispDf,
        column_config = {
            mes['sel']: st.column_config.CheckboxColumn(
                            mes['sel'], default = True)},
            use_container_width = True)
    selected = edited_df.loc[edited_df[mes['sel']] == True]
    selected.columns = peakDf.columns

    if select_menu == mess[lang]['peaksearch']['main']:
        with graph_area:
            if sel_graph == mes['diffPattern']:
                fig = show_graph (df, selected, output = True, lang = lang)
                st.plotly_chart (fig, use_container_width = True)
            else:
                path = '../PeakSearch/LOG_PEAKSEARCH.txt'
                with open (path, 'r', encoding = 'utf-8') as f:
                    content = f.read()
                st.text_area ('log', content, height = 400)


