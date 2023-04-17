
import boto3
import os
import pytest
import unittest

from moto import mock_s3
from requests.exceptions import HTTPError

from . import AWSEnv, stream



class TestTLE(unittest.TestCase):
    expected = {
        25544: '0 ISS (ZARYA)\n1 25544U 98067A   23106.50844690  .00020215  00000-0  36275-3 0  9994\n2 25544  51.6392 274.1971 0005904 200.0032 260.3896 15.49871570392223\n',
        40044: '0 LEMUR 1\n1 40044U 14033AL  23105.44138345  .00003516  00000-0  50441-3 0  9998\n2 40044  97.6656 282.9618 0055880 259.9835  99.5067 14.76048999474004\n'
    }

    @pytest.mark.vcr()
    def test_get(self):
        # Pesky import
        # https://docs.getmoto.org/en/latest/docs/getting_started.html#what-about-those-pesky-imports
        from postag.script import TLE

        self.assertEqual(TLE.get(25544), self.expected.get(25544))
        self.assertEqual(TLE.get(40044), self.expected.get(40044))
        with self.assertRaises(HTTPError):
            TLE.get(1099)
            TLE.get(20010)


@mock_s3
class TestScript(AWSEnv):
    def setUp(self):
        with open(self.tmp, 'w') as f:
            f.writelines(stream)

        self.s3 = boto3.Session().client('s3')
        self.s3.create_bucket(Bucket=self.bucket)
        self.s3.upload_file(self.tmp, self.bucket, self.key)

    def test_parse(self):
        # Pesky import
        # https://docs.getmoto.org/en/latest/docs/getting_started.html#what-about-those-pesky-imports
        from postag import script

        lines = list(script.parse(self.tmp))
        self.assertGreater(len(lines), 0)

        lines = list(script.parse(self.blob))
        self.assertGreater(len(lines), 0)

    def test_write(self):
        # Pesky import
        # https://docs.getmoto.org/en/latest/docs/getting_started.html#what-about-those-pesky-imports
        from postag import script

        script.write(self.tmp, ['a', 'b', 'c'])
        self.assertTrue(os.path.exists(self.tmp))

        script.write(self.blob, ['a', 'b', 'c'])
        self.assertIsNotNone(self.s3.get_object(Bucket=self.bucket, Key=self.key))

    def tearDown(self):
        os.remove(self.tmp)
        self.s3.delete_object(Bucket=self.bucket, Key=self.key)
        self.s3.delete_bucket(Bucket=self.bucket)
