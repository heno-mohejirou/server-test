from operation.press_button import PressBottun
from operation.anser_question import AnserQuestion
from operation.browser_session import BrowserSession
from operation.screen_operation import ScreenOperation

def main(testnames, password, username, grade):

    browser = None
    results_log = []

    print("[DEBUG] Calling main()...", flush=True)
    try:
        browser = BrowserSession()
        driver = browser.boot()
        browser.login(username, password)

        operation = ScreenOperation(driver)
        bottun = PressBottun(driver)
        ansque = AnserQuestion(driver)

        for testname in testnames:
            try:
                driver.get(browser.url)
                pairs_json = ansque.test_json(grade, testname)

                operation.course(grade, testname)
                operation.quiz()
                operation.submit_page()

                while True:
                    for elem in ansque.get_question():
                        print(f"[DEBUG] elem={elem}")
                        target_text = ansque.get_anser(elem, pairs_json)
                        
                        if not target_text:
                            continue

                        if isinstance(target_text, str):
                            if target_text[0] == "@":
                                target_text = target_text[1:]
                                bottun.input_box(elem, target_text)
                                
                            else:
                                bottun.radio_bottun(elem, target_text)

                        elif isinstance(target_text, list):
                            if target_text and target_text[0] == "!":
                                options = target_text[1:]
                                clicked = False
                                # まず全候補を fuzzy=False で完全一致のみ試す
                                for opt in options:
                                    if bottun.radio_bottun(elem, opt, fuzzy=False):
                                        clicked = True
                                        break
                                # 見つからなければ最後の候補だけ fuzzy=True で試す
                                if not clicked:
                                    if bottun.radio_bottun(elem, options[-1], fuzzy=True):
                                        clicked = True
                                # それでも見つからなければ強制クリック
                                if not clicked:
                                    print(f"[WARNING] 全候補不一致、最初のラジオを強制クリック: {options}", flush=True)
                                    try:
                                        container = elem.find_element(By.XPATH, "./ancestor::div[contains(@class,'formulation')]")
                                        radio_inputs = container.find_elements(By.XPATH, ".//input[@type='radio']")
                                        if radio_inputs:
                                            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", radio_inputs[0])
                                            driver.execute_script("arguments[0].click();", radio_inputs[0])
                                    except Exception as e:
                                        print(f"[WARNING ERROR] {e}", flush=True)
                            else:
                                for ans in target_text:
                                    bottun.click_checkbox(elem, ans)

                        elif isinstance(target_text, dict):
                            bottun.pull_down_lsit(target_text)

                    if not operation.next_page():
                        break

                operation.save()
                results_log.append(f"{testname}: 完了しました")

            except Exception as e:
                print(f"Error in {testname}: {e}", flush=True)
                import traceback
                traceback.print_exc()
                results_log.append(f"{testname}: エラー発生 ({e})")

        return "\n".join(results_log)

    except Exception as e:
        print("main error:", e, flush=True)
        import traceback
        traceback.print_exc()
        return f"error {e}"

    finally:
        if browser:
            browser.quit()
