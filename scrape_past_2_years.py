from selenium import webdriver
from bs4 import BeautifulSoup
import os
import time

driver_path = '/usr/local/bin/chromedriver'
driver = webdriver.Chrome(executable_path=driver_path)

url = "https://catalog.purdue.edu/content.php?catoid=14&navoid=17003"
driver.get(url)

# Find all links containing "(CODO) Requirements"
print("Extracting links...")
soup = BeautifulSoup(driver.page_source, 'html.parser')
base_url = "https://catalog.purdue.edu/"
links = [(a.text, base_url + a['href']) for a in soup.find_all('a', href=True) if "(CODO) Requirements" in a.text]

# remove the first link 
links.pop(0)
# print(links)

# Directory to save the files
parent_dir = "./CODO_Requirements"
os.makedirs(parent_dir, exist_ok=True)

def extract_requirements_by_name(soup, name_attribute):
    requirements = []
    for anchor in soup.find_all('a', attrs={'name': name_attribute}):
        ul = anchor.find_parent().find_next_sibling('ul')
        if ul:
            requirements.extend([li.get_text(strip=True) for li in ul.find_all('li')])
    return requirements

for major_name, link in links:
    # Use Selenium to navigate to each page because of potential JavaScript rendering
    driver.get(link)

    # Use BeautifulSoup to parse page content
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract the required information (Adjust the selectors as needed)
    general_requirements = extract_requirements_by_name(soup, 'generalrequirements')
    course_requirements = extract_requirements_by_name(soup, 'courserequirements')
    other_requirements = extract_requirements_by_name(soup, 'otherrequirements')

    # Filename based on some identifying feature of the page
    folder_name = "Purdue_Majors_CODOs_2_years"

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    file_name = os.path.join(folder_name, f"{major_name.replace('/', '_').replace(' ', '_')}_CODO.txt")

    # Write the extracted information to a file
    with open(file_name, 'w') as file:
        file.write("General Requirements:\n")
        file.writelines([f"{req}\n" for req in general_requirements])
        file.write("\nCourse Requirements:\n")
        file.writelines([f"{req}\n" for req in course_requirements])
        file.write("\nOther Requirements:\n")
        file.writelines([f"{req}\n" for req in other_requirements])
        

# Close the WebDriver
driver.quit()

print("Data extraction complete.")
