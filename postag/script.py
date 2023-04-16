
import boto3
import contextlib
import predict
import requests

from smart_open import open

from libs.simpleais import sentences_from_source


session = boto3.Session()


class TLE:
    session = requests.Session()
    host = 'http://tle.spire.com/'
    qth = (37.771034, 122.413815, 7)

    @classmethod
    def get(cls, norad_id):
        r = cls.session.get(cls.host + str(norad_id))
        if not r.ok:
            r.raise_for_status()
        return r.text


def parse(uri):
    for sentence in sentences_from_source(uri):
        if sentence.source and sentence.source not in ['terrestrial', 'dynamic']:
            with contextlib.suppress(ValueError): # skip malformed source strings
                tle = TLE.get(int(sentence.source))
                sat = predict.observe(tle, TLE.qth, sentence.time)
                yield f'\p:{sat.get("latitude", "")},\q:{sat.get("longitude", "")},{sentence.string}'


def write(uri, sentences):
    with open(uri, 'wb', transport_params={'client': session.client('s3')}) as fout:
        return fout.writelines(sentences)
