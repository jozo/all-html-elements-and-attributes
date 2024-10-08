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
    # loads the "HTML element reference" page
    request = requests.get(URL_ELEMENTS)
    soup = BeautifulSoup(request.content, "html.parser")

    sidebar = soup.find(id="sidebar-quicklinks").find('summary', string="HTML elements").find_parent()

    # loops through the listed elements in the sidebar
    for li in sidebar.find_all('li'):
        # loads the element reference page
        request = requests.get(BASE_URL + li.find('a').get('href'))
        soup = BeautifulSoup(request.content, "html.parser")

        element_name = li.find('a').text.strip().lstrip("<").rstrip(">")
        is_deprecated = soup.select_one('.section-content > .notecard.deprecated')
        is_experimental = soup.select_one('.section-content > .notecard.experimental')

        html_elements[element_name]["deprecated"] = bool(is_deprecated)
        html_elements[element_name]["experimental"] = bool(is_experimental)
        html_elements[element_name]["attributes"] = {}

        supported_attributes_container = soup.find("section", attrs={"aria-labelledby": "attributes"})
        deprecated_attributes_container = soup.find("section", attrs={"aria-labelledby": "deprecated_attributes"})

        if supported_attributes_container:
            for attribute in supported_attributes_container.select(".section-content > dl > dt"):
                if attribute.select_one('a code'):
                    attribute_name = attribute.select_one('a code').text
                    html_elements[element_name]["attributes"][attribute_name] = {
                        "deprecated": False,
                        "experimental": bool(attribute.select_one('.icon.icon-experimental'))
                    }

        if deprecated_attributes_container:
            for attribute in deprecated_attributes_container.select(".section-content > dl > dt"):
                if attribute.select_one('a code'):
                    attribute_name = attribute.select_one('a code').text
                    html_elements[element_name]["attributes"][attribute_name] = {
                        "deprecated": True,
                        "experimental": False
                    }

def save_as_json(html_elements: dict) -> None:
    with open("html-elements.json", "w") as f:
        json.dump(html_elements, f, indent=4)


if __name__ == "__main__":
    elements = scrape()
    save_as_json(elements)
