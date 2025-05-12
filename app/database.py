from app.user import User, Role
from app.friendship import Friendship
from app.friendrequest import FriendRequest, RequestStatus
import datetime

users = []
friendships = []
friendrequests = []

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

def create_friendships():

    # Create Friendship objects instead of dictionaries
    friendship1 = Friendship(
        friendshipId=1,
        user1Id=1, # Alice
        user2Id=3, # Charlie
        createdAt=datetime.datetime(2023, 2, 20, 14, 0, 0)
    )

    friendship2 = Friendship(
        friendshipId=2,
        user1Id=1, # Alice
        user2Id=4, # Diana
        createdAt=datetime.datetime(2023, 3, 25, 16, 30, 0)
    )

    friendship3 = Friendship(
        friendshipId=3,
        user1Id=5, # Eve
        user2Id=6, # Frank
        createdAt=datetime.datetime(2023, 4, 10, 12, 15, 0)
    )


    friendships.append(friendship1)
    friendships.append(friendship2)
    friendships.append(friendship3)


def create_friend_requests():
     # Clear list before creating
    friendrequests.clear()

    # Create FriendRequest objects instead of dictionaries
    # Note the change from userId/friendId to senderId/receiverId
    friendrequest1 = FriendRequest(
        requestId=1,
        senderId=1, # Alice wants to add Eve
        receiverId=5,
        status=RequestStatus.PENDING, # Explicitly set status
        createdAt=datetime.datetime(2023, 5, 5, 10, 0, 0)
    )

    friendrequest2 = FriendRequest(
        requestId=2,
        senderId=2, # Bob wants to add Diana
        receiverId=4,
        status=RequestStatus.PENDING,
        createdAt=datetime.datetime(2023, 6, 15, 11, 30, 0)
    )

    friendrequest3 = FriendRequest(
        requestId=3,
        senderId=6, # Frank wants to add Charlie
        receiverId=3,
        status=RequestStatus.PENDING,
        createdAt=datetime.datetime(2023, 7, 20, 9, 45, 0)
    )
    # Example: A request that was accepted (but maybe friendship not created yet, or just for demo)
    friendrequest4 = FriendRequest(
        requestId=4,
        senderId=7, # Grace sent to Alice
        receiverId=1,
        status=RequestStatus.ACCEPTED,
        createdAt=datetime.datetime(2023, 8, 1, 12, 0, 0)
    )
     # Example: A request that was rejected
    friendrequest5 = FriendRequest(
        requestId=5,
        senderId=3, # Charlie sent to Bob
        receiverId=2,
        status=RequestStatus.REJECTED,
        createdAt=datetime.datetime(2023, 8, 5, 15, 0, 0)
    )


    friendrequests.append(friendrequest1)
    friendrequests.append(friendrequest2)
    friendrequests.append(friendrequest3)
    friendrequests.append(friendrequest4)
    friendrequests.append(friendrequest5)
