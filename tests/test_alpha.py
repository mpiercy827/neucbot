import pytest
import re

from unittest import TestCase
from unittest.mock import call, patch
from neucbot.alpha import AlphaList
from neucbot.ensdf import Client, Parser

@patch.object(Parser, "parse")
@patch.object(Client, "read_or_fetch_decay_file")
@patch("os.path.exists")
class TestAlphaList(TestCase):
    def test_write_success(self, mocked_os_path_exists, mocked_read_or_fetch, mocked_parse):
        # Assume no decay or alpha files exist
        mocked_os_path_exists.return_value = False

        mocked_read_or_fetch.return_value = ""

        expected_alphas = {
                6089.88: 27.12,
                6050.78: 69.91,
                5768: 1.70,
                5626: 0.157,
                5607: 1.13,
                5481: 0.013,
                5345: 0.0010,
                5302: 0.00011,
        }

        expected_gammas = {
  	            39.857: 2.96,
  	            288.2: 0.938,
  	            328.03: 0.349,
  	            433.7: 0.047,
  	            452.98: 1.01,
  	            473.0: 0.14,
        }

        mocked_parse.return_value =  {
               "alphas": expected_alphas,
               "gammas": expected_gammas,
               "intensity": 1.0
        }

        alphas = AlphaList("Bi", 212)
        alphas.write()

        mocked_os_path_exists.assert_has_calls([call("./AlphaLists/Bi212Alphas.dat")])
        mocked_read_or_fetch.assert_called()
        mocked_parse.assert_called()

    def test_write_does_not_fetch_if_alpha_file_exists(self, mocked_os_path_exists, mocked_read_or_fetch, mocked_parse):
        # Assume no decay or alpha files exist
        mocked_os_path_exists.return_value = True

        alphas = AlphaList("Bi", 212)
        alphas.write()

        mocked_os_path_exists.assert_has_calls([call("./AlphaLists/Bi212Alphas.dat")])
        mocked_read_or_fetch.assert_not_called()
        mocked_parse.assert_not_called()
