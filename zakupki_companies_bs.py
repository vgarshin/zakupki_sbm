import sys
import json
import os
import pandas as pd
import smtplib as smtp
import socket
import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
from random import randint
from time import sleep
from pandas.io.json import json_normalize

MIN_TIME_SLEEP = 1
MAX_TIME_SLEEP = 15
RNUM_START = 19100000 #19119831
RNUM_END   = 19200000 #19122000
TIMEOUT = 10
MAX_COUNTS = 5

def get_start_index(directory):
    return len(os.listdir(directory))
def get_html(url_page, timeout):
    counts = 0
    html = 'empty_page'
    while counts < MAX_COUNTS:
        try:
            html = urlopen(url_page, timeout=timeout)
            break
        except urllib.request.URLError as e:
            counts += 1
            print('URLError | ', url_page, ' | ', e, ' | counts: ', counts)
            sleep(randint(MIN_TIME_SLEEP, MAX_TIME_SLEEP))
        except urllib.request.HTTPError as e:
            counts += 1
            print('HTTPError | ', url_page, ' | ', e, ' | counts: ', counts)
            sleep(randint(MIN_TIME_SLEEP, MAX_TIME_SLEEP))
        except socket.timeout as e:
            counts += 1
            print('socket timeout | ', url_page, ' | ', e, ' | counts: ', counts)
            sleep(randint(MIN_TIME_SLEEP, MAX_TIME_SLEEP))
    return html
def get_data_dict(data):
    data_dict = {}
    for x in data:
        if len(x) == 2:
            data_dict.update({x[0]: x[1]})
        elif len(x) == 1:
            data_dict.update({x[0]: 1})
        else:
            if x:
                print('error dict field: ', x)
            pass
    return data_dict
def get_dataframe(directory):
    files = [os.path.join(directory, file) for file in os.listdir(directory)]
    print('found {} files, creating dataframe...'.format(len(files)))
    df = pd.DataFrame()
    for file_load in files:
        with open(file_load) as file:
            data_json = json.load(file)
        df = df.append(json_normalize(data_json, sep='_'))
    df = df.reset_index()
    del df['index']
    return df
def send_mail(dest_email, email_text):
    error = []
    try:
        email = 'app.notifications@yandex.ru'
        password = 'Notify2019'
        subject = 'Data load notification'
        message = 'From: {}\nTo: {}\nSubject: {}\n\n{}'.format(email, dest_email, subject, email_text)
        server = smtp.SMTP_SSL('smtp.yandex.com')
        server.login(email, password)
        server.auth_plain()
        server.sendmail(email, dest_email, message)
        server.quit()
    except smtp.SMTPException as e:
        error.append(e)
    return error
def main():
    url_main = 'http://zakupki.gov.ru/epz/eruz/card/general-information.html?reestrNumber='
    print('url: ', url_main)
    path = '{}/'.format(sys.argv[1])
    print('got path to save data: ', path)
    table_name = '{}zakupki_scraping_smb_{}.csv'.format(path, str(sys.argv[2]))
    print('got date: ', str(sys.argv[2]), ' | table name: ', table_name)
    directory = '{}/'.format(sys.argv[3])
    print('got directory for cache: ', directory)
    dest_email = sys.argv[4]
    print('got email for notifications: ', dest_email)
    count_trial = 0
    flag = True
    while flag:
        try:
            start_index = get_start_index(directory)
            print('trial: ', count_trial, ' | start index: ', start_index)
            for reestr_num in range(RNUM_START + start_index, RNUM_END + 1):
                data = []
                url = '{}{}'.format(url_main, str(reestr_num))
                html_i = get_html(url, TIMEOUT)
                soup_i = BeautifulSoup(html_i, 'html.parser')
                try:
                    for part in soup_i.find_all('div', {'class': 'noticeTabBoxWrapper no-top-border'}):
                        table = part.find('table')
                        for row in table.find_all('tr'):
                            cols = row.find_all('td')
                            cols = [' '.join(x.text.split()) for x in cols]
                            data.append([x for x in cols if x])
                except:
                    print('not found reestr_num: ', reestr_num)
                data_dict = get_data_dict(data)
                filename = '{}batch_reestr_num_{}.txt'.format(directory, str(reestr_num))
                with open(filename, 'w') as file:
                    json.dump(data_dict, file)
                sleep(randint(MIN_TIME_SLEEP, MAX_TIME_SLEEP) / MAX_TIME_SLEEP)
            flag = False
        except BaseException as e:
            print('BaseException main cycle | ', e)
            count_trial += 1
            sleep(randint(MIN_TIME_SLEEP, MAX_TIME_SLEEP))
            flag = True
    print('data collected, saved to json files to folder: {}'.format(directory))
    df = get_dataframe(directory)
    print('data frame created of shape: ', df.shape)
    df.to_csv(table_name)
    print('saved to file: ', table_name)
    email_text = 'Data collected, table {} created'.format(table_name)
    error_mail = send_mail(dest_email, email_text)
    if error_mail:
        print('email was not sent to: {} | error: {}'.format(dest_email, error_mail))
    else:
        print('email was sent to: ', dest_email)

if __name__ == '__main__':
    main()