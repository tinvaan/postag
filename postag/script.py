
import boto3
import contextlib
import predict
import requests

from geopy.distance import distance
from smart_open import open

from postag.libs.simpleais import sentences_from_source


session = boto3.Session()


class TLE:
    session = requests.Session()
    host = 'http://tle.spire.com/'
    qth = (37.771034, 122.413815, 7)

    @classmethod
    def get(cls, norad_id):
        r = cls.session.get(cls.host + str(norad_id))
        if not r.ok:  # Explicit status check, added for readability
            r.raise_for_status()
        return r.text


def parse(uri):
    for sentence in sentences_from_source(uri):
        if sentence.source and sentence.source not in ['terrestrial', 'dynamic']:
            with contextlib.suppress(ValueError):  # skip malformed source strings
                lon, lat = sentence.location()  # vessel coordinates
                tle = TLE.get(int(sentence.source))
                sat = predict.observe(tle, TLE.qth, sentence.time)

                p, q = sat.get('longitude', ''), sat.get('latitude', '')  # SSP coordinates
                r = 'OK' if distance((p, q), (lat, lon)) <= sat.get('footprint', 3000) else 'SPOOF'
                yield f"\p:{p},\q:{q},\r:{r},{sentence.string}"  # noqa


def write(uri, sentences):
    with open(uri, 'w', transport_params={'client': session.client('s3')}) as fout:
        return fout.writelines(sentences)
