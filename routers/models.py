# models.py
from flask_login import UserMixin
from werkzeug.security import check_password_hash

class SystemUser(UserMixin):
    def __init__(self, id, username, password, roles):
        self.id = id
        self.username = username
        self.password = password
        self.roles = roles
    
    def check_password(self, password):
        password_check = check_password_hash(self.password, password)
        print(f'Password {self.password} and {password} Check {password_check}')
        return password_check
    
    def get_id(self):
        return str(self.username)
    
    @property
    def get_roles(self):
        return self.roles
