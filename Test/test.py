
import requests
from fake_useragent import UserAgent
from lxml import html

url = 'https://panel-empresarial.institutofomentomurcia.es/IFM-panel-directorio/directorio/listado.listado.pager/1'
headers = {
    'User-Agent': UserAgent().random
}
xpath = '//*[@id="sectorActividad"]/*[@selected]/text()'
session = requests.Session()
site_session = 'BB892798DEA696B90FA1DA104E1B120B'
cookie = {'domain': 'panel-empresarial.institutofomentomurcia.es', 'name': 'JSESSIONID', 'path': '/IFM-panel-directorio', 'value': site_session}
session.cookies.set(**cookie)

def parse(session, url, headers, xpath):
    api = session.get(url=url, headers=headers)
    print(api.text)
    tree = html.document_fromstring(api.text)
    response = tree.xpath(xpath)
    print(response)

parse(session, url, headers, xpath)