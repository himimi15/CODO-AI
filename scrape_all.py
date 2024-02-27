from selenium import webdriver
from bs4 import BeautifulSoup
import os

def setup_driver(driver_path):
    return webdriver.Chrome(executable_path=driver_path)

def get_soup(driver, url):
    driver.get(url)
    return BeautifulSoup(driver.page_source, 'html.parser')

def extract_colleges(soup):
    return [(tag.text, tag['href'].replace('#', '')) for tag in soup.find_all('a') 
            if any(keyword in tag.text for keyword in ['College', 'School', 'Studies', 'Institute']) 
            and tag['href'].startswith('#')]

def extract_majors(soup, section_id):
    section = soup.find(id=section_id)
    return [(li.text.strip(), li.find('a')['href']) for li in section.find_next('ul').find_all('li') if li.find('a')]

def navigate_to_major(driver, major_link, base_url="https://catalog.purdue.edu/"):
    if not major_link.startswith(('http://', 'https://')):
        major_link = base_url + major_link
    driver.get(major_link)

def extract_requirements(soup, name_attribute):
    requirements = []
    for anchor in soup.find_all('a', attrs={'name': name_attribute}):
        ul = anchor.find_parent().find_next_sibling('ul')
        if ul:
            requirements.extend([li.get_text(strip=True) for li in ul.find_all('li')])
    return requirements

def scrape_all_majors(driver_path, url, folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    driver = setup_driver(driver_path)
    soup = get_soup(driver, url)
    colleges = extract_colleges(soup)

    for college_name, section_id in colleges:
        print(f"Processing {college_name}...")
        majors = extract_majors(soup, section_id)
        
        for major_name, major_link in majors:
            navigate_to_major(driver, major_link)
            new_soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            general_requirements = extract_requirements(new_soup, 'generalrequirements')
            course_requirements = extract_requirements(new_soup, 'courserequirements')
            
            # file_name = os.path.join(folder_name, f"{major_name}_CODO.txt").replace('/', '_').replace(' ', '_')
            file_name = os.path.join(folder_name, f"{major_name.replace('/', '_').replace(' ', '_')}_CODO.txt")
            with open(file_name, 'w') as file:
                file.write(f"General Requirements:\n")
                file.writelines([f"{req}\n" for req in general_requirements])
                file.write(f"\nCourse Requirements:\n")
                file.writelines([f"{req}\n" for req in course_requirements])
            
            print(f"Completed: {major_name}")

    driver.quit()
    print("All data has been scraped and saved.")

# Example usage
driver_path = '/usr/local/bin/chromedriver'
url = "https://catalog.purdue.edu/content.php?catoid=15&navoid=19105"
folder_name = "Purdue_Majors_CODOs"
scrape_all_majors(driver_path, url, folder_name)
