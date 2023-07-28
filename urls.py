from typing import List, Tuple
import re
from mylogging import log_setup
import logging

log_setup()
logger = logging.getLogger(__name__)


class Urls:
    def __init__(self, clipboard_item):
        self.success_count: int = 0
        self.failed_count: int = 0
        self.removed_count: int = 0
        self.total_found_urls: int = 0
        self.src_dest_urls: List[Tuple[str, str]] = []
        self.src_dest_urls += self.extractUrls(clipboard_item)

    def extractUrls(self, string_data):
        src_dest_urls = self.splitURLs(self.findURLs(string_data))
        if src_dest_urls:
            self.total_found_urls += len(src_dest_urls)
        return src_dest_urls

    def add_more_urls(self, string_data):
        """Add more URLs"""
        self.src_dest_urls += self.extractUrls(string_data)

    def getSrcDestURLs(self):
        """
        Returns complete urls found in the supplied string in tuple form of
        (source_url, destination_url)
        """
        return self.src_dest_urls

    def setSrcDestURLs(self, src_dest_url_json) -> None:
        """
        Sets urls from previous data stored in json format
        to src_dest_url
        This method also updates the total_found_urls count
        """
        urls = [(from_, to_) for from_, to_ in src_dest_url_json]
        self.src_dest_urls = urls
        self.total_found_urls: int = len(urls)

    def increment_count(self, counter: int) -> int:
        """
        Function to increment counter
        """
        counter = counter + 1
        return counter

    def findURLs(self, string: str) -> List[str]:
        """Returns list of all urls found in the supplied string"""
        logger.debug("Searching for URLs")
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        urls = re.findall(regex, string)
        logger.debug(f"Found {len(urls)} URL(s)")
        return [x[0] for x in urls]

    def splitURLs(self, urls: List[str]):
        """Returns a dictionary of urls splitted in the from of From and To"""
        total_urls = len(urls)
        if total_urls < 2:
            logger.debug("Less than 2 valid urls received")
            return []
        if total_urls % 2 != 0:
            logger.debug("Found only {total_urls} URL(s)")
            return []

        # Checks if url is missing scheme, it will append the secure one
        for i in range(total_urls):
            if urls[i].startswith("www"):
                logger.debug(f"Prefixing scheme to {urls[i]}")
                urls[i] = f"https://{urls[i]}"
            # if not urls[i].endswith('/'):
            #     logger.debug(f"Postfixing forward slash to {urls[i]}")
            #     urls[i] = f"{urls[i]}/"

        from_urls: List[str] = urls[::2]
        to_urls: List[str] = urls[1::2]
        urls = [(from_, to_) for from_, to_ in zip(from_urls, to_urls)]
        return urls

    def remove_urls(self, url_pairs: list[tuple]):
        """
        removes the url passed to the function from the src_dest_urls
        """
        for entry in url_pairs:
            self.src_dest_urls.remove(entry)
            self.removed_count = self.increment_count(self.removed_count)
            logger.debug(f"Removed {entry}")

    def add_success_counter(self):
        self.success_count += 1

    def add_failure_counter(self):
        self.failed_count += 1
