import requests
import key
import json
import pprint


class engWord:
    # Constructor
    def __init__(self):
        self.ResultLang = 'ru'
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
            print(response.text)
            return response.text
        except Exception as e:
            print(e)
            return 'Возникла ошибка:{}'.format(e.args)

    def getTranscription(self):
        try:
            pass
        except Exception as ex:
            print(ex)
            return 'Возникла ошибка:{}'.format(ex.args)

    def getTranslation(self, word):
        try:
            # GOOGLE TRANSLATION API
            url = "https://translation.googleapis.com/language/translate/v2"
            payload = "q={}&target={}&key={}".format(
                word, self.ResultLang, key.GoogleTranslationKey)
            headers = {'content-type': "application/x-www-form-urlencoded"}
            response = requests.request(
                "POST", url, data=payload, headers=headers)
            result = json.loads(response.text)[
                'data']['translations'][0]['translatedText'].lower()
            print(response)

            return result
        except Exception as er:
            print(er)
            return "Возникла ошибка при переводе"
