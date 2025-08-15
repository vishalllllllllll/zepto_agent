from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument(r"your-chrome-profile-path")
options.add_experimental_option("detach", True)  # <-- keeps Chrome open
driver = webdriver.Chrome(options=options)
driver.get("https://www.zeptonow.com/")

