
import logging
import os
from logging import Logger

import requests
from lxml import html
from fake_useragent import UserAgent
from configparser import ConfigParser
import csv
import json


# Global vars
config = ConfigParser()
config.read('config.ini')
logger: Logger


# Global funcs
def parse(session: requests.Session, url: str, headers: dict, xpathes: dict[str: str]) -> dict[str: list[str]]:
    """
    Just parsing url with session and headers by xpathes

    :param session:
    :param url:
    :param headers:
    :param xpathes: dict of calling of xpath and value of it
    :return: responses by calling of xpathes. For example, xpathes = {'activity': 'some_xpath'}, then return {'activity: 'response'}
    """

    answer = {section: [] for section in xpathes}

    api = session.get(url=url, headers=headers)
    tree = html.document_fromstring(api.text)
    for section in xpathes:
        response = tree.xpath(xpathes[section])
        answer[section] += response

    return answer


def transform(response: dict[str: list[str]]) -> dict[str: str]:
    """
    Format response

    :param response:
    :return: if in section by xpath no elements, then it will return empty str, but if there is elements, then return only first one.
    """

    for section in response:
        if not len(response[section]) == 0:
            response[section] = response[section][0]
        else:
            response[section] = ''

    return response


def check_for_req(response: dict[str: list[str]]) -> bool:
    """
    Checks if all required items are present

    :param response:
    :return: if the response does not contain at least one required item, it returns false, otherwise true.
    """

    req = config['PRIORITY']['req'].split(' ')
    is_there = True

    for section in response:
        if section in req:
            if len(response[section]) == 0:
                is_there = False

    return is_there


# Tech Classes

class Dispatcher:
    """
    Manager of all work
    """

    @staticmethod
    def start():
        System.logging()
        System.preparing_csvfile()
        System.preparing_json()

    @staticmethod
    def working_on():
        UI.main()

    def main(self):
        self.start()
        self.working_on()


class System:
    """
    Working with files and logging
    """

    @staticmethod
    def logging():
        global logger

        logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
        )

    @staticmethod
    def preparing_csvfile():
        # If file doesn't exist, then create a new one by template
        if not os.path.isfile('data/data.csv'):
            with open('data/data.csv', 'w', encoding='windows-1252', newline='') as csvfile:
                csvfile = csv.writer(csvfile)
                sections = ['activity', 'link'] + [section for section in config['COMPANY']]
                csvfile.writerow(sections)
            logger.info('data.csv was created successfully')

    @staticmethod
    def preparing_json():
        # If file doesn't exist, then create a new one by template
        if not os.path.isfile('data/data.json'):
            data = {'last_panel_page': {}, 'companies_href': {}}
            with open('data/data.json', 'w') as datajson:
                json.dump(data, datajson)

    @staticmethod
    def delete_cache():
        os.remove(path='data/data.json')
        System.preparing_json()


class UI:
    """
    UI for choice task
    """
    task: int  # Chosen task by user

    @staticmethod
    def parse_companies_href():
        Activity.parse_companies_href()

    @staticmethod
    def parse_companies_info():
        Activity.parse_companies_info()

    @staticmethod
    def delete_cache():
        System.delete_cache()

    @classmethod
    def choice(cls):
        cls.task = int(input('''\nКакое задание сейчас выберете:
Спарсить href - 1
Спарсить info - 2
Очистить кэш - 3
Выйти - 4

Ваш Ответ: '''))

    @classmethod
    def main(cls):
        while True:
            cls.choice()
            if cls.task == 1:
                cls.parse_companies_href()
            elif cls.task == 2:
                cls.parse_companies_info()
            elif cls.task == 3:
                cls.delete_cache()
            else:
                break


class Activity:
    """
    Parsing hrefs and info of chosen activity from site
    """

    site_session = config['PARSE']['site_session']

    @staticmethod
    def parse_companies_href():
        logger.info('preparing to parsing companies href')
        # Get data for parsing
        url = config['PARSE']['url']
        headers = {
            'User-Agent': UserAgent().random
        }
        xpathes = {'companies_href': config['PARSE']['company_xpath']}

        with requests.Session() as session:
            logger.info('session was created')
            # Work with cookies for connecting parser to your session
            cookie = {'domain': 'panel-empresarial.institutofomentomurcia.es', 'name': 'JSESSIONID', 'path': '/IFM-panel-directorio', 'value': Activity.site_session}
            session.cookies.set(**cookie)
            logger.info('logged in was successful')

            # Get current activity
            activity = parse(session=session, url=f'{url}1', headers=headers, xpathes={'activity': config['PARSE']['activity_xpath']})['activity'][0]

            # Get previous last page where parser was stopped in parsing
            try:
                with open('data/data.json', 'r') as datajson:
                    last_page = json.load(datajson)['last_panel_page'][activity]
            except Exception as ex:
                last_page = 1
                logger.error(f'may be no last page.. Error: {ex}')

            # Start to parse for companies href by pages
            page = last_page
            errors = 0
            logger.info('preparing was finished successfully')
            logger.info('start parsing...')
            while errors < 2:  # If three errors were thrown in a row then stop parsing
                try:
                    response = parse(session=session, url=f'{url}{page}', headers=headers, xpathes=xpathes)

                    # Checking if it parses no company then raise error, because page is empty
                    if len(response['companies_href']) == 0:
                        raise Exception

                    # Add our list of hrefs to companies_hrefs in data.json
                    with open('data/data.json', 'r') as datajson:
                        data = json.load(datajson)

                    try:
                        data['companies_href'][activity] += response['companies_href']
                    except NameError:
                        data['companies_href'][activity] = response['companies_href']
                    data['last_panel_page'][activity] = page

                    with open('data/data.json', 'w') as datajson:
                        json.dump(data, datajson)

                    # reset errors count, because page was parsed successfully; and log
                    errors = 0
                    logger.info(f'{page}th page was parsed successfully')
                except Exception as ex:
                    errors += 1
                    logger.error(f'error parsing in {page}th page. Error: {ex}')
                finally:  # Go to next page to parse
                    page += 1
            else:
                logger.info('companies href was parsed')

    @staticmethod
    def parse_companies_info():
        logger.info('preparing to parsing companies info')
        # Get data for parsing
        url = config['PARSE']['main_url']
        headers = {
            'User-Agent': UserAgent().random
        }
        xpathes = {section: config['COMPANY'][section] for section in config['COMPANY']}
        data = json.load(open('data/data.json', 'r'))
        sections = ['activity', 'link'] + [section for section in config['COMPANY']]
        logger.info('preparing was finished successfully')
        
        logger.info('start to parsing href\'s')
        # Parsing companies info
        for activity in data['companies_href']:  # Parse for every activity
            for href in data['companies_href'][activity]:
                with requests.Session() as session:
                    # Parsing info from href
                    response = parse(session=session, url=f'{url}{href}', headers=headers, xpathes=xpathes)

                    # Checkpoint for the presence of required items
                    req = check_for_req(response=response)

                    # Format response
                    response = transform(response=response)
                    response['activity'] = activity
                    response['link'] = f'{url}{href}'

                    # Upload our data if there are all required items; if no, then skip
                    if req:
                        with open('data/data.csv', 'a', encoding='windows-1252', newline='') as csvfile:
                            csvfile = csv.DictWriter(csvfile, fieldnames=sections)
                            csvfile.writerow(response)
                    else:
                        logger.info(f'doesnt interesting in {href}')
                        continue
                logger.info(f'parsed {href} href')
            logger.info(f'parsed all of href')


def main():
    dp = Dispatcher()
    dp.main()
    logger.info('\033[34m\033[43m\033[1m💙💛 Слава Україні! 💙💛\033[0m')


if __name__ == '__main__':
    main()
