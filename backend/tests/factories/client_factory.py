"""Client factory for tests."""

import factory
from faker import Faker
from slugify import slugify

from app.models import Client

fake = Faker()


class ClientFactory(factory.Factory):
    """Factory for creating test clients."""

    class Meta:
        model = Client

    id = factory.LazyFunction(lambda: str(fake.uuid4()))
    name = factory.LazyFunction(fake.company)
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))
    industry = factory.LazyFunction(
        lambda: fake.random_element(["Technology", "Healthcare", "Finance", "Retail"])
    )
    website = factory.LazyFunction(lambda: f"https://{fake.domain_name()}")
    location = factory.LazyFunction(fake.city)
    tone = "professional"
    is_active = True
    agency_id = None
