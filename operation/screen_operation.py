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
            # Confirmation modal might not appear if there is no time limit
            btn = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.NAME, "submitbutton"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            self.driver.execute_script("arguments[0].click();", btn)
        except:
            pass  # It's fine if the modal does not exist

        try:
            # Wait for formulation (questions div) to confirm the test has successfully started
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'formulation')]"))
            )
            return True
        except:
            print("[ERROR] 'formulation' class not found, test might not have started correctly.", flush=True)
            return False
    
    # ページ遷移
    def next_page(self):
        try:
            # 確実な「次のページ」ボタンを探す（Finish attempt は対象外にするため明示的にテキストを見る）
            xpath = "//*[self::button or self::input or self::a][contains(text(), '次のページ') or contains(text(), 'Next page') or contains(text(), '次ページ') or contains(text(), '次へ') or @value='次のページ' or @value='Next page' or @value='次ページ' or @value='次へ']"
            btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            self.driver.execute_script("arguments[0].click();", btn)
            
            # DOMリフレッシュのために待機
            import time
            time.sleep(3)
            return True
        except:
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

        # Step 1: Click "Finish attempt..."
        try:
            # Try by NAME "next" first (commonly used for Finish attempt at the bottom of the last page)
            btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.NAME, "next"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            self.driver.execute_script("arguments[0].click();", btn)
        except:
            try:
                # Fallback to CSS class if "next" is not present
                primary = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".mod_quiz-next-nav"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", primary)
                self.driver.execute_script("arguments[0].click();", primary)
            except Exception as e:
                print(f"[ERROR] Could not click 'Finish attempt': {e}", flush=True)

        self.scroll()

        # Step 2: Click "Submit all and finish"
        try:
            # Look for button/input by text (解答を送信 or すべてを送信), or fallback to ANY btn-primary
            submit_xpath = "(//button[contains(text(), '解答を送信') or contains(text(), 'すべてを送信') or contains(text(), 'Submit all and finish')] | //input[contains(@value, '解答を送信') or contains(@value, 'すべてを送信') or contains(@value, 'Submit all and finish')] | //button[contains(@class, 'btn-primary')])[last()]"
            primary = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, submit_xpath))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", primary)
            self.driver.execute_script("arguments[0].click();", primary)
        except Exception as e:
            print(f"[ERROR] Could not click 'Submit all and finish': {e}", flush=True)
        
        # Step 3: Click confirmation modal "Submit all and finish"
        try:
            confirm_xpath = "(//button[@data-action='save'] | //button[contains(text(), '解答を送信') or contains(text(), 'すべてを送信') or contains(text(), 'Submit all and finish')])[last()]"
            save_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, confirm_xpath))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
            self.driver.execute_script("arguments[0].click();", save_btn)
        except Exception as e:
            print(f"[ERROR] Could not click final confirmation: {e}", flush=True)

    # 問題開始
    def quiz(self):
        try:
            # Click "Attempt quiz now" or similar
            button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btn-primary"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", button)
            self.driver.execute_script("arguments[0].click();", button)
        except Exception as e:
            print(f"[WARNING] Could not click 'Attempt quiz' button: {e}", flush=True)