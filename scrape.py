import json
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

URL_ELEMENTS = "https://developer.mozilla.org/en-US/docs/Web/HTML/Element"
URL_ATTRIBUTES = "https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes"


def scrape():
    html_elements = defaultdict(list)
    _scrape_elements(html_elements)
    _scrape_attributes(html_elements)
    return html_elements


def _scrape_elements(html_elements: dict) -> None:
    r = requests.get(URL_ELEMENTS)
    soup = BeautifulSoup(r.content, "html.parser")

    for table in soup.find_all("table"):
        for tr in table.find_all("tr")[1:]:
            td = tr.find_all("td")[0]
            for e in td.text.split(","):
                element = e.strip().lstrip("<").rstrip(">")
                html_elements[element]  # create a key in the dict


def _scrape_attributes(html_elements: dict) -> None:
    r = requests.get(URL_ATTRIBUTES)
    soup = BeautifulSoup(r.content, "html.parser")

    for table in soup.find_all("table"):
        for tr in table.find_all("tr")[1:]:
            td1, td2, _ = tr.find_all("td")
            attr = td1.find_next("code").text
            for e in td2.text.split(","):
                element = e.strip().lstrip("<").rstrip(">")
                html_elements[element].append(attr)

    html_elements["*"] = html_elements["Global attribute"]
    del html_elements["Global attribute"]


def save_as_json(html_elements: dict) -> None:
    with open("html-elements.json", "w") as f:
        sorted_elements = sorted(html_elements.keys())
        json.dump(sorted_elements, f, indent=4)
    with open("html-elements-attributes.json", "w") as f:
        sorted_elements = dict(sorted(html_elements.items()))
        json.dump(sorted_elements, f, indent=4)


if __name__ == "__main__":
    elements = scrape()
    save_as_json(elements)
