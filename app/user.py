import datetime
from enum import Enum
from typing import Optional # For optional type hints

# For password hashing (install with: pip install Werkzeug)
# Alternatively, you can use bcrypt, passlib, or hashlib (with salt)
from werkzeug.security import generate_password_hash, check_password_hash

class Role(Enum):
    """
    Defines the possible roles a user can have.
    """
    USER = "user"
    ADMIN = "admin"

    # Optional: to allow creating Role from string easily
    @classmethod
    def from_string(cls, s: str) -> 'Role':
        try:
            return cls[s.upper()]
        except KeyError:
            raise ValueError(f"'{s}' is not a valid role. Must be one of {', '.join([r.name for r in cls])}")

class User:
    """
    Represents a user in the system.
    """

    def __init__(self,
                 userId: int,
                 name: str,
                 email: str,
                 username: str,
                 password: str, # Plain text password, will be hashed
                 status: str = "active", # Default status
                 role: Role = Role.USER, # Default role
                 createdAt: Optional[datetime.datetime] = None):
        """
        Initializes a new User object.

        Args:
            userId (int): Unique identifier for the user.
            name (str): Full name of the user.
            email (str): Email address of the user.
            username (str): Unique username for login.
            password (str): Plain text password (will be hashed and stored).
            status (str, optional): Current status of the user (e.g., "active", "inactive", "pending").
                                    Defaults to "active".
            role (Role, optional): The role of the user (Role.USER or Role.ADMIN).
                                   Defaults to Role.USER.
            createdAt (datetime.datetime, optional): The date and time the user was created.
                                                     Defaults to the current datetime if None.
        """
        if not isinstance(userId, int) or userId <= 0:
            raise ValueError("userId must be a positive integer.")
        if not name or not isinstance(name, str):
            raise ValueError("Name cannot be empty and must be a string.")
        if not email or "@" not in email: # Basic email validation
            raise ValueError("A valid email is required.")
        if not username or not isinstance(username, str):
            raise ValueError("Username cannot be empty and must be a string.")
        if not password or len(password) < 6: # Basic password length check
            raise ValueError("Password must be at least 6 characters long.")

        self.userId: int = userId
        self.name: str = name
        self.email: str = email
        self.username: str = username
        self._password_hash: str = self._set_password(password) # Store hashed password
        self.status: str = status

        if isinstance(role, str):
            self.role: Role = Role.from_string(role)
        elif isinstance(role, Role):
            self.role: Role = role
        else:
            raise TypeError("Role must be a Role enum instance or a valid role string.")

        self.createdAt: datetime.datetime = createdAt if createdAt else datetime.datetime.now()

    def _set_password(self, plain_password: str) -> str:
        """Hashes the plain text password."""
        return generate_password_hash(plain_password)

    def check_password(self, plain_password: str) -> bool:
        """
        Checks if the provided plain text password matches the stored hash.

        Args:
            plain_password (str): The password to check.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return check_password_hash(self._password_hash, plain_password)

    @property
    def password(self):
        """Prevents direct reading of the password hash."""
        raise AttributeError("password is not a readable attribute. Use check_password() instead.")

    @password.setter
    def password(self, plain_password: str):
        """Allows setting/updating the password, which will re-hash it."""
        if not plain_password or len(plain_password) < 6:
             raise ValueError("Password must be at least 6 characters long.")
        self._password_hash = self._set_password(plain_password)

    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"User(id={self.userId}, username='{self.username}', email='{self.email}', role='{self.role.value}')"

    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return (f"User(userId={self.userId!r}, name={self.name!r}, email={self.email!r}, "
                f"username={self.username!r}, status={self.status!r}, "
                f"role=Role.{self.role.name}, createdAt={self.createdAt!r})")

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the user (excluding password hash)."""
        return {
            "userId": self.userId,
            "name": self.name,
            "email": self.email,
            "username": self.username,
            "status": self.status,
            "role": self.role.value, # Store the string value of the enum
            "createdAt": self.createdAt.isoformat() # ISO format for easy serialization
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Creates a User instance from a dictionary (e.g., from a database or API)."""
        # Note: This assumes 'password' is not in the dict, or if it is, it's plain text
        # for a new user creation. If loading an existing user, you'd typically load the hash
        # directly into _password_hash and skip the hashing step.
        # For simplicity, this example assumes 'password' is for a new user or password update.

        if 'password' not in data and '_password_hash' not in data:
            raise ValueError("Password information missing from data dictionary.")

        # If loading from a DB where hash is already stored
        if '_password_hash' in data:
            user = cls(
                userId=data['userId'],
                name=data['name'],
                email=data['email'],
                username=data['username'],
                password="dummy_password_to_pass_init_check", # Will be overwritten
                status=data.get('status', 'active'),
                role=Role.from_string(data.get('role', 'user')),
                createdAt=datetime.datetime.fromisoformat(data['createdAt']) if 'createdAt' in data else None
            )
            user._password_hash = data['_password_hash'] # Directly set the stored hash
            return user
        else: # If creating with a plain password
            return cls(
                userId=data['userId'],
                name=data['name'],
                email=data['email'],
                username=data['username'],
                password=data['password'], # This will be hashed by __init__
                status=data.get('status', 'active'),
                role=Role.from_string(data.get('role', 'user')),
                createdAt=datetime.datetime.fromisoformat(data['createdAt']) if 'createdAt' in data else None
            )
