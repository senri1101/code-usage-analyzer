class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.is_active = True
    
    def get_display_name(self):
        """ユーザーの表示名を取得"""
        return self.name
    
    def deactivate(self):
        """ユーザーを非アクティブ化"""
        self.is_active = False
        self._log_status_change("deactivated")
    
    def activate(self):
        """ユーザーをアクティブ化"""
        self.is_active = True
        self._log_status_change("activated")
    
    def _log_status_change(self, status):
        """ステータス変更をログに記録 (内部メソッド)"""
        print(f"User {self.name} was {status} at {self._get_timestamp()}")
    
    def _get_timestamp(self):
        """現在のタイムスタンプを取得 (内部メソッド)"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
