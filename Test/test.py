
import requests
from fake_useragent import UserAgent
from lxml import html

url = 'https://panel-empresarial.institutofomentomurcia.es/IFM-panel-directorio/directorio/view/97759'
headers = {
    'User-Agent': UserAgent().random
}
xpath = '/html/body/div[2]/div/div[6]/div[1]/div[2]'

api = requests.get(url, headers)
tree = html.document_fromstring(api.text)
response = tree.xpath(xpath)
print(response)

response = [' BODEGAS Y VIÑEDOS DEL MEDITERRANEO, S.L.\n']
txt = str(response)[2:-2]
print(str(txt))
print(txt.rstrip())