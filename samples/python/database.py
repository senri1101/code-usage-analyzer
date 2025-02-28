class Database:
    def __init__(self):
        self.users = {}
        self.next_id = 1
    
    def save(self, user):
        """ユーザーを保存"""
        if not hasattr(user, 'id'):
            user.id = self.next_id
            self.next_id += 1
        
        self.users[user.id] = user
        return user
    
    def find_by_id(self, user_id):
        """IDでユーザーを検索"""
        return self.users.get(user_id)
    
    def find_by_email(self, email):
        """メールアドレスでユーザーを検索"""
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def get_all_users(self):
        """全ユーザーを取得"""
        return list(self.users.values())
    
    def clear(self):
        """全データを削除"""
        self.users.clear()
        self._reset_id_counter()
    
    def _reset_id_counter(self):
        """IDカウンターをリセット"""
        self.next_id = 1