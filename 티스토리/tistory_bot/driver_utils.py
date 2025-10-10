from selenium import webdriver

def init_driver(headless=False):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    return driver
