import pyperclip
from requests.utils import urlparse
from ping import Ping
from urls import Urls
from collections import defaultdict
import time
import logging
import os
from datetime import datetime
from mylogging import log_setup
import json

from processors import (
    create_file_if_not_exist,
    is_status_code_ok,
    get_domains,
    remove_prefix,
    terminate,
)
from configuration import FORMATTED_OUTPUT, FORMATTER_TIMES, FORMATTER_CHAR, SLEEP_FOR, CACHE, colorful_site_names, positives, negatives

os.system('color')

# set up logging configuration
log_setup()
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    print(f'\n{" Copy the links... ":-^60}')
    pyperclip.copy("")
    clipboard_content = pyperclip.waitForNewPaste()
    urls_obj = Urls(clipboard_content)

    logger.info("URLs found...")

    while True:
        choice = input("Do you want to add more URLs? (Y/n): ")
        if choice.lower() in positives:
            print(f'\n{" Copy the links... ":-^60}')
            pyperclip.copy("")
            clipboard_content = pyperclip.waitForNewPaste()
            urls_obj.add_more_urls(clipboard_content)
        else:
            break

    src_dest_urls = urls_obj.getSrcDestURLs()

    # the src_des_urls will be None if less than 2 valid urls supplied or paired urls not found
    if not src_dest_urls:
        logger.critical(
            "Valid URLs found were less than 2 or not enough to generate one-to-one pair")
        if os.path.exists(CACHE):
            logger.warning(
                "Found data from previous run, please check if this needs to be restored")
            with open(CACHE, "r") as cache:
                data = json.load(cache)
            print(data[0][0], data[0][1], sep=" |-> ", end="\n...\n..\n.\n")
            choice = input("Do you want to load the data? (Y/n): ")
            while True:
                if choice.lower() in positives:
                    urls_obj.setSrcDestURLs(data)
                    src_dest_urls = urls_obj.getSrcDestURLs()
                    break
                if choice.lower() in negatives:
                    terminate()
                else:
                    choice = input("Please use Y/n.. ")
    else:
        with open(CACHE, "w") as cache:
            json.dump(src_dest_urls, cache, indent=2)

    ping = Ping()

    logger.info("Running check for DESTINATION URLs")

    status_codes_to_urls = ping.getStatusCodeOfURLs(
        map(lambda x: x[1], src_dest_urls))  # Passing destination URLs

    print(f"\n{' Running destination URLs verification... ':{FORMATTER_CHAR}^{FORMATTER_TIMES}}")
    """
    Below code pings to url and check their status codes also verifies if reverse redirection is present to avoid
    infinite redirection. If destination url is further redirecting it will alert the same
    """
    bad_urls: list[tuple] = []
    for (from_url, to_url), status_code in zip(src_dest_urls, status_codes_to_urls):
        # To slow down the program for readability of outputs
        time.sleep(SLEEP_FOR)
        # print(to_url, status_code) # debug print
        if from_url == to_url:
            logger.warning(f'{from_url} == {to_url}')
            continue

        if not is_status_code_ok(to_url=to_url, status_code=status_code):
            to_final_url = ping.get_URL(to_url)
            if to_final_url == from_url or to_final_url.rstrip('/') == from_url.rstrip('/'):
                logger.warning(
                    f"Destination URL is redirected to source {to_url} -> {from_url}")
                bad_urls.append((from_url, to_url))
            else:
                print(f"!!! Attention Required: {to_url}")
                logger.warning(
                    f"Destination URL is redirecting further {to_final_url}")
    # if bad_urls:
    urls_obj.remove_urls(bad_urls)
    bad_urls.clear()

    from_final_urls = ping.getFinalURLs(
        map(lambda x: x[0], src_dest_urls))  # Passing source URLs

    print(
        f"\n{' Running Pre URL validations... ':{FORMATTER_CHAR}^{FORMATTER_TIMES}}")
    for (from_url, to_url), from_final_url in zip(src_dest_urls, from_final_urls):
        # To slow down the program for readability of outputs
        time.sleep(SLEEP_FOR)

        if from_final_url == to_url or from_final_url.rstrip('/') == to_url.rstrip('/'):
            logger.warning(f"Already redirected {from_url} -> {to_url}")
            bad_urls.append((from_url, to_url))

    urls_obj.remove_urls(bad_urls)
    bad_urls.clear()

    domains_k_index = get_domains(map(lambda x: x[0], src_dest_urls))
    # print(domains_k_index.items())

    formatted_from_to_strings = defaultdict(list)
    domain_mapper = dict()
    for dom_index, (domain, index_list) in enumerate(domains_k_index.items(), start=1):
        parsed_url = urlparse(domain).netloc.split('.')
        if parsed_url[0] == 'www':
            site_name: str = parsed_url[1].capitalize()
        else:
            site_name: str = parsed_url[0].capitalize()

        domain_mapper[dom_index] = site_name

        print(f"\n{dom_index}. For {colorful_site_names.get(site_name)}")
        for i in index_list:
            src, dest = src_dest_urls[i]
            formatted_src, formatted_dest = remove_prefix(src, domain), dest
            print(formatted_src, formatted_dest)
            formatted_from_to_strings[site_name].append(
                (formatted_src, formatted_dest))
    if any(formatted_from_to_strings):
        while True:
            if len(formatted_from_to_strings) == 1:
                string = ""
                for item in formatted_from_to_strings.values():
                    for src_domainless_url, dest_url in item:
                        string += f"{src_domainless_url} {dest_url}\n"
                pyperclip.copy(string)
                print(
                    f"\n{colorful_site_names.get(domain_mapper.get(1))} copied!")
                action = input(
                    "Do you want to continue to perform post validations? (Y/n): ")
                if action.lower() in positives:
                    break
                elif action.lower() in negatives:
                    terminate()
                else:
                    continue
            choice = input("\nChoose a domain to copy formatted links: ")
            if not choice.isnumeric():
                print("Enter 0 to do post checks... ")
                continue
            choice = int(choice)
            if choice == 999 or choice == 0:
                break
            try:
                formatted_src_dest_urls: list = formatted_from_to_strings.get(
                    domain_mapper.get(choice))
                string = ""
                for src_domainless_url, dest_url in formatted_src_dest_urls:
                    string += f"{src_domainless_url} {dest_url}\n"
                pyperclip.copy(string)
                print(
                    f"\n{colorful_site_names.get(domain_mapper.get(choice))} copied!")
            except KeyboardInterrupt:
                terminate()
            except Exception as e:
                print(e)
        # Creates file for writitng console output
        create_file_if_not_exist(FORMATTED_OUTPUT)
        today = datetime.now()
        with open(FORMATTED_OUTPUT, 'a') as output_file:
            output_file.write(f"#{today.strftime('%d/%m/%Y, %H:%M:%S')}\n")
            for domain, src_dest_url in formatted_from_to_strings.items():
                output_file.write(f"[{domain}]\n")
                for src_domainless_url, dest_url in src_dest_url:
                    output_file.write(f"{src_domainless_url} {dest_url}\n")
                output_file.write('\n')

        from_final_urls = ping.getFinalURLs(
            map(lambda x: x[0], src_dest_urls))  # Passing source URLs

        print(
            f"\n{' Running Post URL validations... ':{FORMATTER_CHAR}^{FORMATTER_TIMES}}")
        for (from_url, to_url), from_final_url in zip(src_dest_urls, from_final_urls):
            # To slow down the program for readability of outputs
            time.sleep(SLEEP_FOR)

            if from_final_url == to_url or from_final_url.rstrip('/') == to_url.rstrip('/'):
                logger.info(f"Redirection pass {from_url} -> {to_url}")
                urls_obj.add_success_counter()
            else:
                logger.critical(f"Redirection failed {from_url} -> {to_url}")
                bad_urls.append((from_url, to_url))
                urls_obj.add_failure_counter()

    # Program ends, little summary section
    print(f"\n{'-'* (len(FORMATTED_OUTPUT)+13)}\nOutput file: {FORMATTED_OUTPUT}")
    print(f'\nSummary')
    print(f'{"Bad URLs removed": <20}: {urls_obj.removed_count}')
    print(f'{"URLs redirected": <20}: {urls_obj.success_count}')
    print(f'{"Redirection failed": <20}: {urls_obj.failed_count}')
    print(f'_'*23)
    print(f'{"Total URLs found": <20}: {urls_obj.total_found_urls}')
