
import boto3
import os

from datetime import datetime

from postag import script


s3 = boto3.resource('s3')


def run(event, context):
    written = []
    src = s3.Bucket(os.getenv('AWS_SOURCE_BUCKET'))
    dst = s3.Bucket(os.getenv('AWS_DESTINATION_BUCKET'))

    for obj in src.objects.all():
        obj = obj.Object()
        if not obj.metadata.get('processed'):
            lines = script.parse(f's3://{src.name}/{obj.key}')
            script.write(f's3://{dst.name}/{obj.key}', lines)
            written.append(f's3://{dst.name}/{obj.key}')
        obj.put(Metadata={'processed': datetime.now().isoformat()})

    return {'status': 'updated', 'modified': written}
