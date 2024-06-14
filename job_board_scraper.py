import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import time
import re
import sys
import os

def soupify_response(driver_response):
    soup = BeautifulSoup(driver_response.page_source, 'html.parser')
    return soup

def webdriver_response(url):
    # install chrome driver
    chromedriver_autoinstaller.install()

    # Create a Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument('--disable-dev-shm-usage')
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    chrome_options.add_argument(f'user-agent={user_agent}')    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    return driver

def get_hrt_jobs():
    """Hudson River Trading"""
    print("getting HRT jobs")
    hrt_url = 'https://www.hudsonrivertrading.com/careers/?_offices=New+York'
    driver_response = webdriver_response(hrt_url)
    hrt_soup = soupify_response(driver_response)
    nyc_job_data = hrt_soup.find_all('tr', {'class': 'job-row',
                                        'data-filter-hidden' :'false',
                                        'data-search-hidden': 'false'})
    jobs = [job.find('span', {'class': 'job-title'}).text.strip() for job in nyc_job_data]
    driver_response.quit()
    return jobs

def get_deshaw_jobs():
    """DE Shaw"""
    print("Getting DE Shaw jobs")
    deshaw_url = 'https://www.deshaw.com/careers/choose-your-path'
    webdriver = webdriver_response(deshaw_url)
    # Wait until page scrolls down and job-board loads
    time.sleep(2)
    # Wait until cookie-tracker loads
    WebDriverWait(webdriver, 10).until(
        EC.element_to_be_clickable(('xpath', '//*[@id="LAYER_COOKIE"]/section/div/div')))
    # Accept cookie-tracker
    accept_button = webdriver.find_element('class name', 'accept-button')
    webdriver.execute_script("arguments[0].click();", accept_button)
    # Wait until experience level dropdown loads
    WebDriverWait(webdriver, 10).until(EC.element_to_be_clickable(('xpath', '//*[@id="LAYER_MID"]/div/div/main/div[1]/section['
                                                '2]/div/div[1]/div[1]/button')))
    # Find experience level dropdown and click it
    profession_button = webdriver.find_element('xpath', '//*[@id="LAYER_MID"]/div/div/main/div[1]/section['
                                                '2]/div/div[1]/div[1]/button')
    webdriver.execute_script("arguments[0].click();", profession_button)
    # Choose that I am a "professional"
    choose_professional = webdriver.find_element('xpath', '/html/body/div[1]/div[4]/div/div/main/div[1]/section[2]/div/div[1]/div[1]/ul/li[2]')
    webdriver.execute_script("arguments[0].click();", choose_professional)
    # Find office location dropdown and click it
    office_location = webdriver.find_element('xpath', '//*[@id="LAYER_MID"]/div/div/main/div[1]/section['
                                                '2]/div/div[1]/div[3]/button')
    webdriver.execute_script("arguments[0].click();", office_location)
    # Choose that I'm interested in the NY office
    ny_office = webdriver.find_element('xpath', '//*[@id="LAYER_MID"]/div/div/main/div[1]/section[2]/div/div[1]/div[3]/ul/li[2]')
    webdriver.execute_script("arguments[0].click();", ny_office)
    # Choose to view all jobs
    view_all_jobs = webdriver.find_element('xpath', '//*[@id="LAYER_MID"]/div/div/main/div[1]/section['
                                                '2]/div/div[2]/div[3]/div')
    webdriver.execute_script("arguments[0].click();", view_all_jobs)

    jobs_soup = BeautifulSoup(webdriver.page_source, 'html.parser')
    all_jobs = jobs_soup.find_all('span', {'class': None})
    all_jobs = [job.text.strip() for job in all_jobs if job.text.strip()]
    all_jobs = [job for job in all_jobs if 'Intern' not in job]

    webdriver.quit()

    return all_jobs

def get_js_jobs():
    """Jane Street"""
    print("Getting JS Jobs")
    js_url = 'https://www.janestreet.com/join-jane-street/open-roles/?type=experienced-candidates&location=new-york'
    webdriver = webdriver_response(js_url)
    # Wait for jobs to load
    time.sleep(2)
    elements = webdriver.find_elements('xpath', '//div[@class="item experienced position"]')
    jobs = [element.text.strip() for element in elements if element.text.strip()]
    webdriver.quit()
    return jobs

def get_tower_jobs():
    """Tower Research Capital"""
    print("Getting Tower jobs")
    tower_url = 'https://www.tower-research.com/open-positions'
    webdriver = webdriver_response(tower_url)
    # Wait for page to load
    time.sleep(2)
    frame = webdriver.find_element('xpath', '//*[@id="grnhse_iframe"]')
    webdriver.switch_to.frame(frame)

    soup = BeautifulSoup(webdriver.page_source, 'html.parser')
    elements = soup.find_all('div', {'class': 'opening',
                                 'data-office-1249': 'true'})

    jobs = [job.find('a').text.strip() for job in elements if job.find('a').text.strip()]

    webdriver.quit()

    return jobs

def get_millennium_jobs():
    """Millennium Management"""
    print("Getting Millennium jobs")
    millennium_url = 'https://mlp.eightfold.ai/careers?location=New%20York%2C%20New%20York%2C%20United%20States%20of%20America&pid=755933841912&domain=mlp.com&sort_by=relevance&triggerGoButton=false&triggerGoButton=true'
    m_driver = webdriver_response(millennium_url)
    show_more = m_driver.find_element(By.CLASS_NAME, 'show-more-positions')
    # Need to click through all of the "Show More Positions" buttons to bring them all into view
    while show_more:
        m_driver.execute_script("arguments[0].click();", show_more)
        time.sleep(3)
        try:
            show_more = m_driver.find_element(By.CLASS_NAME, 'show-more-positions')
        except NoSuchElementException as e:
            show_more = False

    m_soup = BeautifulSoup(m_driver.page_source, 'html.parser')
    jobs = []
    for job_element in m_soup.find_all('div', {'class': 'position-card'}):
        position = job_element.find('div', {'class': 'position-title'}).text.strip()
        location = job_element.find('p', {'class': 'position-location'}).text.strip()
        jobs.append(position) if 'new york' in location.lower() else None
    m_driver.quit()

    return jobs

def get_aqr_jobs():
    """AQR Capital Management"""
    print("Getting AQR Jobs")
    aqr_url = 'https://careers.aqr.com/jobs/city/greenwich#/'
    aqr_driver = webdriver_response(aqr_url)

    aqr_soup = BeautifulSoup(aqr_driver.page_source, 'html.parser')
    greenwich_jobs = aqr_soup.find_all('td', {'class': 'col-sm-6'})
    # 'td' tags are pairs, one for job and the next for department. [::2] skips
    # every other index in the greenwich_jobs list starting at index 1, because
    # those are all departments. After this we are left with only job titles.

    greenwich_jobs = [job.text.strip() for job in greenwich_jobs if job.text.strip()][::2]
    aqr_driver.quit()

    return greenwich_jobs


def get_squarepoint_jobs():
    """Squarepoint Capital"""
    print("Getting Squarepoint jobs")
    sqp_url = 'https://www.squarepoint-capital.com/careers'
    sqp_driver = webdriver_response(sqp_url)

    open_positions_button = sqp_driver.find_element('xpath', '/html/body/div[2]/section[1]/div/a')
    sqp_driver.execute_script("arguments[0].click();", open_positions_button)
    time.sleep(2)

    sqp_soup = BeautifulSoup(sqp_driver.page_source, 'html.parser')
    sqp_jobs = sqp_soup.find_all('button', {'etype': re.compile(r'.*'),
                                            'office': re.compile(r'.*[nN]ew\s[yY]ork.*')
                                            }
                                 )

    sqp_job_titles = [j.find('strong').text for j in sqp_jobs]

    sqp_driver.quit()

    return sqp_job_titles

def get_iex_jobs():
    """Investor's Exchange"""
    print("Getting IEX Jobs")
    iex_url = 'https://www.iex.io/careers#open-roles'
    iex_driver = webdriver_response(iex_url)
    # Wait for jobs to load
    time.sleep(2)
    iex_soup = BeautifulSoup(iex_driver.page_source, 'html.parser')
    jobs = iex_soup.find_all('div', {'fs-cmsfilter-field': 'title',
                                     'data-js': 'title'})
    jobs = [job.text.strip() for job in jobs]
    iex_driver.quit()
    return jobs

def get_p72_jobs():
    """Point 72 Asset Management"""
    print("Getting Point 72 Jobs")
    p72_url = 'https://careers.point72.com/?location=new%20york'
    p72_driver = webdriver_response(p72_url)
    # Wait for jobs to load
    time.sleep(2)
    p72_soup = BeautifulSoup(p72_driver.page_source, 'html.parser')
    jobs = p72_soup.find_all('a', {'class': 'searchSite'})
    jobs = [job.text.strip() for job in jobs]
    p72_driver.quit()

    return jobs

def get_citsec_jobs():
    """Citadel Securities"""
    print("Getting Citadel Securities' jobs")
    citsec_url = 'https://www.citadelsecurities.com/careers/open-opportunities/positions-for-professionals/'
    citsec_driver = webdriver_response(citsec_url)
    # Wait for page to load
    time.sleep(2)
    citsec_soup = BeautifulSoup(citsec_driver.page_source, 'html.parser')

    locations = citsec_soup.find_all('div', {"class": 'careers-listing-card__location'})
    locations = [location.text.strip() for location in locations]

    jobs = citsec_soup.find_all('div', {'class': 'careers-listing-card__title'})
    jobs = [job.text.strip() for job in jobs]

    jobs_w_loc = zip(jobs, locations)

    nyc_jobs = [job[0] for job in jobs_w_loc if 'New York' in job[1]]

    citsec_driver.quit()

    return nyc_jobs

def get_xtx_jobs():
    """XTX Markets"""
    print("Getting XTX jobs")
    xtx_url = 'https://www.xtxmarkets.com/#careers'
    xtx_driver = webdriver_response(xtx_url)
    # Wait for page to load
    time.sleep(2)
    xtx_soup = BeautifulSoup(xtx_driver.page_source, 'html.parser')
    jobs = xtx_soup.find_all('li', {'class': 'opening_job_item active'})

    nyc_jobs = [job for job in jobs if 'New York' in job.text]

    nyc_job_titles = [job.find('div', {'class': 'title'}) for job in nyc_jobs]

    nyc_job_titles = [job.text.strip() for job in nyc_job_titles]

    xtx_driver.quit()

    return nyc_job_titles

def get_worldquant_jobs():
    """Worldquant, LLC"""
    print("Getting WorldQuant Jobs")
    wq_url = 'https://www.worldquant.com/career-listing/?location=new-york-united-states&department='
    wq_driver = webdriver_response(wq_url)
    # Wait for page to load
    time.sleep(2)

    wq_soup = BeautifulSoup(wq_driver.page_source, 'html.parser')

    jobs = wq_soup.find_all('a', {'class': 'fo-link'})

    job_titles = [job.find('h4', {'class': 'h4'}) for job in jobs]
    job_titles = [job.text.strip() for job in job_titles]

    job_locations = [loc.find('div', {'class': 'fo-zone'}) for loc in jobs]
    job_locations = [loc.text.strip() for loc in job_locations]

    job_w_loc = zip(job_titles, job_locations)

    ny_jobs = []
    for job in job_w_loc:

        # Some jobs location tag says "Multiple Locations", but the class
        # specifies all of the cities the job can be in. It likely would include
        # New York, but would need to check the website.
        if 'New York' in job[1] or 'Multiple Locations' in job[1]:
            ny_jobs.append(job[0].strip())

    wq_driver.quit()

    return ny_jobs

def get_pdt_jobs():
    """PDT Partners"""
    print("Getting PDT Partners' Jobs")
    pdt_url = 'https://pdtpartners.com/careers'
    driver_response = webdriver_response(pdt_url)
    pdt_soup = soupify_response(driver_response)
    jobs = pdt_soup.find_all('div', {'class': 'job'})
    job_titles = [job.find('a').text.strip() for job in jobs]
    driver_response.quit()
    return job_titles

def get_bam_jobs():
    """Balyasny Asset Management"""
    print("Getting Balyasny Jobs")
    bam_url = 'https://bambusdev.my.site.com/s/'
    bam_driver = webdriver_response(bam_url)
    time.sleep(2)
    bam_soup = BeautifulSoup(bam_driver.page_source, 'html.parser')

    jobs = bam_soup.find_all('p', {'class': 'jobRequisitionName'})
    jobs = [job.text for job in jobs]

    locations = bam_soup.find_all('p', {'class': 'jobRequisitionInformation'})
    locations = [loc.text for loc in locations]

    jobs_w_loc = zip(jobs, locations)

    ny_jobs = []
    for job in jobs_w_loc:

        # It is possible that "X Locations" will return jobs not in NY.
        # There doesn't seem to be a clear way to isolate NY if there are
        # multiple locations available.
        if 'New York' in job[1] or 'Locations' in job[1]:
            ny_jobs.append(job[0])

    bam_driver.quit()

    return ny_jobs

def get_rentec_jobs():
    """Renaissance Technologies"""
    print("Getting Rentec Jobs")
    rentec_url = 'https://www.rentec.com/Careers.action?jobs=true'
    driver_response = webdriver_response(rentec_url)
    rentec_soup = soupify_response(driver_response)
    rentec_jobs = rentec_soup.find_all('div', {'class': 'flex-auto'})
    jobs = [job.text.strip() for job in rentec_jobs if "privacy policy" not in job.text.strip() if 'Privacy Policy' not in job.text.strip()]
    driver_response.quit()
    return jobs

def get_two_sigma_jobs():
    """Two Sigma"""
    print("Getting Two Sigma Jobs")
    ts_url = 'https://careers.twosigma.com/careers/SearchJobs/?locationSearch=233%7C%7CNew%20York%7CNew%20York&listFilterMode=1&jobOffset=0'
    ts_driver = webdriver_response(ts_url)
    time.sleep(2)
    ts_soup = BeautifulSoup(ts_driver.page_source, 'html.parser')
    number_of_pages = ts_soup.find_all('a', {'class': 'paginationItem paginationLink'})
    max_pages = max([page.text.strip() for page in number_of_pages])

    all_ts_jobs = []

    # Iterate through the pages. Two Sigma shows 10 jobs max per page.
    for page, iternum in enumerate(range(int(max_pages))):
        cur_page_soup = BeautifulSoup(ts_driver.page_source, 'html.parser')
        jobs_on_page = cur_page_soup.find_all('li', {'class': 'jobResultItem'})
        for job in jobs_on_page:
            all_ts_jobs.append(job.find('a', {'class': 'mobileHide'}).text.strip())
        ts_url = f'https://careers.twosigma.com/careers/SearchJobs/?locationSearch=233%7C%7CNew%20York%7CNew%20York&listFilterMode=1&jobOffset={iternum + 1}0'
        ts_driver.quit()
        ts_driver = webdriver_response(ts_url)
        time.sleep(1)
        ts_soup = BeautifulSoup(ts_driver.page_source, 'html.parser')

    ts_driver.quit()

    return all_ts_jobs

def get_jump_jobs():
    """Jump Trading"""
    print("Getting Jump Trading Jobs")
    jump_url = 'https://www.jumptrading.com/careers/?locations=New-York'
    driver_response = webdriver_response(jump_url)
    jump_soup = soupify_response(driver_response)
    jump_jobs = jump_soup.find_all('p', {'class': 'text-xl lg:text-2xl font-medium text-black group-hover:text-jump-red'})
    locations = jump_soup.find_all('p', {'class': 'text-base lg:text-lg text-dark-gray group-hover:text-black'})
    jobs_w_locations = dict(zip([job.text.strip() for job in jump_jobs], [location.text.strip() for location in locations]))
    ny_jobs = [ny_job for ny_job in jobs_w_locations.keys() if 'New York' in jobs_w_locations[ny_job]]
    driver_response.quit()
    return ny_jobs


def _write_company_jobs_file(company:str, company_jobs: list, date: str, old_jobs=None):
    # Write each companies job listings so program has something to compare against
    # on the next day it is run.
    # Leave old_jobs = None if a new company. If existing company, provide old jobs file
    with open(os.path.join(os.path.dirname(sys.argv[0]), f".{company}"), "w") as new_file:
        new_file.write(f"{date}\n")
        if not old_jobs:
            for job in company_jobs:
                new_file.write(f"{job}\n")
        else:
            new_jobs = []
            for job in company_jobs:
                if job not in old_jobs:
                    new_jobs.append(job)
                new_file.write(f"{job}\n")
            return new_jobs
    return None

def _write_new_jobs_file(new_jobs: list, date: str):
    # Write new jobs to new_jobs file. Rewritten every time this program is run.
    with open(os.path.join(os.path.dirname(sys.argv[0]), 'new_jobs'), 'w') as new_jobs_file:
        new_jobs_file.write(f"New jobs as of {date}:\n")
        for row in new_jobs:
            new_jobs_file.write(row)    
                

def main():
    jobs_dict = {'hrt': {'company_name': 'Hudson River Trading',
                         'todays_jobs': get_hrt_jobs},
                 'deshaw': {'company_name': 'D.E. Shaw',
                            'todays_jobs': get_deshaw_jobs},
                 'js': {'company_name': 'Jane Street',
                        'todays_jobs': get_js_jobs},
                 'tower': {'company_name': 'Tower Research Capital',
                           'todays_jobs': get_tower_jobs},
                 'millennium': {'company_name': 'Millennium',
                                'todays_jobs': get_millennium_jobs},
                 'aqr': {'company_name': 'AQR',
                         'todays_jobs': get_aqr_jobs},
                 'squarepoint': {'company_name': 'Sqaurepoint',
                                 'todays_jobs': get_squarepoint_jobs},
                 'iex': {'company_name': "IEX",
                         'todays_jobs': get_iex_jobs},
                 'p72': {'company_name': 'Point 72',
                         'todays_jobs': get_p72_jobs},
                 'citsec': {'company_name': 'Citadel Securities',
                            'todays_jobs': get_citsec_jobs},
                 'xtx': {'company_name': 'XTX Markets',
                         'todays_jobs': get_xtx_jobs},
                 'worldquant': {'company_name': 'Worldquant',
                                'todays_jobs': get_worldquant_jobs},
                 'pdt': {'company_name': "PDT Partners",
                         'todays_jobs': get_pdt_jobs},
                 'bam': {'company_name': 'Balyasny Asset Management',
                         'todays_jobs': get_bam_jobs},
                 'rentec': {'company_name': 'Renaissance Technologies',
                            'todays_jobs': get_rentec_jobs},
                 'ts': {'company_name': 'Two Sigma',
                        'todays_jobs': get_two_sigma_jobs},
                 'jump': {'company_name': 'Jump Trading',
                          'todays_jobs': get_jump_jobs}
                 }

    today = datetime.now().strftime("%Y%m%d")

    # Make a list to store text that will be written to a file to save
    # a summary of new jobs found today
    new_jobs_file_text = []

    for company in jobs_dict:
        jobs_for_company = jobs_dict[company]['todays_jobs']()
        try:
            with open(os.path.join(os.path.dirname(sys.argv[0]), f".{company}"), 'r') as old_file:
                old_jobs = old_file.read().splitlines()
                last_check_date = old_jobs[0]
                days_between = (datetime.strptime(last_check_date, "%Y%m%d") - datetime.strptime(today, "%Y%m%d")).days
                days_between = days_between * -1 if days_between < 0 else days_between

            # Only write to jobs file if program correctly loaded jobs from careers page
            if jobs_for_company:
                new_jobs = _write_company_jobs_file(company, jobs_for_company, today, old_jobs)
            else:
                new_jobs = []
                print(f"WARNING: picked up 0 jobs for {company}. Not writing new file for {company}.\n")

            # Print new jobs to the terminal
            new_jobs_str = (f"{len(new_jobs)} new jobs for {jobs_dict[company]['company_name']} on {today}. You last "
                            f"checked {days_between} days ago.\n")
            print(new_jobs_str)
            new_jobs_file_text.append(new_jobs_str)
            for job in enumerate(new_jobs, 1):
                new_jobs_for_co = f"\t-{job[0]}) {job[1]}\n"
                print(new_jobs_for_co)
                new_jobs_file_text.append(new_jobs_for_co)

        except FileNotFoundError:
            new_co_string = f"Looks like this is the first day you're checking for " \
                            f"{jobs_dict[company]['company_name']}. Writing {len(jobs_for_company)} jobs to file. " \
                            "Check back tomorrow for new jobs!\n"

            # Print that this is a new company to the terminal
            print(new_co_string)
            # Add text to master file
            new_jobs_file_text.append(new_co_string)
            # Write jobs to company specific file
            _write_company_jobs_file(company, jobs_for_company, today)

        # Let RAM usage cool down
        time.sleep(5)

    # write master new jobs file
    _write_new_jobs_file(new_jobs_file_text, today)



if __name__ == "__main__":
    main()

