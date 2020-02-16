import requests
import key
import json


class engWord:
    # Constructor
    def __init__(self):
        self.ResultLang = 'ru'
        self.url = "https://wordsapiv1.p.rapidapi.com/words/"
        self.headers = {'x-rapidapi-host': "wordsapiv1.p.rapidapi.com",
                        'x-rapidapi-key': key.WordApi}

    def getRandomWord(self):
        url = "https://wordsapiv1.p.rapidapi.com/words/"
        headers = {'x-rapidapi-host': "wordsapiv1.p.rapidapi.com",
                   'x-rapidapi-key': key.WordApi}
        querystring = {"random": "true"}
        response = requests.request(
            "GET", url, headers=headers, params=querystring)
        print(response.text)
        return response.text

    def getTranslation(self, word):
        try:
            # GOOGLE TRANSLATION API
            url = "https://translation.googleapis.com/language/translate/v2"
            payload = "q={}&target={}&key={}".format(
                word, self.ResultLang, key.GoogleTranslationKey)
            headers = {'content-type': "application/x-www-form-urlencoded"}
            print(url, payload)
            response = requests.request(
                "POST", url, data=payload, headers=headers)
            result = json.loads(response.text)[
                'data']['translations'][0]['translatedText'].lower()

            return result
        except Exception as er:
            print(er)
            return "Возникла ошибка при переводе"

# VERSION OF https://rapidapi.com/gofitech/api/nlp-translation/endpoints
#        url = "https://nlp-translation.p.rapidapi.com/v1/translate"
# Forming query_word and config FROM and TO langs
#        payload = "from=en&text={}&to=ru".format(word)
#        headers = {
#            'x-rapidapi-host': "nlp-translation.p.rapidapi.com",
#            'x-rapidapi-key': "key.WordApi",
#            'content-type': "application/x-www-form-urlencoded"
#        }
#        response = requests.request("POST", url, data=payload, headers=headers)
#res = self.translator.translate(word)
# print(self.translator.translate(word))
