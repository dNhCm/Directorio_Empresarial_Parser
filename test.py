
import requests
from fake_useragent import UserAgent
from lxml import html

url = 'https://panel-empresarial.institutofomentomurcia.es/IFM-panel-directorio/directorio/view/97759'
headers = {
    'User-Agent': UserAgent().random
}
xpath = '//div[@class="container detail container-width"]//div[@class="col-6"]/text()'

api = requests.get(url, headers)
tree = html.document_fromstring(api.text)
response = tree.xpath(xpath)
print(response)