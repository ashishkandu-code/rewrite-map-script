import pyperclip
from typing import Final
from requests.utils import urlparse
from ping import Ping
from urls import Urls
from collections import defaultdict
import time
import sys
import logging
import os
from datetime import datetime

from mylogging import log_setup

SLEEP_FOR: Final = .008


# set up logging configuration
log_setup()
logger = logging.getLogger(__name__)


# Creation of path in the current script directory
curr_path = os.path.dirname(os.path.realpath(__file__))
FORMATTED_OUTPUT: Final = os.path.join(curr_path, "output.txt")

# Create the file in current directory if not exist


def create_file_if_not_exist(filename):
    if os.path.isfile(filename) is False:
        try:
            open(filename, 'a').close()
        except OSError:
            print('Failed creating the file', filename)


def is_status_code_ok(to_url, status_code):
    """verify function to check destination URLs status (200 | 404), and if it is redirecting (301) back to source"""
    if status_code == 200:
        print(f"OK: {to_url}")
    elif status_code == 404:
        print(f"PAGE NOT FOUND: {to_url}")
    elif status_code == 301:
        return False
    return True


def get_domains(source_urls: list):

    parsed_urls = [urlparse(url) for url in source_urls]
    pathless_urls = [
        f"{parsed_url.scheme}://{parsed_url.netloc}/" for parsed_url in parsed_urls]

    domains_data = defaultdict(list)
    for index, url in enumerate(pathless_urls):
        domains_data[url].append(index)
    return domains_data


def remove_prefix(text: str, prefix: str) -> str:
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


if __name__ == "__main__":

    clipboard_content = pyperclip.paste()
    # pyperclip.copy(repr(clipboard_content))
    urls_obj = Urls(clipboard_content)

    logger.info("URLs found...")
    src_dest_urls = urls_obj.getSrcDestURLs()

    # the src_des_urls will be None if less than 2 valid urls supplied or paired urls not found
    if not src_dest_urls:
        logger.critical(
            "Valid URLs found were less than 2 or not enough to generate one-to-one pair")
        sys.exit("\nTerminating program")

    # # Printing all from to urls ---------------------->>>>>>>>>>>>> To be removed <<<<<<<<<<<<<---------------------------
    # for from_, to_ in src_dest_urls:
    #     print(f"{from_} {to_}")

    ping = Ping()

    logger.info("Running check for DESTINATION URLs")

    status_codes_to_urls = ping.getStatusCodeOfURLs(
        map(lambda x: x[1], src_dest_urls))  # Passing destination URLs

    print(f"\nRunning destination URLs verification...")
    """
    Below code pings to url and check their status codes also verifies if reverse redirection is present to avoid
    infinite redirection. If destination url is further redirecting it will alert the same
    """
    bad_urls = []
    for (from_url, to_url), status_code in zip(src_dest_urls, status_codes_to_urls):
        # To slow down the program for readability of outputs
        time.sleep(SLEEP_FOR)

        if from_url == to_url:
            logger.warning(f'{from_url} == {to_url}')
            continue

        if not is_status_code_ok(to_url=to_url, status_code=status_code):
            to_final_url = ping.fetchURL(to_url)

            if to_final_url == from_url or to_final_url.rstrip('/') == from_url.rstrip('/'):
                logger.warning(
                    f"Destination URL is redirected to source {to_url} -> {from_url}")
                bad_urls.append((from_url, to_url))
            else:
                print(f"Attention Required: {to_url}")
                logger.warning(
                    f"Destination URL is redirecting further {to_final_url}")
    if bad_urls:
        urls_obj.remove_urls(bad_urls)
    bad_urls.clear()

    from_final_urls = ping.getFinalURLs(
        map(lambda x: x[0], src_dest_urls))  # Passing source URLs

    print("\nRunning Pre URL validations...")
    for (from_url, to_url), from_final_url in zip(src_dest_urls, from_final_urls):
        # To slow down the program for readability of outputs
        time.sleep(SLEEP_FOR)

        if from_final_url == to_url or from_final_url.rstrip('/') == to_url.rstrip('/'):
            logger.warning(f"Already redirected {from_url} -> {to_url}")
            bad_urls.append((from_url, to_url))

    urls_obj.remove_urls(bad_urls)

    domains_k_index = get_domains(map(lambda x: x[0], src_dest_urls))
    # print(domains_k_index.items())

    formatted_from_to_strings = defaultdict(list)

    for domain, index_list in domains_k_index.items():
        domain_heading = f"For {urlparse(domain).netloc.split('.')[1].capitalize()}"
        print(f"\n{domain_heading}")
        for i in index_list:
            src, dest = src_dest_urls[i]
            formatted_src, formatted_dest = remove_prefix(src, domain), dest
            print(formatted_src, formatted_dest)
            formatted_from_to_strings[domain_heading].append(
                (formatted_src, formatted_dest))

    if any(formatted_from_to_strings):
        # Creates file for writitng console output
        create_file_if_not_exist(FORMATTED_OUTPUT)
        today = datetime.now()
        with open(FORMATTED_OUTPUT, 'a') as output_file:
            output_file.write(f"#{today.strftime('%d/%m/%Y, %H:%M:%S')}\n")
            for domain, src_dest_urls in formatted_from_to_strings.items():
                output_file.write(f"[{domain}]\n")
                for src_domainless_url, dest_url in src_dest_urls:
                    output_file.write(f"{src_domainless_url} {dest_url}\n")
                output_file.write('\n')
    print(f"\n{'-'* (len(FORMATTED_OUTPUT)+13)}\nOutput file: {FORMATTED_OUTPUT}")
    print(f'\nSummary')
    print(f'{"Total URLs found": <20}: {urls_obj.total_found_urls}')
    print(f'{"Bad URLs removed": <20}: {urls_obj.removed_count}')
    print(f'{"URLs redirected": <20}: {urls_obj.success_count}')
    print(f'{"Redirection failed": <20}: {urls_obj.failed_count}')
