LOCAL_DATA_ROOT = '/Users/varunn/Documents/projects/Sentence_Embeddings/'
INP_PATH = LOCAL_DATA_ROOT + 'raw_data/'
INT_PATH = LOCAL_DATA_ROOT + 'inter_data/'
PRE_PATH = LOCAL_DATA_ROOT + 'preprocessed_data/'
MODEL_PATH = LOCAL_DATA_ROOT + 'modelling/'
RESULTS_PATH = LOCAL_DATA_ROOT + 'results/'
INP_TICKETS_FN = INP_PATH + 'data_tickets_{}.csv.gz'
INP_TICKET_BODIES_FN = INP_PATH + 'data_ticket_bodies_{}.csv.gz'
INP_NOTES_FN = INP_PATH + 'data_notes_{}.csv.gz'
INP_NOTE_BODIES_FN = INP_PATH + 'data_note_bodies_{}.csv.gz'
PREPARED_TICKET_FN = INT_PATH + 'prepared_data_tickets_{}.csv'
PREPARED_NOTE_FN = INT_PATH + 'prepared_data_notes_{}.csv'
PREPROCESSED_TICKET_FN = PRE_PATH + 'preprocessed_data_tickets_{}.pkl'
PREPROCESSED_NOTE_FN = PRE_PATH + 'preprocessed_data_notes_{}.pkl'
MODELLING_DATA_TICKET_FN = MODEL_PATH + 'data_for_modelling_tickets_A1_{}.csv'
MODELLING_DATA_COMBINED_FN = MODEL_PATH + 'data_for_modelling_combined_{}_{}.csv'
TEST_START_DATE = '2018-12-30'
ID_COL = 'id'
SOURCE_COL = 'source'
SUBJECT_COL = 'subject'
DESC_COL = 'description_html'
DATE_COL = 'date'
L1_FEAT_COL = 'sub_desc_custom_cleaned'
SAMPLE = 'sample'
SEED = 2018
CONTRACTION = False
FILTER_POS = False
ITER = 'ITER'
KEEP_ENG = True
LEM = False
LOWER_CASE = True
MAX_DF = 'MAX_DF'
MAX_FEATURES = 'MAX_FEATURES'
MIN_DF = 'MIN_DF'
NGRAM_RANGE = 'NGRAM_RANGE'
POS_VAR = ('N', 'J')
RANDOM_STATE = 'RANDOM_STATE'
REGEX_CLEANING = False
REMOVE_IGNORE_WORDS = False
REMOVE_NONALPHA = True
REMOVE_NUMERALS = False
REMOVE_PUNKT = False
REMOVE_STOP = True
SPELL_CHECK = False
STEM = True
SVD_COMP = 'SVD_COMP'
TEMPLATE_REMOVAL = False
TEMPLATE_START_STRING = ''
TOKENIZE = False

MODEL_CONFIG = {
    'chat': {
        SVD_COMP: 400,
        MAX_FEATURES: 50000,
        MIN_DF: 20,
        MAX_DF: 0.5,
        NGRAM_RANGE: (1, 3),
        RANDOM_STATE: 2018,
        ITER: 10
    },
    'email': {
        SVD_COMP: 1200,
        MAX_FEATURES: 80000,
        MIN_DF: 20,
        MAX_DF: 0.5,
        NGRAM_RANGE: (1, 3),
        RANDOM_STATE: 2018,
        ITER: 10
    }
}
