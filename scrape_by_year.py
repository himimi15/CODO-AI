# ONLY WORKS FOR 2022-2023 CODO REQUIREMENTS AS THE PAGE LAYOUT CHANGES FOR DIFFERENT YEARS

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

# NOTE: Setup WebDriver (Chrome)
driver_path = '/usr/local/bin/chromedriver'
driver = webdriver.Chrome(executable_path=driver_path)
print("WebDriver setup complete.")

url = "https://www.purdue.edu/advisors/codo/"
driver.get(url)

# Collect all the CODO years and their links (solely through Selenium)
years_elements = driver.find_elements(By.CSS_SELECTOR, 'div.maincontent a[href*="requirements"], div.maincontent a[href*="catalog.purdue.edu"]')
years = [(element.text, element.get_attribute('href')) for element in years_elements]

for i, (year, _) in enumerate(years, start=1):
    print(f"{i}. {year}")

year_index = int(input("Enter the number of the CODO year you want to view: ")) - 1

year_name, selected_year_link = years[year_index]
driver.get(selected_year_link)

soup = BeautifulSoup(driver.page_source, 'html.parser')

# NOTE: Extract all colleges
colleges = [(tag.text, tag['href'].replace('#', '')) for tag in soup.find_all('a') if any(keyword in tag.text for keyword in ['College', 'School', 'Studies', 'Institute']) and tag['href'].startswith('#')]

for i, (college, _) in enumerate(colleges, start=1):
    print(f"{i}. {college}")

college_index = int(input("Enter the number of the college you want to CODO into: ")) - 1
selected_college, section_id = colleges[college_index]

print("Selected college: " + selected_college)

driver.execute_script("document.getElementById(arguments[0]).scrollIntoView();", section_id)

# NOTE: Extract all majors under the selected college
section = soup.find(id=section_id)
majors = [(li.text.strip(), li.find('a')['href']) for li in section.find_next('ul').find_all('li') if li.find('a')]

for i, (major, _) in enumerate(majors, start=1):
    print(f"{i}. {major}")

major_index = int(input("Enter the number of the major you want to CODO into: ")) - 1

if 0 <= major_index < len(majors):
    # Get the selected major's name and link
    selected_major, major_link = majors[major_index]    
    print("Selected major: " + selected_major)
    
    # Navigate to the link of the selected major
    base_url = "https://catalog.purdue.edu/"
    if not major_link.startswith(('http://', 'https://')):
        major_link = base_url + major_link
    
    driver.get(major_link)

else:
    print("Invalid selection. Please run the script again and select a valid number for the major.")
    driver.quit()

# NOTE: Extract CODO requirements from the major's page
soup = BeautifulSoup(driver.page_source, 'html.parser')     # new page, new object

def extract_requirements_by_name(soup, name_attribute):
    requirements = []
    for anchor in soup.find_all('a', attrs={'name': name_attribute}):
        ul = anchor.find_parent().find_next_sibling('ul')
        if ul:
            requirements.extend([li.get_text(strip=True) for li in ul.find_all('li')])
    return requirements

general_requirements = extract_requirements_by_name(soup, 'generalrequirements')
print("General Requirements:")
for requirement in general_requirements:
    print(requirement)

course_requirements = extract_requirements_by_name(soup, 'courserequirements')
print("\nCourse Requirements:")
for requirement in course_requirements:
    print(requirement)
