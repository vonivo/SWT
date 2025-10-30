from selenium import webdriver
from selenium.webdriver.common.by import By
import os


def is_italic(driver, element):
    """Check if element or any parent up to #bodyContent is italic."""
    el = element

    style = driver.execute_script("return window.getComputedStyle(arguments[0]).fontStyle;", el)
    return style in ("italic", "oblique")

def inside_parentheses(driver, element):
    # Run JS in the browser to compute parentheses around this element
    return driver.execute_script(r"""
        var a = arguments[0];
        var parent = a.parentElement;
        
        while (parent && parent.tagName !== 'P') {
            a = parent;
            parent = parent.parentElement;
            if (parent == null) {
                return false;
            }
        }
        
        var childNodes = Array.from(parent.childNodes);
        var index = childNodes.indexOf(a);
        
        var textBefore = childNodes.slice(0, index).map(n => n.textContent).join('');
        var textAfter = childNodes.slice(index + 1).map(n => n.textContent).join('');
        
        // Runde und eckige Klammern zählen
        var openBefore = ((textBefore.match(/\(/g) || []).length + (textBefore.match(/\[/g) || []).length);
        var closeBefore = ((textBefore.match(/\)/g) || []).length + (textBefore.match(/\]/g) || []).length);
        var openAfter = ((textAfter.match(/\(/g) || []).length + (textAfter.match(/\[/g) || []).length);
        var closeAfter = ((textAfter.match(/\)/g) || []).length + (textAfter.match(/\]/g) || []).length);
        
        // Bedingung: a steht innerhalb von geöffneten, aber noch nicht geschlossenen Klammern
        return (openBefore - closeBefore > 0) && (closeAfter - openAfter > 0);

    """, element)

def find_first_valid_link(driver, visited_links):
    anchors = driver.find_elements(By.CSS_SELECTOR, "#mw-content-text a")

    for a in anchors:
        if not a.get_attribute("href"):
            continue
        if a.get_attribute("href") in visited_links:
            print(f"Loop detected on {a.get_attribute("href")}" )
            continue


        # Skip hatnotes
        if (a.find_elements(By.XPATH, "ancestor::*[contains(@class, 'hatnote')]")
                or a.find_elements(By.XPATH, "ancestor::*[contains(@class, 'hintergrundfarbe1')]")
                or a.find_elements(By.XPATH, "ancestor::*[contains(@class, 'float-right')]")
                or not (a.find_elements(By.XPATH, "ancestor::p") or a.find_elements(By.XPATH, "ancestor::li"))
                or a.find_elements(By.XPATH, "ancestor::figure")
                or a.find_elements(By.XPATH, "ancestor::table")):
            continue

        # Skip infobox
        if a.find_elements(By.XPATH, "ancestor::*[contains(@class, 'infobox')]"):
            continue

        # Skip references
        if a.find_elements(By.XPATH, "ancestor::sup"):
            continue

        # Skip links containing images
        if a.find_elements(By.TAG_NAME, "img"):
            continue

        # Skip italics
        if is_italic(driver, a):
            continue

        # Check parentheses
        if inside_parentheses(driver, a):
            continue

        # Found first valid link
        return a

    return None


def run(starting_page):
    driver = webdriver.Firefox()
    driver.get("http://de.wikipedia.org/wiki/" + starting_page)

    visited_links = []
    counter = 0
    while len(driver.find_elements(By.XPATH, "//*[contains(text(), 'Philosophie')]")) <= 0:
        first_link = find_first_valid_link(driver,visited_links)
        print("Link text:", first_link.text)
        print("URL:", first_link.get_attribute("href"))
        visited_links.append(first_link.get_attribute("href"))
        counter += 1
        first_link.click()

    print(f"Anzahl geklickter links: {counter}")
    driver.close()



cwd = os.getcwd()
print(f"A{cwd}")
file = open(f"{cwd}/List.txt", "r")
for line in file:
    run(line.strip())  # .strip() to remove newline characters
file.close()
