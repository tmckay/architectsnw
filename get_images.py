import re
import sys
from urllib.request import urlopen
import webbrowser
from xml.dom import minidom

# e.g. https://www.architectsnw.com/plans/detailedplaninfo.cfm?PlanId=1053
image_path = sys.argv[1]

match = re.match(r'https://.+PlanId=([0-9]+)', image_path)

plan_id = match.groups(1)[0]

print(f'Found plan ID {plan_id}')

photo_xml_url = f'https://www.architectsnw.com/assets/photoXML/{plan_id}.xml'

with urlopen(photo_xml_url) as fh:
    photo_xml = fh.read().decode('utf-8')

dom = minidom.parseString(photo_xml)

elms = dom.getElementsByTagName('album')

large_path = elms[0].getAttribute('lgpath')

if not large_path.startswith('https'):
    large_path = 'https://www.architectsnw.com/' + large_path

imgs = dom.getElementsByTagName('img')

img_urls = []
for img in imgs:
   img_urls.append(large_path + img.getAttribute('src'))

for url in img_urls:
    webbrowser.open_new_tab(url) 
