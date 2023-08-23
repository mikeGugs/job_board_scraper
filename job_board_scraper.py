import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    # Wait until cookie-tracker loads
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
    ny_office = webdriver.find_element('xpath', '//*[@id="LAYER_MID"]/div/div/main/div[1]/section[2]/div/div[1]/div[3]/ul/li[3]')
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
    # Wait for jobs to load
    time.sleep(2)
    elements = webdriver.find_elements('xpath', '//div[@class="item experienced position"]')
    jobs = [element.text.strip() for element in elements if element.text.strip()]
    webdriver.close()
    return jobs

def get_tower_jobs():
    """Tower Research Capital"""
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

    webdriver.close()

    return jobs

def get_millennium_jobs():
    """Millennium Management"""
    millennium_url = 'https://www.mlp.com/job-listings/'
    m_driver = webdriver_response(millennium_url)

    # Try to wait until cookie tracker acceptance button is clickable
    time.sleep(2)

    # Again wait for cookie tracker. Maybe this isn't needed?
    WebDriverWait(m_driver, 10).until(
        EC.element_to_be_clickable(('xpath', '//*[@id="global_cookie_policy"]/div/div/a')))
    # Accept cookie-tracker
    accept_button = m_driver.find_element('xpath', '//*[@id="global_cookie_policy"]/div/div/a')
    accept_button.click()

    m_driver.find_element('xpath', '/html/body/div[4]/main/div/div/section/div')

    m_soup = BeautifulSoup(m_driver.page_source, 'html.parser')
    jobs = []
    for job_element in m_soup.find_all('li', {'class': 'page-section__content--list-container'}):
        if 'New York' in job_element.text:
            jobs.append(job_element.text.strip().split('\n')[0])
    m_driver.close()

    return jobs

def get_aqr_jobs():
    """AQR Capital Management"""
    aqr_url = 'https://careers.aqr.com/jobs/city/greenwich#/'
    aqr_driver = webdriver_response(aqr_url)

    aqr_soup = BeautifulSoup(aqr_driver.page_source, 'html.parser')
    greenwich_jobs = aqr_soup.find_all('td', {'class': 'col-sm-6'})
    # 'td' tags are pairs, one for job and the next for department. [::2] skips
    # every other index in the greenwich_jobs list starting at index 1, because
    # those are all departments. After this we are left with only job titles.

    greenwich_jobs = [job.text.strip() for job in greenwich_jobs if job.text.strip()][::2]
    aqr_driver.close()

    return greenwich_jobs


def get_squarepoint_jobs():
    """Squarepoint Capital"""
    sqp_url = 'https://www.squarepoint-capital.com/careers#s4'
    sqp_driver = webdriver_response(sqp_url)

    sqp_soup = BeautifulSoup(sqp_driver.page_source, 'html.parser')
    sqp_jobs = sqp_soup.find_all('p', {'class': 'positionName'})
    sqp_locations = sqp_soup.find_all('p', {'class': 'positionLocation'})

    if len(sqp_jobs) != len(sqp_locations):
        raise IndexError("The amount of job and location tags for Squarepoint do not equal!"
                         " They probably added a job without a corresponding location.")

    sqp_jobs_w_locations = [(job.text, location.text) for job, location in zip(sqp_jobs, sqp_locations)]
    ny_jobs = [job[0].strip() for job in sqp_jobs_w_locations if 'New York' in job[1]]

    sqp_driver.close()

    return ny_jobs

def get_iex_jobs():
    """Investor's Exchange"""
    iex_url = 'https://www.iex.io/careers#open-roles'
    iex_driver = webdriver_response(iex_url)
    # Wait for jobs to load
    time.sleep(2)
    iex_soup = BeautifulSoup(iex_driver.page_source, 'html.parser')
    jobs = iex_soup.find_all('div', {'fs-cmsfilter-field': 'title',
                                     'data-js': 'title'})
    jobs = [job.text.strip() for job in jobs]
    iex_driver.close()
    return jobs

def get_p72_jobs():
    """Point 72 Asset Management"""
    p72_url = 'https://careers.point72.com/?location=new%20york'
    p72_driver = webdriver_response(p72_url)
    # Wait for jobs to load
    time.sleep(2)
    p72_soup = BeautifulSoup(p72_driver.page_source, 'html.parser')
    jobs = p72_soup.find_all('a', {'class': 'searchSite'})
    jobs = [job.text.strip() for job in jobs]
    p72_driver.close()

    return jobs

def get_citsec_jobs():
    """Citadel Securities"""
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

    citsec_driver.close()

    return nyc_jobs

def get_xtx_jobs():
    """XTX Markets"""
    xtx_url = 'https://www.xtxmarkets.com'
    xtx_driver = webdriver_response(xtx_url)
    # Wait for page to load
    time.sleep(2)
    xtx_soup = BeautifulSoup(xtx_driver.page_source, 'html.parser')
    nyc_jobs = xtx_soup.find_all('li', {'class': 'opening_job_item active',
                                        'data-tabs': "NEW YORK"})
    nyc_job_titles = [job.find('div', {'class': 'title'}) for job in nyc_jobs]

    nyc_job_titles = [job.text.strip() for job in nyc_job_titles]

    xtx_driver.close()

    return nyc_job_titles

def get_worldquant_jobs():
    """Worldquant, LLC"""
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

    wq_driver.close()

    return ny_jobs

def get_pdt_jobs():
    """PDT Partners"""
    pdt_url = 'https://pdtpartners.com/careers'
    pdt_soup = soupify_response(pdt_url)
    jobs = pdt_soup.find_all('div', {'class': 'job'})
    job_titles = [job.find('a').text.strip() for job in jobs]
    return job_titles

def get_bam_jobs():
    """Balyasny Asset Management"""
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

    bam_driver.close()

    return ny_jobs

def get_rentec_jobs():
    """Renaissance Technologies"""
    rentec_url = 'https://www.rentec.com/Careers.action?jobs=true'
    rentec_soup = soupify_response(rentec_url)
    rentec_jobs = rentec_soup.find_all('div', {'class': 'flex-auto'})
    jobs = [job.text.strip() for job in rentec_jobs if "Privacy Policy" not in job.text.strip()]
    return jobs

def get_two_sigma_jobs():
    """Two Sigma"""
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
        if iternum < (int(max_pages) - 2):
            next_button = ts_driver.find_element('xpath', '/html/body/div/div/div[2]/div/div[2]/div[1]/div[2]/a[4]')
            WebDriverWait(ts_driver, 10).until(EC.element_to_be_clickable((next_button))).click()

        # For some reason the xpath of the "next" button changes on the second to last page
        # (the last page where "next" is clickable). Also, I am only able to figure out how to find
        # the top "next" button on the page - I am having no luck finding the bottom "next" button
        # with Selenium, which seems to stay put (no changing xpath) for all of the pages.
        elif iternum == (int(max_pages) - 2):
            next_button = ts_driver.find_element('xpath', '/html/body/div/div/div[2]/div/div[2]/div[1]/div[2]/a[6]')
            WebDriverWait(ts_driver, 10).until(EC.element_to_be_clickable((next_button))).click()

    ts_driver.close()

    return all_ts_jobs


def main():
    jobs_dict = {'hrt': {'company_name': 'Hudson River Trading',
                         'todays_jobs': get_hrt_jobs()},
                 'deshaw': {'company_name': 'D.E. Shaw',
                            'todays_jobs': get_deshaw_jobs()},
                 'js': {'company_name': 'Jane Street',
                        'todays_jobs': get_js_jobs()},
                 'tower': {'company_name': 'Tower Research Capital',
                           'todays_jobs': get_tower_jobs()},
                 'millennium': {'company_name': 'Millennium',
                                'todays_jobs': get_millennium_jobs()},
                 'aqr': {'company_name': 'AQR',
                         'todays_jobs': get_aqr_jobs()},
                 'squarepoint': {'company_name': 'Sqaurepoint',
                                 'todays_jobs': get_squarepoint_jobs()},
                 'iex': {'company_name': "IEX",
                         'todays_jobs': get_iex_jobs()},
                 'p72': {'company_name': 'Point 72',
                         'todays_jobs': get_p72_jobs()},
                 'citsec': {'company_name': 'Citadel Securities',
                            'todays_jobs': get_citsec_jobs()},
                 'xtx': {'company_name': 'XTX Markets',
                         'todays_jobs': get_xtx_jobs()},
                 'worldquant': {'company_name': 'Worldquant',
                                'todays_jobs': get_worldquant_jobs()},
                 'pdt': {'company_name': "PDT Partners",
                         'todays_jobs': get_pdt_jobs()},
                 'bam': {'company_name': 'Balyasny Asset Management',
                         'todays_jobs': get_bam_jobs()},
                 'rentec': {'company_name': 'Renaissance Technologies',
                            'todays_jobs': get_rentec_jobs()},
                 'ts': {'company_name': 'Two Sigma',
                        'todays_jobs': get_two_sigma_jobs()}
                 }

    today = datetime.now().strftime("%Y%m%d")

    # Make a list to store text that will be written to a file to save
    # a summary of new jobs found today
    new_jobs_file_text = []

    for company in jobs_dict:
        try:
            with open(f".{company}", 'r') as old_file:
                old_jobs = old_file.read().splitlines()
                last_check_date = old_jobs[0]
                days_between = (datetime.strptime(last_check_date, "%Y%m%d") - datetime.strptime(today, "%Y%m%d")).days
                days_between = days_between * -1 if days_between < 0 else days_between
            new_jobs = []

            # Only write to jobs file if program correctly loaded jobs from careers page
            if jobs_dict[company]['todays_jobs']:
                with open(f".{company}", 'w') as new_file:
                    new_file.write(f"{today}\n")
                    for job in jobs_dict[company]['todays_jobs']:
                        if job not in old_jobs:
                            new_jobs.append(job)
                        new_file.write(f"{job}\n")
            else:
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
                            f"{jobs_dict[company]['company_name']}. Writing {len(jobs_dict[company]['todays_jobs'])} jobs to file. " \
                            "Check back tomorrow for new jobs!\n"

            # Print that this is a new company to the terminal
            print(new_co_string)

            # Write each companies job listings so program has something to compare against
            # on the next day it is run.
            new_jobs_file_text.append(new_co_string)
            with open(f".{company}", "w") as new_file:
                new_file.write(f"{today}\n")
                for job in jobs_dict[company]['todays_jobs']:
                    new_file.write(f"{job}\n")

    # Write new jobs to new_jobs file. Rewritten every time this program is run.
    with open("new_jobs", 'w') as new_jobs_file:
        new_jobs_file.write(f"New jobs as of {today}:\n")
        for row in new_jobs_file_text:
            new_jobs_file.write(row)


if __name__ == "__main__":
    main()