import requests
from urllib3.exceptions import InsecureRequestWarning
from typing import List
from concurrent.futures import ThreadPoolExecutor

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class Ping():
    def __init__(self):
        self.message = "I'm a ping method"


    def get_response(self, url: str):
        """
        sends request to provided url and returns response with allow_redirects=False
        """
        try:
            return requests.get(url, allow_redirects=False, verify=False)
        except requests.exceptions.RequestException as err:
            raise SystemExit(err)
    

    def get_URL(self, url: str) -> str:
        """
        send request to provided URL and returns landed url from response
        """
        try:
            response = requests.get(url, verify=False).url
            # port address may be returned, hence removing from here
            url_port_split = response.split(":443")
            response = "".join(url_port_split)
            return response
        except requests.exceptions.RequestException as err:
            raise SystemExit(err)
        

    def getFinalURLs(self, urls: List[str]) -> List[str]:
        """
        returns list of landed urls by sending request to all provided URLs
        """
        with ThreadPoolExecutor() as executor:
            results = executor.map(self.get_URL, urls)
        return [result for result in results]


    def getStatusCodeOfURLs(self, urls: List[str]):
        """
        returns list of status codes by sending request to all provided
        """
        with ThreadPoolExecutor() as executor:
            results = executor.map(self.get_response, urls)
        return [response.status_code for response in results]
