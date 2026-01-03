"""Agency factory for tests."""

import factory
from faker import Faker
from slugify import slugify

from app.models import Agency

fake = Faker()


class AgencyFactory(factory.Factory):
    """Factory for creating test agencies."""

    class Meta:
        model = Agency

    id = factory.LazyFunction(lambda: str(fake.uuid4()))
    name = factory.LazyFunction(fake.company)
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))
    subdomain = factory.LazyAttribute(lambda obj: slugify(obj.name)[:20])
    website = factory.LazyFunction(lambda: f"https://{fake.domain_name()}")
    primary_color = "#1a4a6e"
    secondary_color = "#b8860b"
    is_active = True
    plan_id = None
