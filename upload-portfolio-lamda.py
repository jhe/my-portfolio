import zipfile
import io
import boto3
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-west-1:899238936541:deployPortfolioTopic')
    location = {
        'bucketName': 'portfolio.jeffrozic.com', 
        'objectKey': 'portfolioBuild.zip'
    }
    try:
        job = event.get("CodePipeline.job")
        if job:
            for artifact in job['data']['inputArtifacts']:
                if artifact['name'] == 'MyAppBuild':
                    location = artifact['location']['s3Location']
        print('Building portfolio from location = ' + str(location))
        s3 = boto3.resource('s3')
        bb = s3.Bucket('portfolio-build.jeffrozic.com')
        pb = s3.Bucket(location['bucketName'])
        zf = io.BytesIO()
        bb.download_fileobj(location['objectKey'], zf)
        with zipfile.ZipFile(zf) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                pb.upload_fileobj(obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                pb.Object(nm).Acl().put(ACL='public-read')
        
        topic.publish(Subject='Portfolio Deployed', Message='My Portfolio was successfully deployed')
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId = job['id'])
    except:
        topic.publish(Subject='Portfolio deploy failed', Message='My Portfolio was not deployed')        
        raise
    
    print('Job done!')
