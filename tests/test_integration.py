import os
import sys
import json
from unittest import TestCase, main

# テスト対象のモジュールへのパスを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# テスト対象のモジュールをインポート
from code_analyzer import CodeAnalyzer, FunctionInfo

class TestIntegration(TestCase):
    def test_find_private_candidates(self):
        # テスト用のダミーデータを作成
        analyzer = CodeAnalyzer("dummy_path")
        
        # 関数定義を手動で追加
        analyzer.functions = [
            FunctionInfo(name="public_method", file="test.py", class_name="TestClass", lineno=10),
            FunctionInfo(name="_private_method", file="test.py", class_name="TestClass", lineno=20),
            FunctionInfo(name="unused_method", file="test.py", class_name="TestClass", lineno=30),
        ]
        
        # 呼び出しを手動で追加
        analyzer.calls = [
            # public_method は複数回呼ばれる
            ("test.py", "public_method", "TestClass", "test.py", "OtherClass", "some_function"),
            ("test.py", "public_method", "TestClass", "other.py", None, "external_function"),
            
            # _private_method は一回だけ呼ばれる (同じファイル内から)
            ("test.py", "_private_method", "TestClass", "test.py", "TestClass", "public_method"),
        ]
        
        # プライベートメソッド候補を取得
        candidates = analyzer.find_private_candidates()
        
        # 結果を検証
        self.assertEqual(len(candidates), 1, "Should find exactly one candidate")
        self.assertEqual(candidates[0]["method"], "_private_method", "Wrong method identified")
        self.assertEqual(candidates[0]["class"], "TestClass", "Wrong class identified")


if __name__ == "__main__":
    main()