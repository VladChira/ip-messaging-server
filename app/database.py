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
        role=Role.ADMIN,
        createdAt=datetime.datetime(2023, 1, 15, 10, 30, 0)
    )

    user2 = User(
        userId=3,
        name="Charlie Brown",
        email="charlie.brown@example.com",
        username="charlie",
        password="PasswordForCharlie",
        role=Role.USER
    )

    user3 = User(
        userId=4,
        name="Diana Prince",
        email="diana.prince@example.com",
        username="diana",
        password="WonderWoman123",
        role=Role.USER
    )

    user4 = User(
        userId=5,
        name="Eve Polastri",
        email="eve.polastri@example.com",
        username="eve",
        password="KillingEve456",
        role=Role.USER
    )

    user5 = User(
        userId=6,
        name="Frank Castle",
        email="frank.castle@example.com",
        username="punisher",
        password="Punisher789",
        role=Role.USER
    )

    user6 = User(
        userId=7,
        name="Grace Hopper",
        email="grace.hopper@example.com",
        username="grace",
        password="CodePioneer101",
        role=Role.ADMIN
    )

    users.append(user1)
    users.append(admin_user)
    users.append(user2)
    users.append(user3)
    users.append(user4)
    users.append(user5)
    users.append(user6)
