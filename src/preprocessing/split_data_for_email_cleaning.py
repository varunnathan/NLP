import sys
import pandas as pd
from data_preparation import DATA_PATH


# GLOBALS
TYPE = sys.argv[1]
INP = DATA_PATH + 'prepared_data_{}_2.csv'.format(TYPE)
OUT = DATA_PATH + 'prepared_data_{}_2_part_{}.csv'
if TYPE == 'tickets':
    chunk_size = 5000
else:
    chunk_size = 20000


if __name__ == '__main__':
    print 'splitting data into chunks of {} rows each...'.format(chunk_size)
    df = pd.read_csv(INP)
    steps = df.shape[0]//chunk_size+1
    for step in range(steps):
        df1 = df.loc[(step*chunk_size):((step+1)*chunk_size)-1, :]
        df1.reset_index(drop=True, inplace=True)
	df1.to_csv(OUT.format(TYPE, step+1), index=False)
