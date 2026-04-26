import os
import re
import json

from selenium.webdriver.common.by import By
from operation.screen_operation import ScreenOperation
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 問題文取得クラス
class AnserQuestion(ScreenOperation):
    def __init__(self, driver):
        super().__init__(driver)

    # 問題名から回答を取得
    def test_json(self, grade, testname):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ansque_path = os.path.join(root_dir, "data", "tests.json")
        try:
            with open(ansque_path, "r", encoding="utf-8") as f:
                json_obj = json.load(f)
        except Exception as e:
            print(f"JSON Load error: {e}", flush=True)
            raise e

        print(f"grade = {grade}", flush=True)
        print(f"testname = {testname}", flush=True)
        print(f"available grades = {list(json_obj.keys())}", flush=True)
        print(f"available tests = {list(json_obj.get(grade, {}).keys())}", flush=True)

        if testname not in json_obj.get(grade, {}):
            print(f"Error: testname '{testname}' not found in grade '{grade}'", flush=True)
            raise KeyError(f"testname '{testname}' not found in grade '{grade}'")


        # print(f"[DEBUG] json_obj={json_obj}")
        # print(f"[DEBUG] grade={grade}")

        pairs_json = json_obj[grade][testname]
        return pairs_json
    
    # 問題文の取得
    def get_question(self):
        elem = self.driver.find_elements(By.XPATH, "//div[@class='qtext']")
        return elem

    # 回答の取得
    def get_anser(self, elem, pairs_json):
        lines = elem.text.strip().split("\n")
        #print(f"[DEBUG] lines={lines}")

        """問題文の行数"""
        if len(lines) >= 3 and "1つ選択してください:" not in lines:         # ３行以上なら２行目を取得
            lines = [i for i in lines if i != '' or ""]
            #print(f"[DEBUG] lines={lines}")

            target_line = lines[1]
        else:                       # １行目を取得
            target_line = lines[0]

        #print(f"[DEBUG] target_line={target_line}")

        word_text = re.sub(r"\s+", " ", target_line).strip()

        #print(f"[DEBUG] word_text={word_text}")

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", elem
        )

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(elem)
        )

        target_text = pairs_json.get(word_text)
        #print(f"[DEBUG] terget_text={target_text}")

        return target_text