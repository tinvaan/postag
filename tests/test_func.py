
import boto3
import os

from moto import mock_s3

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

    def test_lambda_handler(self):
        # Pesky import
        # https://docs.getmoto.org/en/latest/docs/getting_started.html#what-about-those-pesky-imports
        from postag import func

        response = func.run(dict(), dict())
        self.assertEqual(response.get('status'), 'updated')
        self.assertGreater(len(response.get('modified')), 0)

    def tearDown(self):
        os.remove(self.tmp)
        self.s3.delete_object(Bucket=os.getenv('AWS_SOURCE_BUCKET'), Key=self.key)
        self.s3.delete_bucket(Bucket=os.getenv('AWS_SOURCE_BUCKET'))

        self.s3.delete_object(Bucket=os.getenv('AWS_DESTINATION_BUCKET'), Key=self.key)
        self.s3.delete_bucket(Bucket=os.getenv('AWS_DESTINATION_BUCKET'))
