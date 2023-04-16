
import pytest
import unittest

from requests.exceptions import HTTPError

from postag.script import TLE


class TestTLE(unittest.TestCase):
    expected = {
        25544: '0 ISS (ZARYA)\n1 25544U 98067A   23106.50844690  .00020215  00000-0  36275-3 0  9994\n2 25544  51.6392 274.1971 0005904 200.0032 260.3896 15.49871570392223\n',
        40044: '0 LEMUR 1\n1 40044U 14033AL  23105.44138345  .00003516  00000-0  50441-3 0  9998\n2 40044  97.6656 282.9618 0055880 259.9835  99.5067 14.76048999474004\n'
    }

    @pytest.mark.vcr()
    def test_get(self):
        self.assertEqual(TLE.get(25544), self.expected.get(25544))
        self.assertEqual(TLE.get(40044), self.expected.get(40044))
        with self.assertRaises(HTTPError):
            TLE.get(1099)
            TLE.get(20010)
