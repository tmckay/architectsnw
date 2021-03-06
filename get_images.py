"""
Given a plan on architectsnw.com, this script opens all associated
images in a browser tab. This is because the plan page displays images
in a slideshow with no controls, so it's difficult to see all the images.
"""
import argparse
import logging
import os
import re
import sys
import tempfile
from typing import List
from urllib.request import urlopen, urlretrieve
from urllib.parse import urlparse
import webbrowser
from xml.dom import minidom


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    # e.g. https://www.architectsnw.com/plans/detailedplaninfo.cfm?PlanId=1053
    parser.add_argument('plan', help='The full URL to the plan on architectsnw.com')
    parser.add_argument('--download', default=False, action='store_true')
    parser.add_argument('--debug', default=False, action='store_true')
    return parser.parse_args()


def get_logger(debug: bool = False) -> logging.Logger:
    level = logging.INFO
    if debug:
        level = logging.DEBUG
    logger = logging.getLogger()
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    logger.addHandler(handler)
    return logger


def get_plan_id_from_url(url: str) -> str:
    # match just plan ID
    plan_id_match = re.match(r'([0-9]+)', url)
    # or if given full URL
    full_url_match = re.match(r'https://.+PlanId=([0-9]+)', url)

    match = plan_id_match if plan_id_match else full_url_match

    plan_id = match.groups(1)[0]
    return plan_id


def get_photo_xml(plan_id: str) -> str:
    photo_xml_url = f'https://www.architectsnw.com/assets/photoXML/{plan_id}.xml'

    logging.debug(f'Downloading photo XML from {photo_xml_url}')
    with urlopen(photo_xml_url) as fh:
        photo_xml = fh.read().decode('utf-8')
    return photo_xml


def get_img_urls_from_xml(photo_xml: str) -> List[str]:

    # fix parse error where & is unescaped
    photo_xml = photo_xml.replace('&', '&amp;')

    dom = minidom.parseString(photo_xml)

    elms = dom.getElementsByTagName('album')

    large_path = elms[0].getAttribute('lgpath')

    if not large_path.startswith('http'):
        large_path = 'https://www.architectsnw.com/' + large_path

    imgs = dom.getElementsByTagName('img')

    img_urls = []
    for img in imgs:
       img_urls.append(large_path + img.getAttribute('src'))

    return img_urls


def open_imgs_in_browser(img_urls: List[str]):
    for url in img_urls:
        webbrowser.open_new_tab(url)


def download_imgs(img_urls: List[str]) -> str:
    """Downloads imgs into a temporary directory and returns directory name"""
    tmp_dir = tempfile.mkdtemp()

    for img_url in img_urls:
        leaf_name = urlparse(img_url).path.split('/')[-1]
        local_path = os.path.join(tmp_dir, leaf_name)
        urlretrieve(img_url, filename=local_path)

    return tmp_dir


def main():
    args = parse_args()
    logger = get_logger(args.debug)

    plan_id = get_plan_id_from_url(args.plan)
    logger.debug(f'Found plan ID {plan_id}')

    photo_xml = get_photo_xml(plan_id)

    img_urls = get_img_urls_from_xml(photo_xml)

    if args.download:
        print(download_imgs(img_urls))
    else:
        open_imgs_in_browser(img_urls)


if __name__ == '__main__':
    main()
