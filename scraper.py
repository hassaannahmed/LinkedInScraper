from selenium import webdriver
import time
import sys
import os
import urllib.request as req
import csv
import requests
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.proxy import Proxy, ProxyType
from easygui import *
from PIL import Image, ImageTk

Title = ""
Company = ""
School = ""
Location = ""

WorkExperience = ""

username = ""
password = ""

mode = 2

staticNumber = 0

# Setting time after which it closes for a pause
wakeup = time.time()
wakeup += 60 * 60

option = Options();
option.add_argument("--start-maximized")

r = requests.get("https://pastebin.com/raw/9vPA8ZFY")

if (r.text != 'True'):
    exit()

msg = "Email address and Password are compulsory"
title = "LinkedIn Scrape Bot"
fieldNames = ["Email Address", "Password", "Title", "Company", "School", "Location"]
fieldValues = []  # we start with blanks for the values
fieldValues = multenterbox(msg, title, fieldNames)

# make sure that none of the fields was left blank
while 1:
    if fieldValues == None: break
    errmsg = ""
    for i in range(2):
        if fieldValues[i].strip() == "":
            errmsg = errmsg + ('"%s" is a required field.\n\n' % fieldNames[i])
    if errmsg == "": break  # no problems found
    fieldValues = multenterbox(errmsg, title, fieldNames, fieldValues)
print("Reply was:", fieldValues)

username = fieldValues[0]
password = fieldValues[1]
if len(fieldValues[2]) > 0:
    Title = fieldValues[2]
if len(fieldValues[3]) > 0:
    Company = fieldValues[3]
if len(fieldValues[4]) > 0:
    School = fieldValues[4]
if len(fieldValues[5]) > 0:
    Location = fieldValues[5]

msg = "Mode 1 OR 2?"
title = "Mode"
choices = ["1", "2"]
mode = choicebox(msg, title, choices)

msg = "Scrape Experience?"
title = "Mode"
choices = ["Scrape Experience", "Don't Scrape Experience"]
WorkExperience = choicebox(msg, title, choices)

msg = "Get profiles with no image?"
title = "Blank Image Profiles"
choices = ['Yes', 'No']
getBlank = choicebox(msg, title, choices)

try:
    fh = open('logs/' + Title + Company + School + Location + WorkExperience + 'log.txt', 'r')
    msg = "We have found an old log that had the same search parameters. Do you want to resume search?"
    title = "Log Found"
    choices = ["Yes", "No"]
    resumeSearch = choicebox(msg, title, choices)
    f = open('logs/' + Title + Company + School + Location + WorkExperience + 'log.txt', "r")
    urlToResume = f.read()
except FileNotFoundError:
    resumeSearch = "No"

browser = webdriver.Chrome(executable_path="driver/chromedriver.exe", options=option)

browser.get("http://linkedin.com")
browser.implicitly_wait(30)
browser.find_element_by_id('login-email').send_keys(username)
browser.find_element_by_id('login-password').send_keys(password)
browser.find_element_by_id('login-submit').click()
searchBar = browser.find_element_by_class_name('nav-search-bar')

if (resumeSearch == "Yes"):
    time.sleep(2)
    browser.get(urlToResume)

else:

    # Go to Search Page
    browser.get("https://www.linkedin.com/search/results/people/")

    # Click 'All Filters' and Input the parameters
    time.sleep(1)
    browser.find_element_by_class_name('search-filters-bar__all-filters').click()
    time.sleep(1)
    browser.find_element_by_id('search-advanced-title').send_keys(Title)
    time.sleep(1)
    browser.find_element_by_id('search-advanced-company').send_keys(Company)
    time.sleep(1)
    browser.find_element_by_id('search-advanced-school').send_keys(School)
    time.sleep(1)

    # Finding Locations textbox
    if len(Location) > 0:
        emberTextFields = browser.find_elements_by_class_name('ember-text-field')
        for textField in emberTextFields:
            if textField.get_attribute('placeholder') == 'Add a location':
                textField.send_keys(Location)
                time.sleep(2)
                textField.send_keys(Keys.ENTER)
                break

    # Apply Button
    time.sleep(1)
    browser.find_element_by_class_name('search-advanced-facets__button--apply').click()

# searchBar.find_element_by_xpath("//input[@aria-label='Search']").send_keys(thingToSearch) #Searching for whatever
# searchBar.find_element_by_xpath("//input[@aria-label='Search']").send_keys(Keys.ENTER)

time.sleep(3)
showingXResults = browser.find_element_by_class_name('search-results__total').text
numberToFetch = int(''.join(filter(str.isdigit, showingXResults)))
print(numberToFetch)

if (resumeSearch == "No"):
    if WorkExperience == "Included":
        with open(Title + Company + School + Location + WorkExperience + '.csv', 'w', newline='') as csvFile:
            writer = csv.writer(csvFile)
            rowdata = ['Name', 'Post', 'Firm', 'Location', 'LocalImage', 'Link', 'PictureLink', 'Gender', 'Race',
                       'Experience']
            writer.writerow(rowdata)
    else:
        with open(Title + Company + School + Location + WorkExperience + '.csv', 'w', newline='') as csvFile:
            writer = csv.writer(csvFile)
            rowdata = ['Name', 'Post', 'Firm', 'Location', 'LocalImage', 'Link', 'PictureLink', 'Gender', 'Race']
            writer.writerow(rowdata)

matches = 0
browser.implicitly_wait(10)


def relogin(browser, currentURL, minutesToSleep):
    browser.get('https://www.linkedin.com/m/logout')

    # Staying logged out for 1 minute
    time.sleep(minutesToSleep * 60)

    browser.find_element_by_id('login-email').send_keys(username)
    browser.find_element_by_id('login-password').send_keys(password)
    time.sleep(3)
    browser.find_element_by_id('login-submit').click()
    time.sleep(5)
    browser.get(currentURL)
    wakeup = time.time()
    wakeup += 60 * 60


while (matches < numberToFetch):
    try:
        results = browser.find_elements_by_css_selector(
            '.search-result.search-result__occluded-item.ember-view')
        browser.implicitly_wait(5)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        for i in range(0, len(results)):
            matches += 1

            browser.implicitly_wait(5)
            link = results[i].find_element_by_class_name('search-result__result-link').get_attribute('href')
            print(link)
            browser.implicitly_wait(1)
            try:
                name = results[i].find_element_by_css_selector('.name.actor-name').text
            except:
                name = results[i].find_element_by_class_name('actor-name').text
            print("Name = " + name)
            Job = results[i].find_element_by_class_name('subline-level-1').text  # Get Jobs tag

            if " at " in Job:
                Post = Job.split(" at ")[0]
                Firm = Job.split(" at ")[1]
            else:
                Post = Job
                Firm = Job

            print("Job = " + Job)
            location = results[i].find_element_by_class_name('subline-level-2').text
            print("Location = " + location)

            browser.implicitly_wait(1)
            try:
                pictureLink = results[i].find_element_by_class_name('lazy-image').get_attribute('src')
                # img_data = requests.get(pictureLink, stream=True)
                # image = img_data.raw.read()

                imageName = link.split("/")[4]
                if "results" in imageName:
                    imageName = "LinkedInMember" + str(staticNumber)
                    staticNumber += 1
                req.urlretrieve(pictureLink, "images/" + imageName + ".jpg")
                # open("images/" + imageName + ".jpg", "wb").write(image)
                print("Picture =" + pictureLink)
            except Exception as ee:
                print(ee)
                pictureLink = 'Blank'
                print(pictureLink)
                imageName = 'null'

            if pictureLink == 'Blank':
                if getBlank == "No":
                    continue

            gender = "M/F"
            race = "Race"

            if mode == "2":
                if imageName != 'null':
                    image = "images/" + imageName + ".jpg"
                    msg = "Male Or Female?"
                    choices = ["Male", "Female"]
                    choice = buttonbox(msg, image=image, choices=choices)
                    gender = choice
                    msg = "Please specify his/her race. Name --> " + name
                    choices = ["B", "W", "A", "I", "O", "H"]
                    choice = buttonbox(msg, image=image, choices=choices)
                    race = choice

            workExp = ""
            if WorkExperience == "Scrape Experience":
                browser.get(link)

                # Get list of Experiences
                experienceList = browser.find_elements_by_css_selector('.pv-entity__position-group-pager')
                print(len(experienceList))
                for expirence in experienceList:

                    # Print Firm Name
                    # Check if Post first or Company Name first
                    if len(expirence.find_elements_by_class_name('pv-entity__company-summary-info')) > 0:

                        ## If company info given
                        company = expirence.find_element_by_class_name('pv-entity__company-summary-info')
                        companyName = company.find_element_by_css_selector('.t-16.t-black.t-bold').text
                        companyExp = company.find_element_by_css_selector('.t-14.t-black.t-normal').text
                        workExp = workExp + ";" + companyName + " for " + companyExp

                    else:

                        companyName = expirence.find_element_by_class_name('pv-entity__secondary-title').text
                        companyExp = expirence.find_element_by_css_selector(
                            '.pv-entity__date-range.t-14.t-black--light.t-normal').text[15:]
                        workExp = workExp + ";" + companyName + " for " + companyExp

                browser.back()
                time.sleep(3)

            # Appending the row to the CSV
            if WorkExperience == "Scrape Experience":
                rowdata = [name, Post, Firm, location, "/images/" + imageName + ".jpg", link, pictureLink,
                           gender,
                           race, workExp]
            else:
                rowdata = [name, Post, Firm, location, "/images/" + imageName + ".jpg", link, pictureLink, gender,
                           race]
            with open(Title + Company + School + Location + WorkExperience + '.csv', 'a', newline='') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(rowdata)

            results = browser.find_elements_by_css_selector(
                '.search-result.search-result__occluded-item.ember-view')

        with open('logs/' + Title + Company + School + Location + WorkExperience + 'log.txt', 'w',
                  newline='') as logFile:
            logFile.write(browser.current_url)

        # nextButton = browser.find_element_by_class_name(
        #     'artdeco-button__text')
        # nextButton.click()
        currentUrl = browser.current_url
        if "&page=" in currentUrl:
            pageNum = currentUrl.split("&page=", 1)[1]
            page = int(pageNum) + 1
            currentUrl = currentUrl.split("&page=", 1)[0] + "&page=" + str(page)
            browser.get(currentUrl)
            with open('logs/' + Title + Company + School + Location + WorkExperience + 'log.txt', 'w',
                      newline='') as logFile:
                logFile.write(currentUrl)

        else:
            currentUrl = currentUrl + "&page=2"
            browser.get(currentUrl)
            with open('logs/' + Title + Company + School + Location + WorkExperience + 'log.txt', 'w',
                      newline='') as logFile:
                logFile.write(currentUrl)


    except Exception as E:
        print(E)
        relogin(browser, browser.current_url, 1)

# Check if the time is up
if mode == "1":
    if time.time() > wakeup:
        relogin(browser, browser.current_url, 30)
