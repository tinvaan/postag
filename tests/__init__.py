
import os
import tempfile
import unittest

from moto import mock_s3


stream = [
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
]


class AWSEnv(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key = 'test.sample'
        cls.tmp = tempfile.mktemp()
        cls.bucket = os.getenv('AWS_TEST_BUCKET')
        cls.blob = f's3://{cls.bucket}/{cls.key}'
