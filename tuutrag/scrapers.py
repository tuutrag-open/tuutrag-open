# ================================================================
# path: tuutrag/scrapers.py
# brief: tuutrag module exports
# ================================================================

import time
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

driver = webdriver.Firefox()
driver.get("https://ccsds.org/publications/magentabooks/")


# Waits for data table to be populated
time.sleep(2)

# Clicks buttons to reveal metadata on each book
for idx in range(40):

    # Hovers over button that reveals metadeta
    tracker = driver.find_element(
        By.CSS_SELECTOR, f'.sorting_1.dtr-control[data-row-index="{idx}"]'
    )

    # Keeps the mouse within viewing boundary by scrolling
    tracker.location_once_scrolled_into_view

    # Moves mouse slightly North and West bound to avoid unwanted pdf event
    ActionChains(driver).move_to_element_with_offset(tracker, -1, 1).click().perform()
    time.sleep(0.5)


# Load html after all metadata has been revealed
html = driver.page_source
soup = BeautifulSoup(html)

spans = soup.select("td.child ul li span")
spans_text = [span.get_text(strip=True) for span in spans]

# Adds each book to a dictionary where the key is the book index in the list and
# the value is an array containing the metadata for each book
Magenta = {}
metadata = []
book_num = 1

for idx, span in enumerate(spans_text):
    index = idx + 1
    # Starts new key-value pair after set requirements to store metadeta with its
    # correct book
    if span == "Book Type:" and index > 1:
        Magenta[book_num] = metadata
        metadata = []
        book_num += 1
    elif (index) == len(spans_text):
        metadata.append(span)
        Magenta[book_num] = metadata
        metadata = []
        book_num += 1

    else:
        if index % 2 == 0:
            metadata.append(span)


# Scrapes and cleans titles in data table
tds = soup.table.find_all("td")
titles = [td for td in tds if td.get("data-column-index") == "2"]
titles_text = [td.get_text(strip=True) for td in titles]


# Retrieves links in table and removes unwanted links
links = [row.find("a")["href"] for row in soup.select("td:has(a)")]
links = [link for link in links if "gravity_forms" in link]

# Remove duplicates
links = list(dict.fromkeys(links))

filename = "Magenta_Books.csv"
headers = [
    "Book Type:",
    "Issue Number:",
    "Link:",
    "Title:",
    "Published Date:",
    "Description:",
    "Working Group:",
    "ISO Equivalent:",
]

# Creates a csv to store and organize books with metadata
with open(filename, "w", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)

    # Loops through books within Magenta values, adds links,
    # and titles to each book's row
    for idx, book in enumerate(Magenta.values()):
        link = links[idx]
        title = titles_text[idx]
        row = book[:2] + [link] + [title] + book[2:]
        writer.writerow(row)
