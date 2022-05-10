import json
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

URL_ELEMENTS = "https://developer.mozilla.org/en-US/docs/Web/HTML/Element"
URL_ATTRIBUTES = "https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes"


def scrape():
    elements = defaultdict(list)
    _scrape_elements(elements)
    _scrape_attributes(elements)
    return elements


def _scrape_elements(elements: dict) -> None:
    r = requests.get(URL_ELEMENTS)
    soup = BeautifulSoup(r.content, "html.parser")

    for table in soup.find_all("table"):
        for tr in table.find_all("tr")[1:]:
            td = tr.find_all("td")[0]
            for e in td.text.split(","):
                element = e.strip().lstrip("<").rstrip(">")
                elements[element]  # create a key in the dict


def _scrape_attributes(elements: dict) -> None:
    r = requests.get(URL_ATTRIBUTES)
    soup = BeautifulSoup(r.content, "html.parser")

    for table in soup.find_all("table"):
        for tr in table.find_all("tr")[1:]:
            td1, td2, _ = tr.find_all("td")
            attr = td1.find_next("code").text
            for e in td2.text.split(","):
                element = e.strip().lstrip("<").rstrip(">")
                elements[element].append(attr)

    elements["*"] = elements["Global attribute"]
    del elements["Global attribute"]


def save_as_json(elements: dict) -> None:
    with open("html-elements.json", "w") as f:
        result = sorted(elements.keys())
        json.dump(result, f, indent=4)
    with open("html-elements-attributes.json", "w") as f:
        result = dict(sorted(elements.items()))
        json.dump(result, f, indent=4)


if __name__ == "__main__":
    elements = scrape()
    save_as_json(elements)
