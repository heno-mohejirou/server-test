import re
import unicodedata
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from operation.screen_operation import ScreenOperation
from selenium.webdriver.support.ui import WebDriverWait

# 問題回答クラス
class PressBottun(ScreenOperation):
    def __init__(self, driver):
        super().__init__(driver)

    # 問題文を編集
    @staticmethod
    def edit_question(text):
        text = unicodedata.normalize("NFKC", text or "")
        text = re.sub(r"\s+", " ", text).strip()
        return text.lower()

    # チェックボックス
    def click_checkbox(self, elem, keyword):
        keyword = self.edit_question(keyword)

        try:
            container = elem.find_element(By.XPATH, "./ancestor::div[contains(@class,'formulation')]")
            answer_container = container.find_element(By.XPATH, ".//div[contains(@class,'answer')]")
        except:
            return False

        candidates = answer_container.find_elements(By.XPATH, ".//*[self::div or self::p or self::label]")
        for c in candidates:
            txt = self.edit_question(c.text)
            if keyword in txt :
                try:
                    checkbox = c.find_element(By.XPATH, ".//input[@type='checkbox']")
                except:
                    continue
                
                WebDriverWait(self.driver, 10).until(
                    lambda d: d.execute_script(
                        "return arguments[0] && arguments[0].offsetParent !== null;",
                        checkbox
                    )
                )

                if not checkbox.is_selected():
                    self.driver.execute_script("arguments[0].click();", checkbox)

        return False
    
    # 入力ボックス
    def input_box(self, elem, target_text):
            input_box = elem.find_element(By.CSS_SELECTOR,"input.form-control.d-inline")
            # readonly属性がある場合に入力できないため、JavaScriptで直接valueを書き換える
            self.driver.execute_script("arguments[0].removeAttribute('readonly');", input_box)
            self.driver.execute_script("arguments[0].value = arguments[1];", input_box, target_text)
            
            # send_keysでも入力イベントを発火させておく（Moodle側の内部状態更新のため）
            try:
                input_box.clear()
                input_box.send_keys(target_text)
            except:
                pass

    # ラジオボタン
    def radio_bottun(self, elem, target_text):
            try:
                label_element = elem.find_element(By.XPATH, f".//following::label[normalize-space(text())='{target_text}']")
                for_attr = label_element.get_attribute("for")
                if for_attr:
                    radio_button = self.driver.find_element(By.ID, for_attr)
                else:
                    radio_button = label_element.find_element(By.XPATH, ".//ancestor::div/preceding-sibling::input[@type='radio'] | .//preceding-sibling::input[@type='radio']")
            except:
                try:
                    p_element = elem.find_element(By.XPATH, f".//following::p[normalize-space(text())='{target_text}']")
                    radio_button = p_element.find_element(By.XPATH, ".//ancestor::div/preceding-sibling::input[@type='radio']")
                except:
                    div_element = elem.find_element(By.XPATH, f".//following::div[normalize-space(text())='{target_text}']")
                    radio_button = div_element.find_element(By.XPATH, ".//ancestor::div/preceding-sibling::input[@type='radio']")

            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", radio_button)
            self.driver.execute_script("arguments[0].click();", radio_button)

    # プルダウンリスト
    def pull_down_lsit(self, target_text):
        rows = self.driver.find_elements(By.XPATH, "//tr[contains(@class,'r')]")

        for row in rows:
            txt = row.find_element(By.XPATH, ".//td[@class='text']").text.strip()
            answer = target_text.get(txt)

            try:
                select_elem = row.find_element(By.TAG_NAME, "select")
                select = Select(select_elem)
                select.select_by_visible_text(answer)
                            
            except Exception as e:
                print(f"[ERROR] セレクト失敗: {e}", flush=True)  