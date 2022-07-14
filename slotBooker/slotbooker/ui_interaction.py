from calendar import weekday
from pickle import NONE
from xml.etree.ElementPath import xpath_tokenizer
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from datetime import date 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .helper_functions import get_day, get_day_button, _get_booking_slot



def login(driver: object, base_url: str, username: str, password: str) -> None:  
  driver.get(base_url)
  
  # HERE GOES YOUR CUSTOMIZED INTERACTIVE LOGIN
  xpath_login_one_head = "/html/body/div/div[3]/div/div/div/div/div/div/form"
  xpath_login_two_head = "/html/body/div[1]/div[3]/div/div/div/div/div/div/form"

  # username field
  driver.find_element(By.XPATH, f"{xpath_login_one_head}/div[1]/input").send_keys(username)
  driver.find_element(By.XPATH, f"{xpath_login_one_head}/button").send_keys(Keys.RETURN)
  print("> submit user name successful")

  # password field
  WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, f"{xpath_login_two_head}/div[2]/input"))).send_keys(password)
  # checkbox  
  driver.find_element(By.XPATH, f"{xpath_login_two_head}/div[3]/div/div/div[1]/div/i").click()
  # submit
  driver.find_element(By.XPATH, f"{xpath_login_two_head}/button").send_keys(Keys.RETURN)
  print("> login successful")



def book_slot(driver: object, days_before_bookable: int, booking_action : bool = True) -> None:
  day, next_week = get_day(days_before_bookable)
  print(next_week)
  if next_week:
      xpath_next_week = '/html/body/div/div[5]/div/div[3]/div[9]/div/div/i'
      WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath_next_week))).click()
      print("- switched to next week")

  day_button = get_day_button(day)
  print(f"- booking for {day}")
  WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, day_button))).click()
  # driver.find_element(By.XPATH, friday_button).send_keys(Keys.RETURN)
  print(f"- day booked")

  # /html/body/div/div[5]/div/div[5]/div/div[1]
  # /html/body/div/div[5]/div/div[5]/div/div[1]/div[2]/p[1]
  # /html/body/div/div[5]/div/div[5]/div/div[1]/div[2]/p[2]
  # button to book
  # /html/body/div/div[5]/div/div[5]/div/div[1]/div[3]/button

  # /html/body/div/div[5]/div/div[6]/div/div[1]

  # find all with class = sc-bdfBQB hZKnCW
  
  #my_element = driver.find_element(By.XPATH, "//*[text()='Kaja Nows']")
  #print(my_element.text)
  test = "/html/body/div/div[5]/div/div"
  name = "sc-bdfBQB hZKnCW"
  WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, test)))
  
  my_elements = driver.find_elements(By.XPATH, test)
  #print(my_elements)

  def possible_slot(class_name : str):
    print("possible bookings")
    ls = []
    for i in range(len(my_elements)):
      xpath_test = f"/html/body/div/div[5]/div/div[{i}]/div/div[1]/div[2]/p[1]"
      try:
        if driver.find_element(By.XPATH, xpath_test).text == class_name:
          time = f"/html/body/div/div[5]/div/div[{i}]/div/div[1]/div[1]/p[1]"
          print(f"{i} - {driver.find_element(By.XPATH, time).text}")
          ls.append(i)
      except:
        continue
    return ls
  lists = possible_slot(class_name="Open Gym")
  print(lists)

  def book_slot(index):
  # button to book
    # button_book = /html/body/div/div[5]/div/div[5]/div/div[1]/div[3]/button
    # driver.find_element(By.XPATH, button_book).click()
    pass

      #print(i)
  #for i in my_elements:
  #  print(i)#f"/html/body/div/div[5]/div/div[{i}]/div/div[1]/div[2]/p[1]"
  # my_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Kaja Nows')]").click()
  #print(my_element)
  #print("Element with text(): " + e.getText() );
    
  
  # slot_action = _get_booking_slot(day, booking_action)
  # there is a popup happening I need to resolve..

  # WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH, slot_action))).click()
  # print("booked slot")

  #  driver.find_element(By.XPATH, slot).send_keys(Keys.RETURN)
  # /html/body/div/div[5]/div/div[8]/div/div[1]/div[3]/button
  # wenn nächste woche, dann
  #driver.find_element(By.XPATH, "/html/body/div/div[5]/div/div[3]/div[9]/div/div/i").send_keys(Keys.RETURN)


  #/html/body/div/div[5]/div/div[8]/div/div[1]/div[3]/button
    
  # sunday_button = "/html/body/div/div[5]/div/div[3]/div[7]/div/p"
  driver.find_element(By.XPATH, "xyz").click()

