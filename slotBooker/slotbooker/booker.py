import os
import yaml

from .driver import get_driver, close_driver
from .ui_interaction import login, book_slot


config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
config = yaml.safe_load(open(config_path))

# insert main function
def main():
  driver = get_driver(chromedriver=config.get('chromedriver'))
  login(driver, \
    base_url=config.get('base_url'), \
    username=config.get('email'), \
    password=config.get('password'))
  book_slot(driver, \
    days_before_bookable=config.get('days_before_bookable'))
  close_driver(driver)

if __name__ == '__main__':
  main()