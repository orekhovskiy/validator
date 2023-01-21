from betamax import Betamax
from req import Session
from unittest import TestCase

with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/fixtures/cassettes'


class TestGitHubAPI(TestCase):
    def setUp(self):
        self.session = Session()

    # Set the cassette in line with the context declaration
    def test_repo(self):
        with Betamax(self.session).use_cassette('contract'):
            resp = self.session.get(
                'https://en.wikipedia.org/w/api.php?action=parse&page=Pet_door&format=json'
                )
            assert resp.json() is not None
