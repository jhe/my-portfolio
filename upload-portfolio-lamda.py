import zipfile
import io
import boto3
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    bb = s3.Bucket('portfolio-build.jeffrozic.com')
    pb = s3.Bucket('portfolio.jeffrozic.com')
    zf = io.BytesIO()
    
    bb.download_fileobj('portfolioBuild.zip', zf)
    
    with zipfile.ZipFile(zf) as myzip:
        for nm in myzip.namelist():
            obj = myzip.open(nm)
            pb.upload_fileobj(obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
            pb.Object(nm).Acl().put(ACL='public-read')
    
    print('Job done!')
