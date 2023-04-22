
import boto3
import os
import tempfile

from moto import mock_s3
from datetime import datetime

from . import AWSEnv, stream


@mock_s3
class TestLambdaHandler(AWSEnv):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        os.environ.update({'AWS_SOURCE_BUCKET': 'foo', 'AWS_DESTINATION_BUCKET': 'bar'})

    def setUp(self):
        with open(self.tmp, 'w') as f:
            f.writelines(stream)

        self.s3 = boto3.Session().client('s3')
        self.s3.create_bucket(Bucket=os.getenv('AWS_SOURCE_BUCKET'))
        self.s3.upload_file(self.tmp, os.getenv('AWS_SOURCE_BUCKET'), self.key)

        self.s3.create_bucket(Bucket=os.getenv('AWS_DESTINATION_BUCKET'))

    def populate(self, bucket):
        meta = {'processed': datetime.now().isoformat()}
        for idx in range(20):
            key = str(idx) + '.txt'
            tmp = tempfile.mktemp(key)
            with open(tmp, 'w') as f:
                f.writelines(stream)

            self.s3.upload_file(tmp, bucket, key)
            if idx >= 5:
                self.s3.put_object(Bucket=bucket, Key=key, Metadata=meta)

    def test_lambda_handler(self):
        # Pesky import
        # https://docs.getmoto.org/en/latest/docs/getting_started.html#what-about-those-pesky-imports
        from postag import func

        response = func.run(dict(), dict())
        self.assertEqual(response.get('status'), 'updated')
        self.assertGreater(len(response.get('modified')), 0)

    def test_unprocessed_writes(self):
        # Pesky import
        # https://docs.getmoto.org/en/latest/docs/getting_started.html#what-about-those-pesky-imports
        from postag import func

        self.populate(os.getenv('AWS_SOURCE_BUCKET'))
        response = func.run(dict(), dict())
        self.assertEqual(response.get('status'), 'updated')
        self.assertEqual(len(response.get('modified')), 5 + 1)

    def tearDown(self):
        os.remove(self.tmp)
        keys = [self.key] + [str(idx) + '.txt' for idx in range(20)]
        for key in keys:
            self.s3.delete_object(Bucket=os.getenv('AWS_SOURCE_BUCKET'), Key=key)
            self.s3.delete_object(Bucket=os.getenv('AWS_DESTINATION_BUCKET'), Key=key)

        self.s3.delete_bucket(Bucket=os.getenv('AWS_SOURCE_BUCKET'))
        self.s3.delete_bucket(Bucket=os.getenv('AWS_DESTINATION_BUCKET'))
