from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ScreenOperation:
    def __init__(self, driver):
        self.driver = driver

    # 画面最下部までのスクロール
    def scroll(self, max_try=2):
        driver = self.driver
        last_height = driver.execute_script(
            "return document.body.scrollHeight"
        )

        for _ in range(max_try):
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            try:
                WebDriverWait(driver, 1).until(
                    lambda d: d.execute_script(
                        "return document.body.scrollHeight"
                    ) != last_height
                )
            except:
                break

            last_height = driver.execute_script(
                "return document.body.scrollHeight"
            )

    # 始めのページ遷移
    def submit_page(self):
        try:
            btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "submitbutton"))
            )
        except:
            return False

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", btn
        )
        self.driver.execute_script("arguments[0].click();", btn)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class,'formulation')]")
            )
        )

        return True
    
    # ページ遷移
    def next_page(self):
        try:
            btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "next"))
            )
        except:
            return False

        value = (btn.get_attribute("value") or "").strip()

        if value in ("次のページ", "Next page"):
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", btn
            )
            self.driver.execute_script("arguments[0].click();", btn)
            return True

        return False

    # 問題遷移
    def course(self, grade, testname):
        driver = self.driver

        """２年生コース"""
        if grade == "sophomore":
            links = ["Home", "商船学科2026", "２年", "S2-2026-英語表現"]

        """３年生コース"""
        if grade == "junior":
            links = ["Home", "情報工学科2026", "３年", "I3-2026-英語表現"]

        for link in links:
            try:
                elem = WebDriverWait(driver, 10).until(
                    lambda d: d.find_element(By.LINK_TEXT, link)
                )
            except:
                raise RuntimeError(f"リンクが見つかりません: {link}")

            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", elem
            )
            driver.execute_script("arguments[0].click();", elem)

        try:
            elem = WebDriverWait(driver, 10).until(
                lambda d: d.find_element(
                    By.XPATH, f"//a[contains(., '{testname}')]"
                )
            )
        except:
            raise RuntimeError(f"テストが見つかりません: {testname}")

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", elem
        )
        driver.execute_script("arguments[0].click();", elem)

    # 回答送信
    def save(self):
        self.scroll()

        primary = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".btn.btn-primary")
            )
        )
        primary.click()

        self.scroll()

        primary = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".btn.btn-primary")
            )
        )
        primary.click()
        
        save = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[data-action="save"]')
            )
        )
        save.click()

    # 問題開始
    def quiz(self):
        button = self.driver.find_element(By.CSS_SELECTOR, ".btn.btn-primary")
        button.click()
        next_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.NAME, "submitbutton")
            )
        )
        next_button.click()