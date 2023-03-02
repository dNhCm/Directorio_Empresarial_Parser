
# Imports
import logging, os
import requests
from lxml import html
from fake_useragent import UserAgent
from configparser import ConfigParser
import csv, json


# Global vars
config = ConfigParser()
config.read('config.ini')

# Global funcs
def parse(session: requests.Session, url: str, headers: dict, xpathes: dict[str: str]) -> dict[str: list[str]]:
    answer = {section: [] for section in xpathes}

    api = session.get(url=url, headers=headers)
    tree = html.document_fromstring(api.text)
    for section in xpathes:
        response = tree.xpath(xpathes[section])
        answer[section] += response

    return answer


def transform(response: dict[str: list[str]]) -> dict[str: str]:
    for section in response:
        if not len(response[section]) == 0:
            response[section] = response[section][0]
        else: response[section] = ''

    return response

# Tech Classes

class Dispatcher:
    @staticmethod
    def start():
        System.logging()
        System.preparation_csvfile()
        System.preparation_datajson()

    @staticmethod
    def working_on():
        Activity.init_site_session()
        UI.main()

    def main(self):
        self.start()
        self.working_on()


class System:
    @staticmethod
    def logging():
        global logger

        logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
        )

    @staticmethod
    def preparation_csvfile():
        if not os.path.isfile('data/data.csv'):
            with open('data/data.csv', 'w', encoding='windows-1252', newline='') as csvfile:
                csvfile = csv.writer(csvfile)
                sections = ['activity', 'link'] + [section for section in config['COMPANY']]
                csvfile.writerow(sections)
            logger.info('data.csv was created successfully')

    @staticmethod
    def preparation_datajson():
        if not os.path.isfile('data/data.json'):
            data = {'last_panel_page': {}, 'companies_href': {}}
            with open('data/data.json', 'w') as datajson:
                json.dump(data, datajson)

    @staticmethod
    def delete_cache():
        os.remove(path='data/data.json')
        System.preparation_datajson()


class UI:
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
    def web(self):
        self.task = int(input(
'''\nКакое задание сейчас выберете:
Спарсить href - 1
Спарсить info - 2
Очистить кэш - 3
Выйти - 4

Ваш Ответ: '''
        ))

    @classmethod
    def main(self):
        while True:
            self.web()
            if self.task == 1: self.parse_companies_href()
            elif self.task == 2: self.parse_companies_info()
            elif self.task == 3: self.delete_cache()
            else: break


class Activity:
    @classmethod
    def init_site_session(self):
        self.site_session = config['PARSE']['site_session']

    @classmethod
    def parse_companies_href(self):
        logger.info('preparating to parsing companies href')
        url = config['PARSE']['url']
        headers = {
            'User-Agent': UserAgent().random
        }
        xpathes = {'companies_href': config['PARSE']['company_xpath']}
        logger.info('preparating was finished successfully')

        with requests.Session() as session:
            logger.info('session was created')
            cookie = {'domain': 'panel-empresarial.institutofomentomurcia.es', 'name': 'JSESSIONID', 'path': '/IFM-panel-directorio', 'value': self.site_session}
            session.cookies.set(**cookie)
            logger.info('logged in was successful')

            activity = parse(session=session, url=f'{url}1', headers=headers, xpathes={'activity': config['PARSE']['activity_xpath']})['activity'][0]
            try:
                with open('data/data.json', 'r') as datajson:
                    last_page = json.load(datajson)['last_panel_page'][activity]
            except Exception as ex:
                last_page = 1
                logger.error(f'may be no last page.. Error: {ex}')

            page = last_page
            errors = 0
            logger.info('start parsing...')
            while errors < 2:
                try:
                    response = parse(session=session, url=f'{url}{page}', headers=headers, xpathes=xpathes)
                    if len(response['companies_href']) == 0: raise Exception
                    with open('data/data.json', 'r') as datajson:
                        data = json.load(datajson)
                    try: data['companies_href'][activity] += response['companies_href']
                    except: data['companies_href'][activity] = response['companies_href']
                    data['last_panel_page'][activity] = page
                    with open('data/data.json', 'w') as datajson:
                        json.dump(data, datajson)
                    errors = 0
                    logger.info(f'{page}th page was parsed succesfully')
                except Exception as ex:
                    errors += 1
                    logger.error(f'error parsing in {page}th page. Error: {ex}')
                finally: page += 100
            else: logger.info('companies href was parsed')

    @classmethod
    def parse_companies_info(self):
        logger.info('preparating to parsing companies info')
        url = config['PARSE']['main_url']
        headers = {
            'User-Agent': UserAgent().random
        }
        xpathes = {section: config['COMPANY'][section] for section in config['COMPANY']}
        with open('data/data.json', 'r') as datajson:
            data = json.load(datajson)
        sections = ['activity', 'link'] + [section for section in config['COMPANY']]
        logger.info('preparating was finished successfully')
        
        logger.info('start to parsing href`s')
        for activity in data['companies_href']:
            for href in data['companies_href'][activity]:
                with requests.Session() as session:
                    response = parse(session=session, url=f'{url}{href}', headers=headers, xpathes=xpathes)
                    req = self.check_for_req(response=response)
                    response = transform(response=response)
                    response['activity'] = activity
                    response['link'] = f'{url}{href}'
                    if req:
                        with open('data/data.csv', 'a', encoding='windows-1252', newline='') as csvfile:
                            csvfile = csv.DictWriter(csvfile, fieldnames=sections)
                            csvfile.writerow(response)
                    else: logger.info(f'doesnt intresting in {href}')
                logger.info(f'parsed {href} href')
            logger.info(f'parsed all of href')

    @staticmethod
    def check_for_req(response: dict[str: list[str]]) -> bool:
        req = config['PRIORITY']['req'].split(' ')

        for section in response:
            if section == req:
                if len(response[section]) == 0: return False
        else: return True


# Main
def main():
    dp = Dispatcher()
    dp.main()
    logger.info('\033[34m\033[43m\033[1m💙💛 Слава Україні! 💙💛\033[0m')

if __name__ == '__main__':
    main()