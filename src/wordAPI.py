from datetime import timedelta
import requests
import key
import json
import logging.handlers
import logging
import pprint
from datetime import datetime
import urllib
from datamuse import datamuse
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class engWord:
    # Constructor
    def __init__(self):
        self.ResultLang = 'ru'
        self.SourceLang = 'en'
        self.Topic = ''
        self.MaxWords = 1000
        self.datamuse = datamuse.Datamuse()

    def getWordOnTopic(self, topic, position):
        try:
            url = "http://api.datamuse.com/words"
            querystring = {"ml": topic,
                           "max": position+1, "md": "r", "ipa": "1"}
            headers = {'cache-control': "no-cache"}
            response = requests.request(
                "GET", url,  headers=headers, params=querystring)
            words = json.loads(response.text)
            tags = words[position]['tags']
            transcripton = '['+tags[len(tags)-1].split(':')[1]+']'
            word = words[position]['word']
            # TODO get synonym of a word
            return transcripton, word
        except Exception as exp:
            logging.error('[getWordOnTopic]: {}'.format(exp))
            return 'Возникла ошибка:{}'.format(exp.args), None

    def getSynonym(self, word, position):
        try:
            url = "http://api.datamuse.com/words"
            querystring = {"rel_syn": word,
                           "max": position+1}
            headers = {'cache-control': "no-cache"}
            logging.info('Making request to get synonyms')
            response = requests.request(
                "GET", url,  headers=headers, params=querystring)
            temp = json.loads(response.text)
            logging.info(
                'Request to get sysnonym succeeded.Result:{}'.format(temp))
            synonyms = []
            for syn in temp:
                synonyms.append(syn['word'])
            return synonyms if len(synonyms) > 0 else None
        except Exception as ex:
            logging.error('[getSynonym]:Error {}'.format(ex))
            return 'Возникла ошибка:{}'.format(ex.args), None

    def detectLanguage(self, word):
        try:
            url_detect = "https://translation.googleapis.com/language/translate/v2/detect"
            headers = {
                'content-type': "application/x-www-form-urlencoded",
                'cache-control': "no-cache"
            }
            payload = "q={}&key={}".format(
                word, key.GoogleTranslationKey)
            response = requests.request(
                "POST", url_detect, data=payload, headers=headers)

            self.SourceLang = json.loads(response.text)[
                'data']['detections'][0][0]['language']
            if self.SourceLang == 'ru':
                self.ResultLang = 'en'
            else:
                self.ResultLang = 'ru'
        except Exception as exp:
            logging.error(exp)
            return "Возникла ошибка при определении языка: {}".format(exp)

    def getTranslation(self, word):
        try:
            # encode word
            word = urllib.parse.quote(word)
            # detect lang
            self.detectLanguage(word)
            logging.info('SourceLang:{}, ResultLang:{}'.format(
                self.ResultLang, self.SourceLang))
            # GOOGLE TRANSLATION API
            url = "https://translation.googleapis.com/language/translate/v2"
            payload = "q={}&target={}&key={}&source={}".format(
                word, self.ResultLang, key.GoogleTranslationKey, self.SourceLang)
            headers = {
                'content-type': "application/x-www-form-urlencoded",
                'cache-control': "no-cache"
            }
            response = requests.request(
                "POST", url, data=payload, headers=headers)

            logging.info('[getTranslation]: list of translations:{}'.format(
                json.loads(response.text)))
            translateVars = []
            allTranslations = json.loads(response.text)[
                'data']['translations']
            logging.info(allTranslations)
            for tr in allTranslations:
                translateVars.append(tr['translatedText'])
            return ', '.join(translateVars)
        except Exception as exp:
            logging.error(exp)
            return "Возникла ошибка при переводе:{}".format(exp)
