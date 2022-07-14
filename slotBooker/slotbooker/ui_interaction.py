from calendar import weekday
from pickle import NONE
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from datetime import date 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .helper_functions import get_button_day, _get_slot



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



def book_slot(driver: object, book : bool = True) -> None:
  day_button, future_day = get_button_day(1)
  print("- got button")
  WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, day_button))).click()
  # driver.find_element(By.XPATH, friday_button).send_keys(Keys.RETURN)
  print(f"- selected day: {future_day}")


  slot_action = _get_slot(future_day, book)
  # there is a popup happening I need to resolve..

  WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH, slot_action))).click()
  print("booked slot")

  #  driver.find_element(By.XPATH, slot).send_keys(Keys.RETURN)
  # /html/body/div/div[5]/div/div[8]/div/div[1]/div[3]/button
  # wenn nächste woche, dann
  #driver.find_element(By.XPATH, "/html/body/div/div[5]/div/div[3]/div[9]/div/div/i").send_keys(Keys.RETURN)


  #/html/body/div/div[5]/div/div[8]/div/div[1]/div[3]/button
    
  # sunday_button = "/html/body/div/div[5]/div/div[3]/div[7]/div/p"
  # driver.find_element(By.XPATH, "xyz").click()

