import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from datetime import datetime
import time

def soupify_response(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 '
                             'Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def webdriver_response(url):
    driver = webdriver.Firefox()
    driver.get(url)
    return driver

def get_hrt_jobs():
    """Hudson River Trading"""
    hrt_url = 'https://www.hudsonrivertrading.com/careers/?_offices=New+York'
    hrt_soup = soupify_response(hrt_url)
    nyc_job_data = hrt_soup.find_all('tr', {'class': 'job-row',
                                        'data-filter-hidden' :'false',
                                        'data-search-hidden': 'false'})
    jobs = [job.find('span', {'class': 'job-title'}).text.strip() for job in nyc_job_data]
    return jobs

def get_deshaw_jobs():
    """DE Shaw"""
    deshaw_url = 'https://www.deshaw.com/careers/choose-your-path'
    webdriver = webdriver_response(deshaw_url)
    # Wait until page scrolls down and job-board loads
    WebDriverWait(webdriver, 30).until(EC.invisibility_of_element_located(('xpath',
                                                                   "//*[@id='TemplateTransitionLayer']")))
    # Wait cookie-tracker loads
    WebDriverWait(webdriver, 10).until(
        EC.element_to_be_clickable(('xpath', '//*[@id="LAYER_COOKIE"]/section/div/div')))
    # Accept cookie-tracker
    accept_button = webdriver.find_element('class name', 'accept-button')
    accept_button.click()
    # Wait until experience level dropdown loads
    WebDriverWait(webdriver, 10).until(EC.element_to_be_clickable(('xpath', '//*[@id="LAYER_MID"]/div/div/main/div[1]/section['
                                                '2]/div/div[1]/div[1]/button')))
    # Find experience level dropdown and click it
    profession_button = webdriver.find_element('xpath', '//*[@id="LAYER_MID"]/div/div/main/div[1]/section['
                                                '2]/div/div[1]/div[1]/button')
    profession_button.click()
    # Choose that I am a "professional"
    choose_professional = webdriver.find_element('xpath', '/html/body/div[1]/div[4]/div/div/main/div[1]/section[2]/div/div[1]/div[1]/ul/li[2]')
    choose_professional.click()
    # Find office location dropdown and click it
    office_location = webdriver.find_element('xpath', '//*[@id="LAYER_MID"]/div/div/main/div[1]/section['
                                                '2]/div/div[1]/div[3]/button')
    office_location.click()
    # Choose that I'm interested in the NY office
    ny_office = webdriver.find_element('xpath', '//*[@id="LAYER_MID"]/div/div/main/div[1]/section[2]/div/div[1]/div[3]/ul/li[2]')
    ny_office.click()
    # Choose to view all jobs
    view_all_jobs = webdriver.find_element('xpath', '//*[@id="LAYER_MID"]/div/div/main/div[1]/section['
                                                '2]/div/div[2]/div[3]/div')
    view_all_jobs.click()

    jobs_soup = BeautifulSoup(webdriver.page_source, 'html.parser')
    all_jobs = jobs_soup.find_all('span', {'class': None})
    all_jobs = [job.text.strip() for job in all_jobs if job.text.strip()]
    all_jobs = [job for job in all_jobs if 'Intern' not in job]

    webdriver.close()

    return all_jobs

def get_js_jobs():
    """Jane Street"""
    js_url = 'https://www.janestreet.com/join-jane-street/open-roles/?type=experienced-candidates&location=new-york'
    webdriver = webdriver_response(js_url)
    elements = webdriver.find_elements('xpath', '//div[@class="item experienced position"]')
    jobs = [element.text.strip() for element in elements if element.text.strip()]
    webdriver.close()
    return jobs

def get_tower_jobs():
    """Tower Research Capital"""
    tower_url = 'https://www.tower-research.com/open-positions'
    webdriver = webdriver_response(tower_url)
    frame = webdriver.find_element('xpath', '//*[@id="grnhse_iframe"]')
    webdriver.switch_to.frame(frame)
    soup = BeautifulSoup(webdriver.page_source, 'html.parser')
    elements = soup.find_all('div', {'class': 'opening',
                                 'data-office-1249': 'true'})
    jobs = [job.find('a').text.strip() for job in elements if job.find('a').text.strip()]
    webdriver.close()
    return jobs

def main():
    jobs_dict = {'hrt': {'company_name': 'Hudson River Trading',
                         'todays_jobs': get_hrt_jobs()},
                 'deshaw': {'company_name': 'D.E. Shaw',
                            'todays_jobs': get_deshaw_jobs()},
                 'js': {'company_name': 'Jane Street',
                        'todays_jobs': get_js_jobs()},
                 'tower': {'company_name': 'Tower Research Capital',
                           'todays_jobs': get_tower_jobs()}}

    today = datetime.now().strftime("%Y%m%d")

    for company in jobs_dict:
        try:
            with open(f".{company}", 'r') as old_file:
                old_jobs = old_file.read().splitlines()
                last_check_date = old_jobs[0]
                days_between = (datetime.strptime(last_check_date, "%Y%m%d") - datetime.strptime(today, "%Y%m%d")).days
                days_between = days_between * -1 if days_between < 0 else days_between
            new_jobs = []
            with open(f".{company}", 'w') as new_file:
                new_file.write(f"{today}\n")
                for job in jobs_dict[company]['todays_jobs']:
                    if job not in old_jobs:
                        new_jobs.append(job)
                    new_file.write(f"{job}\n")

            print(f"{len(new_jobs)} new jobs for {jobs_dict[company]['company_name']} on {today}. You last "
                  f"checked {days_between} days ago.")
            for job in enumerate(new_jobs):
                print(f"\t-{job[0]}) {job[1]}\n")

        except FileNotFoundError:
            print(f"Looks like this is the first day you're checking for "
                  f"{jobs_dict[company]['company_name']}. Writing jobs to file. "
                  "Check back tomorrow for new jobs!")
            with open(f".{company}", "w") as new_file:
                new_file.write(f"{today}\n")
                for job in jobs_dict[company]['todays_jobs']:
                    new_file.write(f"{job}\n")





if __name__ == "__main__":
    main()


    # USE OS TO CHECK IF DIR EXISTS, IF NOT THEN MAKE IT (TO HOLD FILE FOR EACH CO)


