import json

def test_it():
    import os
    from operation.anser_question import AnserQuestion
    from unittest.mock import MagicMock
    
    # Mocking driver
    mock_driver = MagicMock()
    ansque = AnserQuestion(mock_driver)
    
    grade = "sophomore"
    testname = "後期中間までの課題1（U.3の復習）"
    
    try:
        pairs_json = ansque.test_json(grade, testname)
        print("Success, pairs keys are:")
        print(list(pairs_json.keys()))
    except Exception as e:
        print("Error details:", repr(e))

if __name__ == "__main__":
    test_it()
