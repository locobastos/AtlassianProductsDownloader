#!/usr/bin/env python3
# coding=utf-8

import datetime
import os
import requests
import time
import sys

from packaging import version   # "packaging" by Donald Stufft
from selenium import webdriver  # "selenium" by selenium.dev

# Download "Microsoft Edge Driver" from https://developer.microsoft.com/fr-fr/microsoft-edge/tools/webdriver/

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.select import Select


# _____FUNCTION_________________________________________________________________________________________________________

units = {
    'B': {'size': 1, 'speed': 'B/s'},
    'KB': {'size': 1024, 'speed': 'KB/s'},
    'MB': {'size': 1024 * 1024, 'speed': 'MB/s'},
    'GB': {'size': 1024 * 1024 * 1024, 'speed': 'GB/s'}
}


def check_unit(length):  # length in bytes
    if length < units['KB']['size']:
        return 'B'
    elif units['KB']['size'] <= length <= units['MB']['size']:
        return 'KB'
    elif units['MB']['size'] <= length <= units['GB']['size']:
        return 'MB'
    elif length > units['GB']['size']:
        return 'GB'


def download_file(file_url, save_directory):
    local_filename = file_url.rsplit('/', 1)[1]

    with open(os.path.join(save_directory, local_filename), 'wb') as f:
        print("Downloading: " + local_filename + "...")
        start = time.time()
        r = requests.get(url, stream=True)

        # total length in bytes of the file
        total_length = float(r.headers.get('content-length'))

        d = 0  # counter for amount downloaded

        # when file is not available
        if total_length is None:
            f.write(r.content)
        else:
            for chunk in r.iter_content(8192):
                d += float(len(chunk))
                f.write(chunk)  # writing the file in chunks of 8192 bytes
                downloaded = d / units[check_unit(d)]['size']  # amount downloaded in proper units

                # converting the unit of total length or size of file from bytes.
                tl = total_length / units[check_unit(total_length)]['size']

                trs = d // (time.time() - start)  # speed in bytes per sec
                download_speed = trs / units[check_unit(trs)]['size']  # speed in proper unit
                speed_unit = units[check_unit(trs)]['speed']  # speed in proper units
                done = 100 * d / total_length  # percentage downloaded or done.
                fmt_string = "\r%6.2f %s [%s%s] %7.2f%s  /  %4.2f %s  %7.2f %s"
                set_of_vars = (float(done), '%',
                               '*' * int(done / 2),
                               '_' * int(50 - done / 2),
                               downloaded, check_unit(d),
                               tl, check_unit(total_length),
                               download_speed, speed_unit)
                sys.stdout.write(fmt_string % set_of_vars)
                sys.stdout.flush()
            sys.stdout.write('\n')


# _____MAIN_____________________________________________________________________________________________________________

ATLASSIAN_PRODUCTS_URL = {
    'Bamboo':                         'https://www.atlassian.com/software/bamboo/download',
    'Bitbucket Server':               'https://www.atlassian.com/software/bitbucket/download-archives',
    'Confluence':                     'https://www.atlassian.com/software/confluence/download-archives',
    'Crowd':                          'https://www.atlassian.com/software/crowd/download-archive',
    'Crucible':                       'https://www.atlassian.com/software/crucible/download',
    'Fisheye':                        'https://www.atlassian.com/software/fisheye/download',
    'Jira Core Server':               'https://www.atlassian.com/software/jira/core/download',
    'Jira Service Management Server': 'https://www.atlassian.com/software/jira/service-management/download-archives',
    'Jira Software':                  'https://www.atlassian.com/software/jira/update'
}

# save_location = input("Download Atlassian products to: ")
save_location = r"U:\Atlassian"

print("Save Location set to: '" + save_location + "'")

edge_service = Service(executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedgedriver.exe")
edge_driver = webdriver.Edge(service=edge_service)

for product_name, product_url in ATLASSIAN_PRODUCTS_URL.items():
    print("-------------------------------------------------------------------------------------------------------")

    save_path = os.path.join(save_location, product_name)
    print("Saving to: '" + save_path + "'")

    if not os.path.isdir(save_path):
        os.mkdir(save_path)
        print("'" + save_path + "' created")

    os.chdir(save_path)

    edge_driver.get(product_url)
    time.sleep(5)

    # Close cookie panel
    onetrust_consent_panel = edge_driver.find_element(By.ID, "onetrust-consent-sdk")
    edge_driver.execute_script("""
        var onetrustConsentPanel = arguments[0];
        onetrustConsentPanel.parentNode.removeChild(onetrustConsentPanel);
    """, onetrust_consent_panel)

    latest_version = "0"
    try:
        for get_started_button in edge_driver.find_elements(By.ID, "get-started"):
            if version.parse(get_started_button.get_attribute('data-version')) > version.parse(latest_version):
                latest_version = get_started_button.get_attribute('data-version')
        edge_driver.find_element(By.XPATH, '//a[@id="get-started"][@data-version="' + latest_version + '"]').click()
    except NoSuchElementException:
        edge_driver.find_element(By.ID, 'downloads-button').click()

    try:
        select = Select(edge_driver.find_element(By.ID, "select-product-version"))
    except NoSuchElementException:
        select = Select(edge_driver.find_element(By.ID, "select-product-standard-version"))

    for option in select.options:
        product_description = option.get_attribute('data-file-description')
        product_release_date = datetime.datetime.strptime(option.get_attribute('data-product-release-date'), '%d-%b-%Y')
        date_formatted = "(" + str(product_release_date.year) + "-" + str(product_release_date.strftime('%m')) + ")"
        if not os.path.isdir(os.path.join(save_path, product_description + " " + date_formatted)):
            os.mkdir(os.path.join(save_path, product_description + " " + date_formatted))
            url = option.get_attribute('value')
            download_file(url, os.path.join(save_path, product_description + " " + date_formatted))
