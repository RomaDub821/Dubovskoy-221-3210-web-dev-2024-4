from flask_login import current_user

class UsersPolicy:
    def __init__(self, user=None):
        self.user = user

    def create(self):
        return current_user.role_id == 3 

    def delete(self):
        return current_user.role_id == 3

    def edit(self):
        return self.user.id == current_user.id or current_user.role_id == 3

    def show(self):
        return self.user.id == current_user.id or current_user.role_id == 3 

    def assign_roles(self):
        return current_user.role_id == 3 