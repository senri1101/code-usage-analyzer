import os
import json
import tempfile
import shutil
from unittest import TestCase

class TestCodeAnalyzer(TestCase):
    def setUp(self):
        # テスト用の一時ディレクトリを作成
        self.temp_dir = tempfile.mkdtemp()
        
        # サンプルコードディレクトリを作成
        self.sample_dir = os.path.join(self.temp_dir, "sample")
        os.makedirs(self.sample_dir)
        
        # サンプルコードファイルを作成
        self.create_sample_files()
    
    def tearDown(self):
        # テスト後に一時ディレクトリを削除
        shutil.rmtree(self.temp_dir)
    
    def create_sample_files(self):
        # テスト用のサンプルコードを作成
        model_code = """
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.is_active = True
    
    def get_display_name(self):
        return self.name
    
    def deactivate(self):
        self.is_active = False
        self._log_status_change("deactivated")
    
    def activate(self):
        self.is_active = True
        self._log_status_change("activated")
    
    def _log_status_change(self, status):
        print(f"User {self.name} was {status}")
    
    def _get_timestamp(self):
        import datetime
        return datetime.datetime.now()
"""
        
        service_code = """
class UserService:
    def create_user(self, name, email):
        from sample.model import User
        user = self._build_user(name, email)
        return user
    
    def _build_user(self, name, email):
        from sample.model import User
        return User(name, email)
"""
        
        # ファイルに書き込み
        with open(os.path.join(self.sample_dir, "model.py"), "w") as f:
            f.write(model_code)
        
        with open(os.path.join(self.sample_dir, "service.py"), "w") as f:
            f.write(service_code)
    
    def test_analyzer(self):
        # コード解析スクリプトのパス（実際のファイルパスに置き換えてください）
        analyzer_path = "../code_analyzer.py"
        
        # 出力ファイルパス
        output_path = os.path.join(self.temp_dir, "results.json")
        
        # 解析コマンドを実行
        import subprocess
        result = subprocess.run(
            ["python", analyzer_path, self.sample_dir, "--output", output_path],
            capture_output=True,
            text=True
        )
        
        # 正常終了を確認
        self.assertEqual(result.returncode, 0, f"Analyzer failed: {result.stderr}")
        
        # 出力ファイルが存在することを確認
        self.assertTrue(os.path.exists(output_path), "Output file was not created")
        
        # 結果を読み込み
        with open(output_path, "r") as f:
            candidates = json.load(f)
        
        # 結果を検証
        # 期待される候補：
        # - User._log_status_change (deactivate と activate から呼ばれる)
        # - User._get_timestamp (一回も呼ばれていない)
        # - UserService._build_user (create_user から呼ばれる)
        
        # 少なくとも候補があることを確認
        self.assertGreater(len(candidates), 0, "No candidates found")
        
        # メソッド名のリスト
        method_names = [c["method"] for c in candidates]
        
        # 期待されるメソッドが候補に含まれているか確認
        self.assertIn("_build_user", method_names, "_build_user should be a candidate")
        
        # プライベートメソッドの数を確認
        private_methods = [m for m in method_names if m.startswith("_")]
        self.assertGreater(len(private_methods), 0, "No private methods found")
