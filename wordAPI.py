from datetime import timedelta
import requests
import key
import json
import logging.handlers
import logging
import pprint
from datetime import datetime
import urllib

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class engWord:
    # Constructor
    def __init__(self):
        self.ResultLang = 'ru'
        self.SourceLang = 'en'
        self.Topic = ''
        self.url = "https://wordsapiv1.p.rapidapi.com/words/"
        self.headers = {'x-rapidapi-host': "wordsapiv1.p.rapidapi.com",
                        'x-rapidapi-key': key.WordApi}

    def getRandomWord(self):
        try:
            url = "https://wordsapiv1.p.rapidapi.com/words/"
            headers = {'x-rapidapi-host': "wordsapiv1.p.rapidapi.com",
                       'x-rapidapi-key': key.WordApi}
            querystring = {"random": "true"}
            response = requests.request(
                "GET", url, headers=headers, params=querystring)
            data = json.loads(response.text)
            if data.get('pronunciation') is not None:
                pron = data['pronunciation']
                # check key 'all'
                if pron.get('all') is not None:
                    pronounce = data['pronunciation']['all']
                    return data['word'], pronounce       
            return data['word'], None
        except Exception as e:
            print(e)
            return data['word'], None

    def getWordOnTopic(self,):
        try:
            url = 'http://api.datamuse.com/words?topics={}'.format(self.Topic)
        except Exception as ex:
            print(ex)

    def getTranscription(self):
        try:
            pass
        except Exception as ex:
            print(ex)
            return 'Возникла ошибка:{}'.format(ex.args)

    def getTranslation(self, word):
        try:
            # detect lang
            url_detect = "https://translation.googleapis.com/language/translate/v2/detect"

            word_encoded = urllib.parse.quote(word)
            headers = {
                'content-type': "application/x-www-form-urlencoded",
                'cache-control': "no-cache"
            }
            payload = "q={}&key={}".format(
                word_encoded, key.GoogleTranslationKey)
            response = requests.request(
                "POST", url_detect, data=payload, headers=headers)
            print(response)
            self.SourceLang = json.loads(response.text)[
                'data']['detections'][0][0]['language']
            if self.SourceLang == 'ru':
                self.ResultLang = 'en'
            else:
                self.ResultLang = 'ru'
            # GOOGLE TRANSLATION API
            url = "https://translation.googleapis.com/language/translate/v2"

            payload = "q={}&target={}&key={}&source={}".format(
                word_encoded, self.ResultLang, key.GoogleTranslationKey, self.SourceLang)
            headers = {
                'content-type': "application/x-www-form-urlencoded",
                'cache-control': "no-cache"
            }
            response = requests.request(
                "POST", url, data=payload, headers=headers)

            result = json.loads(response.text)[
                'data']['translations'][0]['translatedText'].lower()

            return result
        except Exception as er:
            print(er)
            return "Возникла ошибка при переводе"
