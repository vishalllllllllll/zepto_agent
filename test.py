from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument(r"--user-data-dir=C:\Users\Visha\vscode project files\zepto_agent\chrome_profile")
options.add_experimental_option("detach", True)  # <-- keeps Chrome open
driver = webdriver.Chrome(options=options)
driver.get("https://www.zeptonow.com/")
