
import boto3
import os
import pytest
import tempfile
import unittest

from requests.exceptions import HTTPError

from postag import script
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


class TestScript(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = boto3.Session().client('s3')
        cls.bucket = os.getenv('AWS_TEST_BUCKET')

    def setUp(self):
        self.tmp = tempfile.mktemp()
        self.blob = 's3://%s/test.out' % self.bucket
        with open(self.tmp, 'w') as f:
            f.writelines([
                '\s:terrestrial,c:1615816351*52\!AIVDM,1,1,,A,342O;g@P@61tAMRF00EK@8;00>@<,0*34\n',
                '\s:terrestrial,c:1615816351*52\!AIVDM,1,1,,B,144i@9P0002f57bIPLw>46vv2>@<,0*3E\n',
                '\s:terrestrial,c:1615816309*5F\!AIVDM,1,1,,B,152blF0PADIGC@t@hw=sO9;R0p:f,0*55\n',
                '\s:terrestrial,c:1615816351*52\!AIVDM,1,1,,B,13aFdSOP0OPO::6MqC@3ugvv2>`<,0*30\n',
                '\g:1-2-9,s:terrestrial,c:1615816351*19\!AIVDM,2,1,9,B,53c4vr82<ciI0D<N220DhU<48E@R222222222217=@<99toa0=nQA@TUAiiO,0*16\n',
                '\g:2-2-9*64\!AIVDM,2,2,9,B,R5C38888880,2*39\n',
                '\g:1-2-10,s:terrestrial,c:1615816351*21\!AIVDM,2,1,0,B,53c4vr82<ciI0D<N220DhU<48E@R222222222217=@<99toa0=nQA@TUAiiO,0*1F\n',
                '\g:2-2-10*5C\!AIVDM,2,2,0,B,R5C38888880,2*30\n',
                '\s:terrestrial,c:1615816351*52\!AIVDM,1,1,,B,13GQ3J?OiewluSJHkUO@HP:v0D10,0*1B\n',
                '\s:dynamic,c:1615815280*4C\!AIVDM,1,1,,A,B3:GbB006B=KfIU;cUAfcwP00000,0*2C\n',
                '\s:dynamic,c:1615815299*44\!AIVDM,1,1,,A,15D2E4?P005gV8F7OW``IVEp0000,0*35\n',
                '\s:dynamic,c:1615815447*41\!AIVDM,1,1,,A,14`Ut8gP00Ll``IjiVgu?a7p0000,0*5A\n',
                '\s:dynamic,c:1615815539*49\!AIVDM,1,1,,A,17liV?OP008<IrWv5qMtg?wp0000,0*6F\n',
                '\s:dynamic,c:1615815557*41\!AIVDM,1,1,,A,13:1wR?P301tHkNRF4wIC7Op0000,0*1B\n',
                '\s:44405,c:1615815822*0A\!AIVDM,1,1,,A,14eG;oh2@0o;eDtL@>37Sn140@Do,0*2B\n',
                '\s:44405,c:1615815717*03\!AIVDM,1,1,,B,4030p<QvDoeainQABdNN8=7005bT,0*66\n',
                '\s:44405,c:1615815943*0C\!AIVDM,1,1,,B,14eHUbsP1>o<P8PL6Vt2cww:08EW,0*54\n',
                '\s:44405,c:1615815898*0B\!AIVDM,1,1,,B,1815;0001lD=tTTM32?SB2eV05bh,0*1F\n',
                '\s:44405,c:1615815976*0A\!AIVDM,1,1,,B,B4eGR9000=fSWF7?;aoQ0c4QnDNr,0*7F\n',
                '\s:44405,c:1615815977*0B\!AIVDM,1,1,,B,14QSvp7000l96t8NvGnto`:F0<0B,0*64\n'
            ])

    def test_parse(self):
        lines = list(script.parse(self.tmp))
        self.assertGreater(len(lines), 0)

        blobUri = 's3://%s/test.sample' % self.bucket
        lines = list(script.parse(blobUri))
        self.assertGreater(len(lines), 0)

    def test_write(self):
        script.write(self.tmp, ['a', 'b', 'c'])
        self.assertTrue(os.path.exists(self.tmp))

        script.write(self.blob, ['a', 'b', 'c'])
        self.assertIsNotNone(self.client.get_object(Bucket=self.bucket, Key='test.out'))

    def tearDown(self):
        os.remove(self.tmp)
        self.client.delete_object(Bucket=self.bucket, Key='test.out')
