import requests   
from bs4 import BeautifulSoup

class Translator:
    limit = 15
    remote_translator_URL = "https://www.slovnik.cz/bin/mld.fpl"
    request_payload = {"trn": "přeložit", "dictdir": "encz.cz", "lines": limit, "js": 1}
    key_name = "vcb"

    def __init__(self, text) -> None:       
        self.text = text
        self.html_response = ""
        self.translation_dict = []
        self.formatted_text = ""

    def _request_translation(self):         
        url = self.remote_translator_URL
        self.request_payload[self.key_name] =  self.text
        self.html_response = requests.get(url, self.request_payload).text
        return self.html_response

    def _parse(self):
        soup = BeautifulSoup(self.html_response, 'html.parser')
        for item in soup.find_all(class_ = "pair"):
            self.translation_dict.append((item.find(class_ = "l").get_text(), item.find(class_ = "r").get_text()))
        return self.translation_dict    

    def _format_translation(self):        
        for i,y in self.translation_dict:
            self.formatted_text += i + " - " + y + "\n"
        return self.formatted_text

    def get(self):
        self._request_translation()
        self._parse()        
        return self._format_translation()

