import sys
import os
import pandas as pd
import joblib
from data_preparation import LOCAL_DATA_ROOT


# GLOBALS
TYPE = sys.argv[1]
PRE_PATH = LOCAL_DATA_ROOT + 'preprocessed_data/'
print PRE_PATH
OUT = PRE_PATH + 'preprocessed_data_{}_2.pkl'.format(TYPE)


if __name__ == '__main__':
    print 'combining data from preprocessing step...'
    files = [PRE_PATH+x for x in os.listdir(PRE_PATH) if (
     x.find('preprocessed_data') != -1) & (x.find(TYPE) != -1)]
    print files
    dfs = []
    for fn in files:
        print 'reading file %s' % (fn)
        df = joblib.load(fn)
        dfs.append(df)
    final = pd.concat(dfs, axis=0)
    final.reset_index(drop=True, inplace=True)
    print 'shape of final DF: ', final.shape
    print 'save'
    final.to_pickle(OUT)
