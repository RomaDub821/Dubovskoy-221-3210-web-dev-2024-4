from flask_login import current_user

class UsersPolicy:
    def __init__(self, user=None):
        self.user = user

    def create(self):
        return current_user.role_id == 3  # Admin role

    def delete(self):
        return current_user.role_id == 3  # Admin role

    def edit(self):
        return self.user.id == current_user.id or current_user.role_id == 3  # Admin or self

    def show(self):
        return self.user.id == current_user.id or current_user.role_id == 3  # Admin or self

    def assign_roles(self):
        return current_user.role_id == 3  # Admin role
