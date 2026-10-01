from operation.press_button import PressBottun
from operation.anser_question import AnserQuestion
from operation.browser_session import BrowserSession
from operation.screen_operation import ScreenOperation
from selenium.webdriver.common.by import By


def main(testnames, password, username, details):

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

        # testnames は ["前期中間までの課題1"] のようなリスト
        if isinstance(testnames, str):
            testnames = [testnames]

        # details は
        # ["Home", "商船学科2026", "２年", "S2-2026-英語表現"]
        # のようなリスト

        for testname in testnames:

            print(f"[TEST] testname: {testname}", flush=True)
            print(f"[TEST] details: {details}", flush=True)

            try:
                # Moodleトップへ戻る
                driver.get(browser.url)

                # 問題と回答データ取得
                pairs_json = ansque.test_json(testname)

                # detailsに従ってMoodle内を移動
                # 最後にtestnameのテストをクリック
                operation.course(
                    details,
                    testname
                )

                # テスト開始
                operation.quiz()
                operation.submit_page()

                # ==================================
                # 問題回答
                # ==================================
                while True:

                    for elem in ansque.get_question():

                        print(
                            f"[DEBUG] elem={elem}",
                            flush=True
                        )

                        target_text = ansque.get_anser(
                            elem,
                            pairs_json
                        )

                        if not target_text:
                            continue

                        # ----------------------------------
                        # 文字列
                        # ----------------------------------
                        if isinstance(target_text, str):

                            if target_text[0] == "@":

                                target_text = target_text[1:]

                                bottun.input_box(
                                    elem,
                                    target_text
                                )

                            else:

                                bottun.radio_bottun(
                                    elem,
                                    target_text
                                )

                        # ----------------------------------
                        # リスト
                        # ----------------------------------
                        elif isinstance(target_text, list):

                            if (
                                target_text
                                and target_text[0] == "!"
                            ):

                                options = target_text[1:]

                                clicked = False

                                # 完全一致を優先
                                for opt in options:

                                    if bottun.radio_bottun(
                                        elem,
                                        opt,
                                        fuzzy=False
                                    ):
                                        clicked = True
                                        break

                                # 見つからなければfuzzy
                                if not clicked:

                                    if bottun.radio_bottun(
                                        elem,
                                        options[-1],
                                        fuzzy=True
                                    ):
                                        clicked = True

                                # 最終フォールバック
                                if not clicked:

                                    print(
                                        "[WARNING] "
                                        f"全候補不一致、"
                                        f"最初のラジオを強制クリック: "
                                        f"{options}",
                                        flush=True
                                    )

                                    try:

                                        container = elem.find_element(
                                            By.XPATH,
                                            "./ancestor::div[contains(@class,'formulation')]"
                                        )

                                        radio_inputs = container.find_elements(
                                            By.XPATH,
                                            ".//input[@type='radio']"
                                        )

                                        if radio_inputs:

                                            driver.execute_script(
                                                "arguments[0].scrollIntoView({block:'center'});",
                                                radio_inputs[0]
                                            )

                                            driver.execute_script(
                                                "arguments[0].click();",
                                                radio_inputs[0]
                                            )

                                    except Exception as e:

                                        print(
                                            f"[WARNING ERROR] {e}",
                                            flush=True
                                        )

                            else:

                                for ans in target_text:

                                    bottun.click_checkbox(
                                        elem,
                                        ans
                                    )

                        # ----------------------------------
                        # プルダウン
                        # ----------------------------------
                        elif isinstance(target_text, dict):

                            bottun.pull_down_lsit(
                                target_text
                            )

                    # 次のページ
                    if not operation.next_page():
                        break

                # 回答送信
                operation.save()

                results_log.append(
                    f"{testname}: 完了しました"
                )

            except Exception as e:

                print(
                    f"Error in {testname}: {e}",
                    flush=True
                )

                import traceback
                traceback.print_exc()

                results_log.append(
                    f"{testname}: エラー発生 ({e})"
                )

        return "\n".join(results_log)

    except Exception as e:

        print(
            "main error:",
            e,
            flush=True
        )

        import traceback
        traceback.print_exc()

        return f"error {e}"

    finally:

        if browser:
            browser.quit()
