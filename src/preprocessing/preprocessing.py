import pandas as pd
import numpy as np
import os
import sys
import joblib
import json
import re
import unicodedata
from utility import *
sys.path.append('/Users/varunn/Documents/projects/FreshIQ_POC/Explorations/')
from cleaning import *
from cleaning.custom_cleaner import CustomCleaner
from config import *


class PreProcessor(object):

    def __init__(self, email_cleaning=False, custom_cleaning=True,
                 source_col='source', desc_col='description_html',
		         subject_col='subject', truncate_length=10000,
                 note_flag=False):
        self.email_cleaning = email_cleaning
        self.custom_cleaning = custom_cleaning
        self.desc_col = desc_col
        self.note_flag = note_flag
        self.subject_col = subject_col
        self.source_col = source_col
        self.truncate_length = truncate_length

    def _remove_non_ascii_characters(self, text):
        if (text):
            text = re.sub(r'[^\x00-\x7F]+',' ', text)
        return text

    def _primary_cleaning(self, row):
        cols = [self.desc_col]
        if not self.note_flag:
            ignore_sources = [[3]]
            main_ticket_bool = [True]
        else:
            ignore_sources = [[6, 9]]
            main_ticket_bool = [False]
        cleaned = [None]
        for i, col in enumerate(cols):
            if pd.notnull(row[col]):
                if row[self.source_col] in ignore_sources[i]:
                    cleaned[i] = row[col]
                else:
                    cleaner = CustomCleaner(row[col], row[self.source_col], main_ticket_bool[i], True, True)
                    cleaned[i] = cleaner.clean().get_text()
        return cleaned

    def _secondary_cleaning(self, series):
        custom_cleaner = Text_Preprocessing(
         keep_eng=KEEP_ENG, remove_nonalpha=REMOVE_NONALPHA, lower_case=LOWER_CASE,
         remove_punkt=REMOVE_PUNKT, remove_stop=REMOVE_STOP,
         remove_numerals=REMOVE_NUMERALS, spell_check=SPELL_CHECK,
         contraction=CONTRACTION, contraction_var=CONTRACTIONS,
         stem=STEM, lem=LEM, filter_pos=FILTER_POS, pos_var=POS_VAR,
         tokenize=TOKENIZE, template_removal=TEMPLATE_REMOVAL,
         template_start_string=TEMPLATE_START_STRING, regex_cleaning=REGEX_CLEANING,
         remove_ignore_words=REMOVE_IGNORE_WORDS, ignore_words=IGNORE_WORDS)
        return custom_cleaner.fit_transform(series)

    def text_encoding(self, x):
        try:
            return unicodedata.normalize('NFKD', unicode(x.lower().decode('utf-8'))).encode('utf-8','ignore')
        except:
            return unicodedata.normalize('NFKD', unicode(x.lower())).encode('utf-8','ignore')

    def _email_cleaning(self, data):
        df = data.copy()

        for col in [self.subject_col, self.desc_col]:
            print 'removal of non-ascii chars'
            df[col] = df[col].apply(lambda x: self._remove_non_ascii_characters(str(x)))
            print 'replace \x01 with blank'
            df[col] = df[col].apply(lambda x: x.replace('\x01', ''))
        df[self.desc_col] = df[self.desc_col].apply(lambda x: x[:self.truncate_length])

        print 'email cleaning begins'
        cleaned = df.apply(self._primary_cleaning, axis=1)
        df[self.desc_col+'_cleaned'] = cleaned.apply(lambda x: x[0])

        print 'normalization'
        for col in [self.subject_col, self.desc_col+'_cleaned']:
            df[col] = df[col].fillna('')
            df[col] = df[col].apply(lambda x: self.text_encoding(x))

        print 'shape of final DF: ', df.shape
        return df

    def _custom_cleaning(self, data):
        df = data.copy()

        print 'custom cleaning on sub'
        df[self.subject_col+'_custom_cleaned'] = self._secondary_cleaning(
         df[self.subject_col])

        print 'custom cleaning on desc'
        if self.desc_col+'_cleaned' not in df:
            print 'email cleaning should be run first'
        else:
            df[self.desc_col+'_custom_cleaned'] = self._secondary_cleaning(
             df[self.desc_col+'_cleaned'])

        print 'concat custom cleaned sub and desc'
        df['sub_desc_custom_cleaned'] = map(
         lambda a, b: str(a)+'. '+str(b), df[self.subject_col+'_custom_cleaned'],
         df[self.desc_col+'_custom_cleaned'])

        return df

    def _cleaning(self, data):
        df = data.copy()
        if self.email_cleaning:
            print 'email cleaning is starting'
            df = self._email_cleaning(df)
        else:
            for col in [self.subject_col, self.desc_col]:
                print 'removal of non-ascii chars'
                df[col] = df[col].apply(lambda x: self._remove_non_ascii_characters(str(x)))
                print 'replace \x01 with blank'
                df[col] = df[col].apply(lambda x: x.replace('\x01', ''))
            df[self.desc_col+'_cleaned'] = df[self.desc_col]
            print 'normalization'
            for col in [self.subject_col, self.desc_col+'_cleaned']:
                df[col] = df[col].fillna('')
                df[col] = df[col].apply(lambda x: self.text_encoding(x))
        if self.custom_cleaning:
            print 'custom cleaning is starting'
            df = self._custom_cleaning(df)
        else:
            print 'no custom cleaning is needed'

        return df
