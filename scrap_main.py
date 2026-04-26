from operation.press_button import PressBottun
from operation.anser_question import AnserQuestion
from operation.browser_session import BrowserSession
from operation.screen_operation import ScreenOperation

def main(testnames, password, username, grade):

    browser = None

    try:
        for testname in testnames:
            print("[DEBUG] Calling BrowserSession()...")
            browser = BrowserSession()
            print("[DEBUG] Calling browser.boot()...")
            driver = browser.boot()

            operation = ScreenOperation(driver)
            bottun = PressBottun(driver)
            ansque = AnserQuestion(driver)

            print(f"[DEBUG] grade= {grade}")

            if grade == "0":
                grade = "sophomore"
            else:
                grade = "junior"

            print(f"[DEBUG] grade= {grade}")
            
            pairs_json = ansque.test_json(grade, testname)

            print("[DEBUG] Calling browser.login()...")
            browser.login(username, password)
            print("[DEBUG] Calling operation.course()...")
            operation.course(grade, testname)

            operation.quiz()
            operation.submit_page()

            while True:
                for elem in ansque.get_question():
                    target_text = ansque.get_anser(elem, pairs_json)
                    
                    if not target_text:
                        continue

                    if isinstance(target_text, str):
                        if target_text[0] == "@":
                            target_text = target_text[1:]
                            bottun.input_box(target_text)
                            
                        else:
                            bottun.radio_bottun(elem, target_text)

                    elif isinstance(target_text, list):
                        for ans in target_text:
                            bottun.click_checkbox(elem, ans)

                    elif isinstance(target_text, dict):
                        bottun.pull_down_lsit(target_text)

                if not operation.next_page():
                    break

            # print("[DEBUG] Callong operation.save()...")
            operation.save()

            # print("[DEBUG] Callong browser.quit()...")
            browser.quit()

            browser = None

        return "complet"

    except Exception as e:
        print("main error:", e)
        return f"error {e}"

    finally:
        if browser:
            browser.quit()