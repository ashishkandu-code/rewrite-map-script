from typing import List, Tuple
import re
from mylogging import log_setup
import logging

log_setup()
logger = logging.getLogger(__name__)

class Urls:
    def __init__(self, clipboard_item):
        self.src_dest_urls = self.splitURLs(self.findURLs(clipboard_item))
        self.total_found_urls: int = len(self.src_dest_urls)
        self.success_count:int = 0
        self.failed_count:int = 0
        self.removed_count: int = 0

    def getSrcDestURLs(self):
        """
        Returns complete urls found in the supplied string in tuple form of
        (source_url, destination_url)
        """
        return self.src_dest_urls
    
    def increment_count(self, counter: int) -> int:
        counter = counter + 1
    

    def findURLs(self, string: str) -> List[str]:
        """Returns list of all urls found in the supplied string"""
        logger.debug("Searching for URLs")
        regex=r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        urls= re.findall(regex,string)
        logger.debug(f"Found {len(urls)} URL(s)")
        return [x[0] for x in urls]


    def splitURLs(self, all_urls: List[str]):
        """Returns a dictionary of urls splitted in the from of From and To"""
        total_urls = len(all_urls)
        if total_urls < 2:
            logger.debug("Less than 2 valid urls received")
            return None
        if total_urls%2 != 0:
            logger.debug("Found only {total_urls} URL(s)")
            return None

        # Checks if url is missing scheme, it will append the secure one
        for i in range(total_urls):
            if all_urls[i].startswith("www"):
                logger.debug(f"Prefixing scheme to {all_urls[i]}")
                all_urls[i] = f"https://{all_urls[i]}"
            # if not all_urls[i].endswith('/'):
            #     logger.debug(f"Postfixing forward slash to {all_urls[i]}")
            #     all_urls[i] = f"{all_urls[i]}/"

        from_urls: List[str] = all_urls[::2]
        to_urls: List[str] = all_urls[1::2]
        urls = [(from_, to_) for from_, to_ in zip(from_urls, to_urls)]
        return urls


    def remove_urls(self, from_to_entries):
        for entry in from_to_entries:
            self.src_dest_urls.remove(entry)
            self.increment_count(self.removed_count)
            logger.debug(f"Removed {entry}")
