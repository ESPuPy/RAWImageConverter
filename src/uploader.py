#----------------------------------
# function: uploader
#   receive the RAW image data and save to S3
#
#----------------------------------
import json
import boto3
import base64
import datetime

ENABLE_AUTH = True
BUCKET_NAME = '__buketName__'   # set your S3 Bucket Name  e.g wificambucket
API_KEY = 'setYourAPIKey'       # set your API key

def lambda_handler(event, context):

    #for Debug
    #print(event)
    #print(event['body'])

    #check API KEY
    if ENABLE_AUTH:
        if (not 'API-Key' in event['headers'])\
           or (event['headers']['API-Key'] != API_KEY):
            return {
                'statusCode': 401,
                'body': json.dumps('Unauthorized')
            }
    
    #check media type    
    if (not 'Content-type' in event['headers'])\
       or (event['headers']['Content-type'] != 'application/octet-stream')\
       or (not 'isBase64Encoded' in event)\
       or (event['isBase64Encoded'] != True):
        return {
            'statusCode': 415,
            'body': json.dumps('unsupported media type')
        }
    
    
    imgData = base64.b64decode(event['body'])

    # for Debug, write to logfile data type and length
    print(type(imgData))
    print(len(imgData))
    
    bucketName = BUCKET_NAME
    tz_jst = datetime.timezone(datetime.timedelta(hours=+9))
    dt = datetime.datetime.now(tz_jst)
    folderName = 'rawdata' + '/' + dt.strftime('%Y%m')
    fileName = dt.strftime('%y%m%d_%H%M%S') + ".raw"
    key = folderName + '/' + fileName
    s3 = boto3.resource('s3')   
    obj = s3.Object(bucketName,key)
    obj.put(Body = imgData)
    
    return {
        'statusCode': 200,
        'body': json.dumps('upload complete')
    }
