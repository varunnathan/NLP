import pandas as pd
import pickle
import sys
import os
import re
from preprocessing import PreProcessor
from config import *

# GLOBALS
ACC = sys.argv[1]
TYPE = sys.argv[2]
PART = sys.argv[3]
INP = INT_PATH + 'prepared_data_{}_{}_part_{}.csv'.format(TYPE, ACC, PART)
OUT = PRE_PATH + 'preprocessed_data_{}_{}_part_{}.pkl'.format(TYPE, ACC, PART)


def data_cleaning(data, type=TYPE):
    df = data.copy()
    if DESC_COL in df:
        df[DESC_COL] = df[DESC_COL].apply(lambda x: re.sub('[0-9]+', '', str(x)))
    print 'class instantiation'
    if type == 'tickets':
        preprocessor = PreProcessor(email_cleaning=True, custom_cleaning=True,
                                    note_flag=False)
    else:
        print 'include source and subject columns in data'
        df[SOURCE_COL] = 1
        df[SUBJECT_COL] = ''
        preprocessor = PreProcessor(email_cleaning=True, custom_cleaning=True,
                                    desc_col='body', note_flag=True)
    df1 = preprocessor._cleaning(df)
    return df1


def main(type=TYPE):
    print 'read file %s' % (INP)
    df = pd.read_csv(INP)
    print 'preprocessing of data'
    df_pre = data_cleaning(df, type)
    print 'completed'
    print 'save'
    df_pre.to_pickle(OUT)


if __name__ == '__main__':
    print 'preprocessing begins for part %s...' % (PART)
    main()
