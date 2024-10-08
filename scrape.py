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

        element = li.find('a').text.strip().lstrip("<").rstrip(">")
        isDeprecated = soup.select_one('.section-content > .notecard.deprecated')
        isExperimental = soup.select_one('.section-content > .notecard.experimental')

        html_elements[element]["deprecated"] = bool(isDeprecated)
        html_elements[element]["experimental"] = bool(isExperimental)
        html_elements[element]["attributes"] = []

        supportedAttributesContainer = soup.find("section", attrs={"aria-labelledby": "attributes"})
        deprecatedAttributesContainer = soup.find("section", attrs={"aria-labelledby": "deprecated_attributes"})

        if supportedAttributesContainer:
            for attribute in supportedAttributesContainer.select(".section-content > dl > dt"):
                if attribute.select_one('a code'):
                    html_elements[element]["attributes"].append({
                        "name": attribute.select_one('a code').text,
                        "deprecated": False,
                        "experimental": bool(attribute.select_one('.icon.icon-experimental'))
                    })

        if deprecatedAttributesContainer:
            for attribute in deprecatedAttributesContainer.select(".section-content > dl > dt"):
                if attribute.select_one('a code'):
                    html_elements[element]["attributes"].append({
                        "name": attribute.select_one('a code').text,
                        "deprecated": True,
                        "experimental": False
                    })

def save_as_json(html_elements: dict) -> None:
    with open("html-elements.json", "w") as f:
        json.dump(html_elements, f, indent=4)


if __name__ == "__main__":
    elements = scrape()
    save_as_json(elements)
