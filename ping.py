import requests
from typing import List
from concurrent.futures import ThreadPoolExecutor


class Ping():
    def __init__(self):
        self.message = "I'm a ping method"


    def pingURL(self, url: str):
        """Pings supplied url and returns status code"""
        try:
            return requests.get(url, allow_redirects=False)
        except requests.exceptions.RequestException as err:
            raise SystemExit(err)
    

    def fetchURL(self, url: str) -> str:
        try:
            res = requests.get(url).url
            # port address may be returned, hence removing from here
            url_port_split = res.split(":443")
            res = "".join(url_port_split)
            return res
        except requests.exceptions.RequestException as err:
            raise SystemExit(err)
        

    def getFinalURLs(self, urls: List[str]):
        with ThreadPoolExecutor() as executor:
            results = executor.map(self.fetchURL, urls)
        return [result for result in results]


    def getStatusCodeOfURLs(self, urls: List[str]):
        with ThreadPoolExecutor() as executor:
            results = executor.map(self.pingURL, urls)
        return [response.status_code for response in results]
