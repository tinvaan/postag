
import boto3
import os

from . import script


s3 = boto3.resource('s3')


def run(event, context):
    written = []
    src = s3.Bucket(os.getenv('AWS_SOURCE_BUCKET'))
    dst = s3.Bucket(os.getenv('AWS_DESTINATION_BUCKET'))

    for obj in src.objects.all():
        srcUri = f's3://{src.name}/{obj.key}'
        dstUri = f's3://{dst.name}/{obj.key}'

        script.write(dstUri, list(script.parse(srcUri)))
        written.append(dstUri)

    return {'status': 'updated', 'modified': written}
