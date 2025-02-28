class Application:
    def __init__(self):
        from sample.database import Database
        from sample.service import UserService
        
        self.database = Database()
        self.user_service = UserService(self.database)
    
    def run(self):
        """アプリケーションを実行"""
        # ユーザーを作成
        user = self.user_service.create_user("John Doe", "john@example.com")
        print(f"Created user: {user.get_display_name()}")
        
        # ユーザー名を更新
        updated_user = self.user_service.update_user_name(1, "John Smith")
        if updated_user:
            print(f"Updated user name: {updated_user.get_display_name()}")
        
        # ユーザーを非アクティブ化
        user.deactivate()
        
        # 非アクティブユーザーを取得
        inactive_users = self._get_inactive_users()
        print(f"Found {len(inactive_users)} inactive users")
    
    def _get_inactive_users(self):
        """非アクティブユーザーの一覧を取得"""
        return [user for user in self.database.get_all_users() if not user.is_active]
