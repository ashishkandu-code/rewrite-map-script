import os
from requests.utils import urlparse
from collections import defaultdict
import sys


def create_file_if_not_exist(filename):
    """
    Create the file in the current directory if not exist
    """
    if os.path.isfile(filename) is False:
        try:
            open(filename, 'a').close()
        except OSError:
            print('Failed creating the file', filename)


def is_status_code_ok(to_url: str, status_code: int):
    """
    Returns False if redirection found otherwise print URLs status (200 | 404)
    """
    if status_code == 200:
        print(f"OK: {to_url}")
    elif status_code == 404:
        print(f"PAGE NOT FOUND: {to_url}")
    elif status_code == 301:
        return False
    return True


def get_domains(source_urls: list):
    """
    Returns defaultdict of fqdn without path as key and list of indexes (w.r.t provided urls list) of following urls as values
    """
    parsed_urls = [urlparse(url) for url in source_urls]
    pathless_urls = [
        f"{parsed_url.scheme}://{parsed_url.netloc}/" for parsed_url in parsed_urls]

    domains_data = defaultdict(list)
    for index, url in enumerate(pathless_urls):
        domains_data[url].append(index)
    return domains_data


def remove_prefix(text: str, prefix: str) -> str:
    """
    Helper function to remove prefix
    """
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def terminate():
    """
    Terminates the execution with message
    """
    sys.exit("\nTerminating program")