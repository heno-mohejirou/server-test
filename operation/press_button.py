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
    
        def _find_radio_from_element(found_elem):
            try:
                parent_label = found_elem.find_element(By.XPATH, "ancestor::label[@for][1]")
                for_attr = parent_label.get_attribute("for")
                if for_attr:
                    return self.driver.find_element(By.ID, for_attr)
            except:
                pass
            try:
                elem_id = found_elem.get_attribute("id")
                if elem_id:
                    return self.driver.find_element(
                        By.XPATH, f".//input[@type='radio'][@aria-labelledby='{elem_id}']"
                    )
            except:
                pass
            try:
                labeled_ancestor = found_elem.find_element(By.XPATH, "ancestor::*[@id][1]")
                ancestor_id = labeled_ancestor.get_attribute("id")
                if ancestor_id:
                    return self.driver.find_element(
                        By.XPATH, f".//input[@type='radio'][@aria-labelledby='{ancestor_id}']"
                    )
            except:
                pass
            try:
                return found_elem.find_element(By.XPATH, "ancestor::*/preceding-sibling::input[@type='radio'][1]")
            except:
                pass
            return found_elem.find_element(By.XPATH, ".//ancestor::div/preceding-sibling::input[@type='radio']")
    
        # --- 完全一致 ---
        try:
            try:
                label_element = elem.find_element(By.XPATH, f".//following::label[normalize-space(.)='{target_text}']")
                for_attr = label_element.get_attribute("for")
                if for_attr:
                    radio_button = self.driver.find_element(By.ID, for_attr)
                else:
                    radio_button = _find_radio_from_element(label_element)
            except:
                try:
                    p_element = elem.find_element(By.XPATH, f".//following::p[normalize-space(.)='{target_text}']")
                    radio_button = _find_radio_from_element(p_element)
                except:
                    try:
                        div_element = elem.find_element(
                            By.XPATH,
                            f".//following::div[normalize-space(text())='{target_text}' or normalize-space(.)='{target_text}']"
                        )
                        radio_button = _find_radio_from_element(div_element)
                    except:
                        # <br> 混在ケース: innerText で比較
                        all_divs = elem.find_elements(By.XPATH, ".//following::div")
                        matched_div = None
                        for d in all_divs:
                            inner = self.driver.execute_script("return arguments[0].innerText;", d)
                            if inner and inner.strip() == target_text.strip():
                                matched_div = d
                                break
                        if matched_div is None:
                            raise Exception("div not found")
                        radio_button = _find_radio_from_element(matched_div)
    
            _try_click(radio_button)
            return True
        except:
            pass
    
        # --- ファジーマッチ ---
        if not fuzzy:
            return False
        try:
            # ★ radio_inputs と norm_target をここで定義（以前のコードでは順序が逆だった）
            container = elem.find_element(By.XPATH, "./ancestor::div[contains(@class,'formulation')]")
            answer_div = container.find_element(By.XPATH, ".//div[contains(@class,'answer')]")
            radio_inputs = answer_div.find_elements(By.XPATH, ".//input[@type='radio']")
    
            best_score = 0.0
            best_radio = None
            norm_target = self.edit_question(target_text)
            print(f"[FUZZY] norm_target='{norm_target}'", flush=True)
    
            for radio in radio_inputs:
                radio_id = radio.get_attribute("id")
                label_text = ""

                try:
                    lbl = self.driver.find_element(By.XPATH, f".//label[@for='{radio_id}']")
                    label_text = lbl.text.strip()
                except:
                    pass
    
                if not label_text:
                    try:
                        labelledby_id = radio.get_attribute("aria-labelledby")
                        if labelledby_id:
                            label_div = self.driver.find_element(By.ID, labelledby_id)
                            label_text = self.driver.execute_script(
                                "return arguments[0].innerText;", label_div
                            ).strip()
                    except:
                        pass
    
                if not label_text:
                    try:
                        label_text = radio.find_element(By.XPATH, "./following-sibling::*[1]").text.strip()
                    except:
                        pass
    
                if not label_text:
                    continue
    
                edited_label = self.edit_question(label_text)
                score = difflib.SequenceMatcher(None, norm_target, edited_label).ratio()
                print(f"[FUZZY] radio_id={radio_id} label='{label_text}' edited='{edited_label}' score={score:.2f}", flush=True)
                if score > best_score:
                    best_score = score
                    best_radio = radio
    
            if best_radio and best_score >= 0.4:
                print(f"[FUZZY] 選択 score={best_score:.2f} target='{target_text}'", flush=True)
                _try_click(best_radio)
                return True
            elif best_radio:
                # スコアが低くても best を押す
                print(f"[FUZZY] 低スコアで強制選択 score={best_score:.2f} target='{target_text}'", flush=True)
                _try_click(best_radio)
                return True
            else:
                # ラジオボタンが取得できなかった or スコアが低い場合
                # aria-labelledby のテキストで直接一致を試みる
                print(f"[FINAL FALLBACK] 全ラジオ数={len(radio_inputs)} target='{target_text}'", flush=True)
                for radio in radio_inputs:
                    try:
                        labelledby_id = radio.get_attribute("aria-labelledby")
                        if labelledby_id:
                            label_div = self.driver.find_element(By.ID, labelledby_id)
                            inner = self.driver.execute_script("return arguments[0].innerText;", label_div)
                            inner_clean = re.sub(r"\s+", "", (inner or "").strip())
                            target_clean = re.sub(r"\s+", "", target_text.strip())
                            print(f"[FINAL FALLBACK] inner_clean='{inner_clean}' target_clean='{target_clean}'", flush=True)
                            if inner_clean == target_clean:
                                print(f"[FINAL FALLBACK] 一致！クリック", flush=True)
                                _try_click(radio)
                                return True
                    except:
                        pass
                # それでも見つからなければ最初のラジオを押す
                if radio_inputs:
                    print(f"[FINAL FALLBACK] 強制的に最初のラジオをクリック", flush=True)
                    _try_click(radio_inputs[0])
                    return True
                return False
        except Exception as e:
            print(f"[FUZZY ERROR] {e}", flush=True)
            return False
            
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
