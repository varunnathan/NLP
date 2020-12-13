# custom cleaning for global model
import re
import requests
import logging

# GLOBALS
LOCAL_ROOT = "/home/freshiq_team/vnathan/"
PROJ_PATH = LOCAL_ROOT + "freshservice_bot/"
LOG_FILE = PROJ_PATH + "custom_cleaner.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG
    )
logging.getLogger().addHandler(logging.StreamHandler())
formatter = logging.Formatter(
    '[%(levelname)1.1s %(asctime)s.%(msecs)d '
    '%(module)s:%(lineno)d] %(message)s',
    "%Y-%m-%d %H:%M:%S"
)  # creating own format
for handler in logging.getLogger().handlers:  # setting format for all handlers
    handler.setFormatter(formatter)
SPECIAL_TOKEN = "[s]"
NAME_URL = "http://ner.freshworksapi.com/person"
API_DATA = {'client_id': 'xxx', 'user_id': 'xxx',
            'username': 'navaneethan'}
URL_DCT = {"name": (NAME_URL, "persons")}
DATE_RULES = ["([1-3][0-9]{3})[-./\s](0?[1-9]|1[0-2]|jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)[-./\s]([0-3][0-9])",
              "([1-3][0-9]{3})[-./\s]([0-3][0-9])[-./\s](0?[1-9]|1[0-2]|jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)",
              "([1-3][0-9]{3})[-./\s]?(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)([0-3][0-9])",
              "([0-3][0-9])[-./\s]?(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)([1-3][0-9]{3})",
              "([0-3][0-9])[-./\s](0?[1-9]|1[0-2]|jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)[-./\s]([1-3][0-9]{3})",
              "(0?[1-9]|1[0-2]|jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)[-./\s]([0-3][0-9])[-./\s]([1-3][0-9]{3})",
              "([1-3][0-9]{3})[-/\s](0?[1-9]|1[0-2]|jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)",
              "(0?[1-9]|1[0-2]|jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)[-/\s]([1-3][0-9]{3})",
              "(\d{2,4})[-/\s]q([1-4])", "q([1-4])[-/\s](\d{2,4})",
              "(noon|midni(ght|te)|(the )?(eod|end of (the )?day))",
              "(morning|after ?noo?n(ish)?|evening|night|(at )?lunch)",
              "early ((in|hours of) the )?morning", "(late )?toni(ght|gth|te)s?",
              "mondays?|mon\.?", "tuesdays?|tues?\.?", "wed?nesdays?|wed\.?",
              "thursdays?|thu(rs?)?\.?", "fridays?|fri\.?", "saturdays?|sat\.?",
              "sundays?|sun\.?", "january|jan\.?", "february|feb\.?",
              "march|mar\.?", "april|apr\.?", "may", "june|jun\.?",
              "july|jul\.?", "august|aug\.?", "september|sept?\.?",
              "october|oct\.?", "november|nov\.?", "december|dec\.?"]


class Custom_Cleaner(object):

    def __init__(self, lower_case=True, name_replacement=True,
                 email_replacement=True, phone_replacement=True,
                 datetime_replacement=True, url_replacement=True,
                 html_replacement=True, numeral_replacement=True,
                 special_token=SPECIAL_TOKEN, api_data=API_DATA,
                 url_dct=URL_DCT, date_rules=DATE_RULES, colon_count=4,
                 truncation_length=500):
        self.lower_case = lower_case
        self.name_replacement = name_replacement
        self.email_replacement = email_replacement
        self.phone_replacement = phone_replacement
        self.datetime_replacement = datetime_replacement
        self.url_replacement = url_replacement
        self.html_replacement = html_replacement
        self.numeral_replacement = numeral_replacement
        self.special_token = special_token
        self.api_data = api_data
        self.url_dct = url_dct
        self.date_rules = date_rules
        self.colon_count = colon_count
        self.truncation_length = truncation_length

    def fit_transform(self, inp_txt):
        
        logging.info("inp_text: %s" %inp_txt)
        
        if not ((inp_txt) and (inp_txt != "")):
            logging.info("Input text is empty. Quitting")
            return inp_txt
        elif inp_txt.count(":") > self.colon_count:
            logging.info("Input text has more than %d colons. So, it should most likely be a form. Hence, returning an empty string" %(self.colon_count))
            return ""
        else:
            logging.info("truncation")
            inp_txt = inp_txt[:self.truncation_length]
            logging.info("length of input text is %d" %(len(inp_txt)))
            
            if self.lower_case:
                logging.info("lower casing")
                inp_txt = inp_txt.strip().lower()
                logging.info("text after lower casing: %s" %inp_txt)

            logging.info("correction of improper emails")
            inp_txt = self._detect_improper_urls_mailids(inp_txt, "mail")
            logging.info("correction of improper urls")
            inp_txt = self._detect_improper_urls_mailids(inp_txt, "url")

            if self.email_replacement:
                logging.info("email replacement")
                pattern = re.compile("([\w_+-]+(?:(?: dot |\.)[\w_+-]+){0,10})(?: at |@)([a-zA-Z]+(?:(?:\.| dot )[\w_-]+){1,10})")
                logging.info("replacement of emails")
                inp_txt = self._detect_custom_patterns(inp_txt, pattern)
                logging.info("text after email replacement: %s" %inp_txt)

            if self.name_replacement:
                logging.info("name replacement")
                logging.info("extraction of person names")
                ents = self._extract_entities(inp_txt, "name", self.url_dct,
                                              self.api_data)
                logging.info(str(ents))
                if ents:
                    logging.info("replacement of detected names")
                    inp_txt = self._replace_entities(inp_txt, ents)
                logging.info("text after name replacement: %s" %inp_txt)

            if self.datetime_replacement:
                logging.info("datetime replacement")
                logging.info("extraction of dates")
                ent = self._extract_date_time(inp_txt, self.date_rules)
                logging.info(str(ent))
                if ent:
                    logging.info("replacement of detected dates")
                    inp_txt = self._replace_entities(inp_txt, ent)
                logging.info("text after date replacement: %s" %inp_txt)

                logging.info("extraction of times")
                pattern = "((([0]?[1-9]|1[0-2])((-|:|\.)[0-5][0-9](-|:|\.)[0-5][0-9])?( )?(am|pm))|(([0]?[0-9]|1[0-9]|2[0-3])(-|:|\.)[0-5][0-9]((-|:|\.)[0-5][0-9])?))"
                ent = self._extract_date_time(inp_txt, pattern)
                logging.info(str(ent))
                if ent:
                    logging.info("replacement of detected times")
                    inp_txt = self._replace_entities(inp_txt, ent)
                logging.info("text after time replacement: %s" %inp_txt)

            if self.phone_replacement:
                logging.info("phone number replacement")
                pattern = re.compile("\+{0,1}\d{1,3}\D{0,3}\d{3}\D{0,3}\d{3}\D{1}\d{4}|\(?\+{0,1}\d{1,3}\D{0,3}\d{3}\D{0,3}\d{4,7}|\d{3}\D{0,3}\d{4,7}")
                logging.info("replacement of phone numbers")
                inp_txt = self._detect_custom_patterns(inp_txt, pattern)
                logging.info("text after phone replacement: %s" %inp_txt)

            if self.url_replacement:
                logging.info("url replacement")
                pattern = re.compile(r'https?://\S+')
                logging.info("replacement of urls")
                inp_txt = self._detect_custom_patterns(inp_txt, pattern)
                logging.info("text after url replacement: %s" %inp_txt)

            if self.html_replacement:
                logging.info("html replacement")
                pattern = re.compile('<.*?>')
                inp_txt = self._detect_custom_patterns(inp_txt, pattern)
                logging.info("text after html replacement: %s" %inp_txt)

            if self.numeral_replacement:
                logging.info("numeral replacement")
                pattern = re.compile('[0-9]+')
                inp_txt = self._detect_custom_patterns(inp_txt, pattern)
                logging.info("text after numeral replacement: %s" %inp_txt)

            return inp_txt

    def _detect_improper_urls_mailids(self, inp_text, entity_type):
        """custom function to detect and rectify discrepancies in url
           entity_type: mail or url"""
        if entity_type == "url":
            pattern = r"https?://\S+. \S+. \S*"
        elif entity_type == "mail":
            pattern = r"\S+. \S+@\S+. com|\S+@\S+. com"
        result = re.findall(pattern, inp_text)
        if result:
            for r in result:
                r_new = r.replace(" ", "")
                inp_text = re.sub(re.escape(r), r_new, inp_text)
        return inp_text

    def _detect_custom_patterns(self, inp_text, pattern):
        return pattern.sub(self.special_token, inp_text)

    def _extract_entities(self, inp_text, entity_type, url_dct, api_data):
        api_data["text"] = inp_text
        url_tup = url_dct.get(entity_type)
        print("url: ", url_tup[0])
        res = requests.post(url=url_tup[0], json=api_data)
        outs = []
        
        try:
            res_json = res.json()
            if res_json[url_tup[1]]:
                outs = [x["value"] for x in res_json[url_tup[1]]]
        except:
            logging.info("API Call was unsuccessful for %s" %(inp_text))
            pass

        return outs

    def _extract_date_time(self, inp_text, rules):
        if isinstance(rules, list):
            out = []
            for rule in rules:
                match = re.search(rule, inp_text)
                if match:
                    out.append(match.group())
            if out:
                out_sorted = sorted(out, key=lambda x: len(x), reverse=True)
                return out_sorted[0]
        elif isinstance(rules, str):
            match = re.search(rules, inp_text)
            if match:
                return match.group()

    def _replace_entities(self, inp_text, entity):
        if isinstance(entity, list):
            for ent in entity:
                inp_text = re.sub(re.escape(ent), self.special_token, inp_text)
        elif isinstance(entity, str):
            inp_text = re.sub(re.escape(entity), self.special_token, inp_text)
        return inp_text
