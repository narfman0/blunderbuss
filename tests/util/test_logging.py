import unittest
from blunderbuss.util import logging


class TestLogging(unittest.TestCase):
    def test_initialize_logging(self):
        logging.initialize_logging()
