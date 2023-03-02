
import requests
from fake_useragent import UserAgent
from lxml import html
from random import randint as rint

hrefs = ["/IFM-panel-directorio/directorio/view/64", "/IFM-panel-directorio/directorio/view/21467", "/IFM-panel-directorio/directorio/view/20609", "/IFM-panel-directorio/directorio/view/29358", "/IFM-panel-directorio/directorio/view/3093", "/IFM-panel-directorio/directorio/view/39650", "/IFM-panel-directorio/directorio/view/4957", "/IFM-panel-directorio/directorio/view/44867", "/IFM-panel-directorio/directorio/view/43222", "/IFM-panel-directorio/directorio/view/8002", "/IFM-panel-directorio/directorio/view/99967", "/IFM-panel-directorio/directorio/view/89374", "/IFM-panel-directorio/directorio/view/24211", "/IFM-panel-directorio/directorio/view/58116", "/IFM-panel-directorio/directorio/view/54888", "/IFM-panel-directorio/directorio/view/89203", "/IFM-panel-directorio/directorio/view/60056", "/IFM-panel-directorio/directorio/view/46321", "/IFM-panel-directorio/directorio/view/88553", "/IFM-panel-directorio/directorio/view/61292", "/IFM-panel-directorio/directorio/view/61096", "/IFM-panel-directorio/directorio/view/54324", "/IFM-panel-directorio/directorio/view/52991", "/IFM-panel-directorio/directorio/view/89142", "/IFM-panel-directorio/directorio/view/66447", "/IFM-panel-directorio/directorio/view/20606", "/IFM-panel-directorio/directorio/view/100034", "/IFM-panel-directorio/directorio/view/98288", "/IFM-panel-directorio/directorio/view/89107", "/IFM-panel-directorio/directorio/view/34563", "/IFM-panel-directorio/directorio/view/54373", "/IFM-panel-directorio/directorio/view/55430", "/IFM-panel-directorio/directorio/view/96744", "/IFM-panel-directorio/directorio/view/54458", "/IFM-panel-directorio/directorio/view/54417", "/IFM-panel-directorio/directorio/view/75533", "/IFM-panel-directorio/directorio/view/32886", "/IFM-panel-directorio/directorio/view/77458", "/IFM-panel-directorio/directorio/view/98802", "/IFM-panel-directorio/directorio/view/77099"]
urls = [f'https://panel-empresarial.institutofomentomurcia.es{href}' for href in hrefs]

headers = {
    'User-Agent': UserAgent().random
}
xpath = '//div[@class="container detail container-width"]/div[14]//div[2]/text()'
session = requests.Session()
#site_session = 'BB892798DEA696B90FA1DA104E1B120B'
#cookie = {'domain': 'panel-empresarial.institutofomentomurcia.es', 'name': 'JSESSIONID', 'path': '/IFM-panel-directorio', 'value': site_session}
#session.cookies.set(**cookie)

def parse(session, urls, headers, xpath):
    for url in urls:
        api = session.get(url=url, headers=headers)
        #print(api.text)
        tree = html.document_fromstring(api.text)
        response = tree.xpath(xpath)
        print(response)

parse(session, urls, headers, xpath)