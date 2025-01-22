import re
import json
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://developer.mozilla.org"
URL_ELEMENTS = "https://developer.mozilla.org/en-US/docs/Web/HTML/Element"


def scrape():
    html_elements = defaultdict(lambda: {})
    _scrape_elements(html_elements)
    return html_elements


def _scrape_elements(html_elements: dict) -> None:
    # loads the "HTML elements reference" page
    request = requests.get(URL_ELEMENTS)
    soup = BeautifulSoup(request.content, "html.parser")

    html_elements["*"]["attributes"] = {}

    global_attributes_container = soup.find(id="sidebar-quicklinks").find('summary', string="Global attributes").find_parent()

    # loops through the listed global attributes in the sidebar
    for li in global_attributes_container.find_all('li'):
        is_experimental = bool(li.select_one(".icon.icon-experimental"))
        html_elements["*"]["attributes"][li.find('a').text] = {
            "experimental": is_experimental
        }

    html_elements_container = soup.find(id="sidebar-quicklinks").find('summary', string="HTML elements").find_parent()

    # loops through the listed html elements in the sidebar
    for li in html_elements_container.find_all('li'):
        # loads the element reference page
        request = requests.get(BASE_URL + li.find('a').get('href'))
        soup = BeautifulSoup(request.content, "html.parser")

        element_name = li.find('a').text.strip().lstrip("<").rstrip(">")
        is_deprecated = bool(soup.select_one('.section-content > .notecard.deprecated'))
        is_experimental = bool(soup.select_one('.section-content > .notecard.experimental'))

        html_elements[element_name]["deprecated"] = is_deprecated
        html_elements[element_name]["experimental"] = is_experimental
        html_elements[element_name]["attributes"] = {}

        # here we are looking for <section> elements with the "aria-labelledby" attribute value starting with "attributes"
        # (that's to support pages where the attributes are documented using more than one container)
        supported_attributes_containers = soup.find_all("section", attrs={"aria-labelledby": re.compile(r'attributes')})

        # loops through all <section> elements we found
        for supported_attributes_container in supported_attributes_containers:
            # we are not scraping non-standard attributes for now
            if "non-standard_attributes" in supported_attributes_container["aria-labelledby"]:
                continue

            # scrapes data for each attribute
            for attribute in supported_attributes_container.select(".section-content > dl > dt"):
                attribute_name = attribute.select_one('a code').text
                html_elements[element_name]["attributes"][attribute_name] = {
                    "deprecated": bool(attribute.select_one('.icon.icon-deprecated')),
                    "experimental": bool(attribute.select_one('.icon.icon-experimental'))
                }

       # the heading elements don't have a separate page for each element (only the "h1" element is referenced in the sidebar)
        if element_name == "h1":
            # duplicates the data we found for the "h1" element for other heading elements
            for element_name in ["h2", "h3", "h4", "h5", "h6"]:
                html_elements[element_name] = html_elements["h1"]


def save_as_json(html_elements: dict) -> None:
    with open("html-elements.json", "w") as f:
        json.dump(html_elements, f, indent=4)


if __name__ == "__main__":
    elements = scrape()
    save_as_json(elements)
