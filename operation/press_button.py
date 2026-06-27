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
            try:
                # 親要素（formulation）全体から探す（qtextの外にinputがあるケースに対応）
                container = elem.find_element(By.XPATH, "./ancestor::div[contains(@class,'formulation')]")
                input_box = container.find_element(By.CSS_SELECTOR, "input[type='text']")
            except:
                try:
                    # followingを使ってqtext以降に出現する最初のinputを探す
                    input_box = elem.find_element(By.XPATH, ".//following::input[@type='text'][1]")
                except:
                    # 最終的なフォールバック（elem内部）
                    input_box = elem.find_element(By.CSS_SELECTOR, "input.form-control.d-inline")

            # 要素が見える位置までスクロール
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", input_box)
            
            # value属性がない初期状態でも強制的に設定し、入力イベントを発生させる
            self.driver.execute_script("""
                arguments[0].removeAttribute('readonly');
                arguments[0].value = arguments[1];
                arguments[0].setAttribute('value', arguments[1]);
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, input_box, target_text)
            
            # Seleniumの通常のキー入力も行う
            try:
                input_box.click()
                input_box.clear()
                input_box.send_keys(target_text)
            except:
                pass
                
    # ラジオボタン（完全一致 → ファジーマッチのフォールバック付き）
    def radio_bottun(self, elem, target_text, fuzzy=True):
        import difflib

        def _try_click(radio_button):
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", radio_button)
            self.driver.execute_script("arguments[0].click();", radio_button)

        # formulation内のラジオを全取得
        try:
            container = elem.find_element(By.XPATH, "./ancestor::div[contains(@class,'formulation')]")
            radio_inputs = container.find_elements(By.XPATH, ".//input[@type='radio']")
            print(f"[RADIO] ラジオ数={len(radio_inputs)} target='{target_text}'", flush=True)
        except Exception as e:
            print(f"[RADIO] formulation取得失敗: {e}", flush=True)
            return False

        if not radio_inputs:
            print(f"[RADIO] ラジオなし", flush=True)
            return False

        target_clean = re.sub(r"\s+", "", target_text.strip())

        # --- aria-labelledby で直接テキスト一致 ---
        for radio in radio_inputs:
            try:
                labelledby_id = radio.get_attribute("aria-labelledby")
                if labelledby_id:
                    label_div = self.driver.find_element(By.ID, labelledby_id)
                    inner = self.driver.execute_script("return arguments[0].innerText;", label_div)
                    inner_clean = re.sub(r"\s+", "", (inner or "").strip())
                    print(f"[RADIO] aria inner='{inner_clean}' target='{target_clean}'", flush=True)
                    if inner_clean == target_clean:
                        print(f"[RADIO] 一致！クリック", flush=True)
                        _try_click(radio)
                        return True
            except Exception as e:
                print(f"[RADIO] aria取得失敗: {e}", flush=True)

        # --- label テキスト一致 ---
        for radio in radio_inputs:
            try:
                radio_id = radio.get_attribute("id")
                lbl = self.driver.find_element(By.XPATH, f".//label[@for='{radio_id}']")
                lbl_clean = re.sub(r"\s+", "", lbl.text.strip())
                if lbl_clean == target_clean:
                    print(f"[RADIO] label一致！クリック", flush=True)
                    _try_click(radio)
                    return True
            except:
                pass

        # --- ファジーマッチ ---
        if fuzzy:
            norm_target = self.edit_question(target_text)
            best_score = 0.0
            best_radio = None
            for radio in radio_inputs:
                label_text = ""
                try:
                    labelledby_id = radio.get_attribute("aria-labelledby")
                    if labelledby_id:
                        label_div = self.driver.find_element(By.ID, labelledby_id)
                        label_text = self.driver.execute_script("return arguments[0].innerText;", label_div).strip()
                except:
                    pass
                if not label_text:
                    try:
                        radio_id = radio.get_attribute("id")
                        lbl = self.driver.find_element(By.XPATH, f".//label[@for='{radio_id}']")
                        label_text = lbl.text.strip()
                    except:
                        pass
                if not label_text:
                    continue
                edited = self.edit_question(label_text)
                score = difflib.SequenceMatcher(None, norm_target, edited).ratio()
                print(f"[FUZZY] label='{label_text}' score={score:.2f}", flush=True)
                if score > best_score:
                    best_score = score
                    best_radio = radio

            if best_radio:
                print(f"[FUZZY] 選択 score={best_score:.2f}", flush=True)
                _try_click(best_radio)
                return True

        # --- 最終フォールバック: 最初のラジオを押す ---
        print(f"[FALLBACK] 最初のラジオを強制クリック", flush=True)
        _try_click(radio_inputs[0])
        return True
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
