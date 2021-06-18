import argparse
import logging
import re
import sys
from urllib.request import urlopen
import webbrowser
from xml.dom import minidom


def main():
    parser = argparse.ArgumentParser()
    # e.g. https://www.architectsnw.com/plans/detailedplaninfo.cfm?PlanId=1053
    parser.add_argument('plan')
    parser.add_argument('--debug', default=False, action='store_true') 
    args = parser.parse_args()

    level = logging.INFO
    if args.debug:
        level = logging.DEBUG
    logger = logging.getLogger()
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    logger.addHandler(handler)

    plan_id_match = re.match(r'([0-9]+)', args.plan)
    full_url_match = re.match(r'https://.+PlanId=([0-9]+)', args.plan)

    match = plan_id_match if plan_id_match else full_url_match

    plan_id = match.groups(1)[0]

    logger.debug(f'Found plan ID {plan_id}')

    photo_xml_url = f'https://www.architectsnw.com/assets/photoXML/{plan_id}.xml'

    logging.debug(f'Downloading photo XML from {photo_xml_url}')
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


if __name__ == '__main__':
    main()
