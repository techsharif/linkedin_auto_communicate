from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import SearchForm
from .models import *

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

from getpass import getpass
import sys
import re
import time


def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            searchname = form.cleaned_data.get('search_name')
            keyword = form.cleaned_data.get('keyword')

            driver = webdriver.Firefox(executable_path='D:\SQTechnology\Projects\development\geckodriver.exe')
            driver.get("https://www.linkedin.com")
            # wait = WebDriverWait(driver, 5)

            # search connection
            search_input = driver.find_element_by_xpath("/html/body/nav/div/form/div/div/div/artdeco-typeahead-deprecated/artdeco-typeahead-deprecated-input/input")
            search_input.clear()
            search_input.send_keys(keyword)
            search_input.send_keys(Keys.ENTER)
            print("-------click search button-----------")

            print(searchname)

            for i in range(2):
                time.sleep(5)
                driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(5)

                actor_name_lists = driver.find_elements_by_class_name("actor-name")
                actor_title_company_lists = driver.find_elements_by_class_name("subline-level-1")
                actor_location_lists = driver.find_elements_by_class_name("subline-level-2")

                for actor_name_list in actor_name_lists:
                    actor_name = actor_name_list.text
                    print (actor_name.encode('utf-8'))

                for actor_title_company_list in actor_title_company_lists:
                    actor_title_company = actor_title_company_list.text
                    if " at " in actor_title_company:
                        title_company = actor_title_company.split(" at ")
                        actor_title = title_company[0]
                        actor_company = title_company[1]
                        print (actor_company)
                        print (actor_title)

                for actor_location_list in actor_location_lists:
                    actor_location = actor_location_list.text
                    print (actor_location)

                # store DB

                driver.find_element_by_class_name("next").click()
    else:
        form = SearchForm()
    return render(request, 'connector/search.html', {'form': form})
            