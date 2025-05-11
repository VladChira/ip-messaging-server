from app.user import User, Role
import datetime

users = []


def create_users():
    user1 = User(
            userId=1,
            name="Alice Wonderland",
            email="alice@example.com",
            username="alice",
            password="SecurePassword123",
            role=Role.USER
        )

    admin_user = User(
            userId=2,
            name="Bob The Admin",
            email="bob.admin@example.com",
            username="admin_bob",
            password="SuperSecretAdminPassword!",
            status="active",
            role=Role.ADMIN, # Can pass the enum member directly
            createdAt=datetime.datetime(2023, 1, 15, 10, 30, 0)
        )
    
    users.append(user1)
    users.append(admin_user)