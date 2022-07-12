import string
import datetime

from faker.factory import Factory
from faker.providers.lorem.en_US import Provider as WordProvider


class UniqueWordProvider(WordProvider):
    def word(self, ext_word_list=None):
        data = []

        for _ in range(2):
            data.append(self.words(100, ext_word_list, unique=True)[0][:6])

        ms = str(datetime.datetime.utcnow().microsecond)[-2:]
        alphabet_ms = ''.join(map(lambda x: string.ascii_letters[int(x)], list(ms)))
        data.append(alphabet_ms)
        return ''.join(data)


class FakerFactory(Factory):
    @classmethod
    def create(cls, **config):
        fake = super().create(**config)
        fake.add_provider(UniqueWordProvider)
        return fake


Faker = FakerFactory.create

fake = Faker()
