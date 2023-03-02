
# Imports
import logging
import requests
from lxml import html
from fake_useragent import UserAgent
from configparser import ConfigParser
import csv, json


# Global vars
config = ConfigParser()
config.read('config.ini')

# Global funcs
def parse(session: requests.Session, url: str, headers: dict, xpathes: dict) -> dict:
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
    def parsing():
        for activity in activities:
            activity.main()

    def main(self):
        self.start()
        self.parsing()


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
        with open('data/data.csv', 'w', encoding='windows-1252', newline='') as csvfile:
            csvfile = csv.writer(csvfile)
            sections = ['activity', 'link'] + [section for section in config['COMPANY']]
            csvfile.writerow(sections)
        logger.info('data.csv was created successfully')

    @staticmethod
    def preparation_datajson():
        data = {'companies_href': []}
        with open('data/data.json', 'w') as datajson:
            json.dump(data, datajson)



class Activity():
    def __init__(self, name: str, site_session: str = None):
        self.name = name
        self.site_session = site_session

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
            if self.site_session != None:
                cookie = {'domain': 'panel-empresarial.institutofomentomurcia.es', 'name': 'JSESSIONID', 'path': '/IFM-panel-directorio', 'value': self.site_session}
                session.cookies.set(**cookie)
                logger.info('agro-cult was initialized')
            else: logger.info('industry was initialized')
            pages = parse(session=session, url=f'{url}1', headers=headers, xpathes={'pages': config['PARSE']['pages_xpath']})['pages'][0].split(' ')[-1]


            logger.info('start parsing...')
            for page in pages:
                try:
                    response = parse(session=session, url=f'{url}{page}', headers=headers, xpathes=xpathes)
                    if len(response['companies_href']) == 0: raise Exception
                    with open('data/data.json', 'r') as datajson:
                        data = json.load(datajson)
                    data['companies_href'] += response['companies_href']
                    with open('data/data.json', 'w') as datajson:
                        json.dump(data, datajson)

                    logger.info(f'{page}th page was parsed succesfully')
                except Exception as ex:
                    logger.error(f'error parsing in {page}th page. Error: {ex}')
            else: logger.info('companies href was parsed')

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
        for href in data['companies_href']:
            with requests.Session() as session:
                response = parse(session=session, url=f'{url}{href}', headers=headers, xpathes=xpathes)
                req = self.check_for_req(response=response)
                response = transform(response=response)
                response['activity'] = self.name
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


    def main(self):
        self.parse_companies_href()
        self.parse_companies_info()


# Main
def main():
    global activities
    activities = [Activity('Industrial'), Activity('Agro-culture', config['PARSE']['site_session'])]

    dp = Dispatcher()
    dp.main()
    logger.info('! FINISHED !')

if __name__ == '__main__':
    main()