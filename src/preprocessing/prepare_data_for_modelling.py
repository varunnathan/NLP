"""
# steps
1. Preprocess email cleaned column with just 3 options viz. lower_case,
keep_eng and remove_numerals - Approach2
1a. Create a block of text for each row that concatenates sub, desc and
notes in the correct order (sorted by created_at) - Take data preprocessed using Approach2 - sub_desc_notes_approach2
2. Split data into train, lookup and test (last 3 days of data in test;
last 1 month of data from the earliest date in test set in lookup; train
includes lookup as well)
3. Train sentence embeddings with the following approaches:
a) LSA - 1) Approach1 + only tickets 2) Approach1 + tickets and notes appended
b) Fasttext - 1) Approach1 + only tickets 2) Approach1 + tickets and notes appended
c) Skip Thoughts - 1) sub_desc_notes_approach2
d) Autoencoders - 1) sub_desc_notes_approach2
e) Universal Sentence Encoder - 1) sub_desc_notes_approach2
f) ELMO - 1) sub_desc_notes_approach2
g) BERT - 1) sub_desc_notes_approach2
"""
import joblib
import pandas as pd
from data_preparation import LOCAL_DATA_ROOT
from utility import *


# GLOBALS
PRE_PATH = LOCAL_DATA_ROOT + 'preprocessed_data/'
INP_TICKETS_FN = PRE_PATH + 'preprocessed_data_{}_2.pkl'.format('tickets')
INP_NOTES_FN = PRE_PATH + 'preprocessed_data_{}_2.pkl'.format('notes')
OUT_PATH = LOCAL_DATA_ROOT + 'modelling/'
OUT_TICKETS_A1_FN = OUT_PATH + 'data_for_modelling_tickets_A1.csv'
OUT_COMBINED_A1_FN = OUT_PATH + 'data_for_modelling_combined_A1.csv'
OUT_COMBINED_A2_FN = OUT_PATH + 'data_for_modelling_combined_A2.csv'
OUT_COMBINED_CONCAT_A2_FN = OUT_PATH + 'data_for_modelling_combined_concat_A2.csv'


def _concat(sub, desc):
    if (sub == '') | (pd.isnull(sub)):
        return desc
    else:
        return sub + '. ' + desc


def train_test_split(data):
    df = data.copy()
    df['date'] = df['created_at'].apply(lambda x: pd.to_datetime(
     x.split(' ')[0], format='%Y-%m-%d'))
    mask_test = df['date'] >= '2018-12-15'
    mask_lookup = ((df['date'] >= (pd.to_datetime('2018-12-14') - pd.DateOffset(n=30))) &
                   (df['date'] <= '2018-12-14'))
    df['sample'] = 'train'
    df.loc[mask_test, 'sample'] = 'test'
    df.loc[mask_lookup, 'sample'] = 'lookup'
    id_sample_dct = dict(zip(df['id'], df['sample']))
    return id_sample_dct


if __name__ == '__main__':
    print 'preparing data for modelling...'
    print 'reading file %s' % (INP_TICKETS_FN)
    df_tickets = joblib.load(INP_TICKETS_FN)
    if 'sub_desc_custom_cleaned' not in df_tickets:
        df_tickets.drop('sub_desc_custom_cleaned', axis=1, inplace=True)
        df_tickets['sub_desc_custom_cleaned'] = map(
         lambda x, y: _concat(x, y), df_tickets['subject_custom_cleaned'],
         df_tickets['description_html_custom_cleaned'])
    print 'reading file %s' % (INP_NOTES_FN)
    df_notes = joblib.load(INP_NOTES_FN)
    print 'drop some columns from df_notes DF and df_tickets DF'
    df_notes.drop(['subject', 'subject_custom_cleaned',
                   'sub_desc_custom_cleaned'], axis=1, inplace=True)
    df_tickets.drop(['subject_custom_cleaned',
                     'description_html_custom_cleaned'], axis=1, inplace=True)
    print 'rename columns in df_tickets DF and df_notes DF'
    df_tickets.rename(columns={'sub_desc_custom_cleaned': 'sub_desc_custom_cleaned_A1'},
                      inplace=True)
    df_notes.rename(columns={'body_custom_cleaned': 'notes_custom_cleaned_A1'},
                    inplace=True)
    preprocessor = Text_Preprocessing(
     keep_eng=True, remove_nonalpha=False, lower_case=True, remove_punkt=False,
     regex_cleaning=False, remove_stop=False, remove_numerals=True,
     spell_check=False, contraction=False, stem=False, lem=False,
     filter_pos=False, tokenize=False, template_removal=False,
     remove_ignore_words=False)
    print 'preprocessing on df_tickets DF'
    _sub = preprocessor.fit_transform(df_tickets['subject'])
    _desc = preprocessor.fit_transform(df_tickets['description_html_cleaned'])
    df_tickets['sub_desc_custom_cleaned_A2'] = map(lambda x, y: _concat(x, y),
                                                   _sub, _desc)
    print 'preprocessing on df_notes DF'
    df_notes['notes_custom_cleaned_A2'] = preprocessor.fit_transform(
     df_notes['body_cleaned'])

    print 'step 1a'
    print 'sorting df_notes DF by note_id in ascending order'
    df_notes.sort('note_id', ascending=True, inplace=True)
    df_notes.reset_index(drop=True, inplace=True)
    print 'concat notes column grouped by id'
    body_cleaned_concat = pd.DataFrame(df_notes.groupby('id')['notes_custom_cleaned_A2'].apply(
     lambda x: ". ".join(x)))
    body_cleaned_concat.reset_index(inplace=True)
    print 'merge df_tickets DF and df_notes DF'
    cols = ['id', 'note_id', 'notes_custom_cleaned_A1', 'label']
    df_tickets1 = df_tickets.copy()
    df_tickets1.rename(columns={'sub_desc_custom_cleaned_A1': 'notes_custom_cleaned_A1'},
                       inplace=True)
    if 'note_id' not in df_tickets1:
        df_tickets1['note_id'] = None
    if 'label' not in df_tickets1:
        df_tickets1['label'] = 'sub_desc'
    if 'label' not in df_notes:
        df_notes['label'] = 'notes'
    df_combined = pd.concat([df_tickets1[cols], df_notes[cols]], axis=0)
    df_combined.rename(columns={'notes_custom_cleaned_A1': 'inp_text'}, inplace=True)
    print 'sort df_combined DF by id'
    df_combined.sort(['id', 'note_id'], ascending=True, inplace=True)
    df_combined.reset_index(drop=True, inplace=True)

    df_combined1 = pd.merge(df_tickets, body_cleaned_concat, on='id')
    print 'concat sub_desc_custom_cleaned_A2 and notes_custom_cleaned_A2'
    df_combined1['inp_text'] = map(
     lambda x, y: x+'. '+y, df_combined1['sub_desc_custom_cleaned_A2'],
     df_combined1['notes_custom_cleaned_A2'])

    df_tickets2 = df_tickets.copy()
    df_tickets2.rename(columns={'sub_desc_custom_cleaned_A2': 'notes_custom_cleaned_A2'},
                       inplace=True)
    if 'note_id' not in df_tickets2:
        df_tickets2['note_id'] = None
    if 'label' not in df_tickets2:
        df_tickets2['label'] = 'sub_desc'
    cols = ['id', 'note_id', 'notes_custom_cleaned_A2', 'label']
    df_combined2 = pd.concat([df_tickets2[cols], df_notes[cols]], axis=0)
    df_combined2.rename(columns={'notes_custom_cleaned_A2': 'inp_text'}, inplace=True)

    df_tickets.rename(columns={'sub_desc_custom_cleaned_A1': 'inp_text'},
                      inplace=True)

    print 'train_test_split'
    id_sample_dct = train_test_split(df_tickets)

    print 'add sample column to all the DFs'
    df_tickets['sample'] = df_tickets['id'].apply(lambda x: id_sample_dct[x])
    df_combined['sample'] = df_combined['id'].apply(lambda x: id_sample_dct[x])
    df_combined1['sample'] = df_combined1['id'].apply(lambda x: id_sample_dct[x])
    df_combined2['sample'] = df_combined2['id'].apply(lambda x: id_sample_dct[x])

    print 'save'
    df_tickets.to_csv(OUT_TICKETS_A1_FN, index=False)
    df_combined.to_csv(OUT_COMBINED_A1_FN, index=False)
    df_combined1.to_csv(OUT_COMBINED_A2_FN, index=False)
    df_combined2.to_csv(OUT_COMBINED_CONCAT_A2_FN, index=False)
