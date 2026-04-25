import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ブラウザ操作クラス
class BrowserSession:
    def __init__(self):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        url_path = os.path.join(root_dir, "data", "url.txt")

        with open(url_path, "r", encoding="utf-8") as f:
            self.url = f.readline().strip()

        self.driver = None

    # ブラウザ起動
    def boot(self):
        options = Options()

        options.binary_location = "/usr/bin/chromium"

        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = Service(executable_path="/usr/bin/chromedriver")  # ← ★これも重要

        self.driver = webdriver.Chrome(
            service=service, options=options)

        self.driver.get(self.url)

        return self.driver

    # ブラウザ終了
    def quit(self):
        if self.driver:
            self.driver.quit()

    # ログイン
    def login(self, username, password):
        driver = self.driver

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "ログイン"))
        ).click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )

        driver.find_element(By.ID, "username").clear()
        driver.find_element(By.ID, "username").send_keys(username)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        )

        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "password").send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(
            lambda d: "login" not in d.current_url.lower()
        )

















































































































































        # db.json_db(username, password)