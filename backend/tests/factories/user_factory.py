"""User factory for tests."""

import factory
from faker import Faker

from app.models import User
from app.services.auth_service import AuthService

fake = Faker()


class UserFactory(factory.Factory):
    """Factory for creating test users."""

    class Meta:
        model = User

    id = factory.LazyFunction(lambda: str(fake.uuid4()))
    email = factory.LazyFunction(fake.email)
    first_name = factory.LazyFunction(fake.first_name)
    last_name = factory.LazyFunction(fake.last_name)
    hashed_password = factory.LazyAttribute(
        lambda _: AuthService.hash_password("testpassword123")
    )
    role = "agency_member"
    is_active = True
    is_verified = True
    agency_id = None
