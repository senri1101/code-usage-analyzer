
class UserService:
    def __init__(self, database):
        self.database = database
    
    def create_user(self, name, email):
        """新しいユーザーを作成"""
        user = self._build_user(name, email)
        self.database.save(user)
        return user
    
    def _build_user(self, name, email):
        """ユーザーオブジェクトを構築"""
        from sample.model import User
        return User(name, email)
    
    def get_user_by_email(self, email):
        """メールアドレスでユーザーを検索"""
        return self.database.find_by_email(email)
    
    def update_user_name(self, user_id, new_name):
        """ユーザー名を更新"""
        user = self.database.find_by_id(user_id)
        if user:
            user.name = new_name
            self.database.save(user)
            self._notify_update(user)
        return user
    
    def _notify_update(self, user):
        """更新通知を送信"""
        print(f"User {user.name} was updated")
