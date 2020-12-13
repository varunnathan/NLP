import pandas as pd
import numpy as np
import os


# GLOBALS
LOCAL_DATA_ROOT = '/Users/varunn/Documents/projects/Sentence_Embeddings/'
DATA_PATH = LOCAL_DATA_ROOT + 'raw_data/'
NAME = 'data_for_sentence_embeddings_{}_2.csv.gz'
INP_TICKETS_FN = DATA_PATH + NAME.format('tickets')
INP_TICKET_BODIES_FN = DATA_PATH + NAME.format('ticket_bodies')
INP_NOTES_FN = DATA_PATH + NAME.format('notes')
INP_NOTE_BODIES_FN = DATA_PATH + NAME.format('note_bodies')
OUT_TICKETS_FN = DATA_PATH + 'prepared_data_tickets_2.csv'
OUT_NOTES_FN = DATA_PATH + 'prepared_data_notes_2.csv'


if __name__ == '__main__':
    print 'data preparation for creating sentence embeddings...'
    print 'reading data'
    df_tickets = pd.read_csv(INP_TICKETS_FN)
    df_notes = pd.read_csv(INP_NOTES_FN)
    df_note_bodies = pd.read_csv(INP_NOTE_BODIES_FN)
    mylist = []

    for chunk in  pd.read_csv(INP_TICKET_BODIES_FN, sep=',', chunksize=20000):
        mylist.append(chunk)

    df_ticket_bodies = pd.concat(mylist, axis= 0)
    del mylist

    print 'tickets data preparation'
    df_ticket_bodies.rename(columns={'ticket_id': 'id'}, inplace=True)
    cols = ['id', 'description', 'description_html']
    df_tickets = pd.merge(df_tickets, df_ticket_bodies[cols], on='id',
                          how='left')
    mask = (df_tickets['spam'] == 0) & (df_tickets['source'] == 1)
    df_tickets1 = df_tickets.loc[mask, :]
    df_tickets1.reset_index(drop=True, inplace=True)
    df_tickets1.fillna('', inplace=True)
    print df_tickets1.shape
    print df_tickets1['description_html'].isnull().sum()
    print 'save'
    df_tickets1.to_csv(OUT_TICKETS_FN, index=False)

    print 'notes data preparation'
    df_notes.rename(columns={'id': 'note_id'}, inplace=True)
    df_notes = pd.merge(df_notes, df_note_bodies[['note_id', 'body']],
                        on='note_id', how='left')
    df_notes.rename(columns={'notable_id': 'id'}, inplace=True)
    df_notes1 = pd.merge(df_tickets1[['id']], df_notes[['note_id', 'id', 'body']],
                           on='id', how='left')
    df_notes1.sort('note_id', ascending=True, inplace=True)
    df_notes1.reset_index(drop=True, inplace=True)
    df_notes1.fillna('', inplace=True)
    print df_notes1.shape
    print df_notes1['body'].isnull().sum()
    print 'save'
    df_notes1.to_csv(OUT_NOTES_FN, index=False)
