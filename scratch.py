from selenium import webdriver

path = '/usr/local/bin/geckodriver'

url = 'https://www.janestreet.com/join-jane-street/open-roles/?type=experienced-candidates&location=new-york'

driver = webdriver.Firefox()

driver.get(url)

elements = driver.find_elements('xpath', '//div[@class="item experienced position"]')

jobs = [element.text.strip() for element in elements if element.text.strip()]

print(jobs)
print(len(jobs))

driver.close()