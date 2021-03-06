#----------------------------------
# lambda function:  convertRawToJPG
#  image convert(Bayer RAW Format->JPEG/TIFF) and
#  push message via SNS(Amazon Simple Notification Service)
#
# save file
#  Bucket:     <BUCKET_NAME>
#  filepath:   photo/YYYYmm/yymmdd_HHMMSS.jpg


import json
import boto3
import copy
import datetime

# PIL from Layer
from PIL import Image, ImageDraw

# SNS ARN
SNS_ARN = '__your_SNS_ARN__'  # set your SNS ARN 
                              # e.g  'arn:aws:sns:ap-northeast-1:12345678:uploadNotify'

# image size
WIDTH = 640
HEIGHT = 480

#  define color compiment rule
#  +---------+---------+---------+
#  |[SQ]     |[PN,PNLR]|[SQ]     |
#  +---------+---------+---------+
#  |[LR,PNLR]|   [IT]  |[LR,PNLR]|
#  +---------+---------+---------+
#  |[SQ]     |[PN,PNLR]|[SQ]     |
#  +---------+---------+---------+
#
#  IT ... use it color of pixcel
#  SQ ... collect color from diagonal 4 sides of pixcels
#  PN ... collect color from previous and next pixcels
#  LR ... collect color from left ans right pixcels
#  PNLR ... collect color from  PN and LR
#
IT=0
PN=1
LR=2
PNLR=3
SQ=4

COLOR_R=0
COLOR_G=1
COLOR_B=2

# notation of position is (x,y)
POS_X=0
POS_Y=1


# define color complement rule
# target Bayer Color Pattern is..
#  [G][B]
#  [R][G]
complRule=(((PN,IT,LR),(SQ,PNLR,IT)),((IT,PNLR,SQ),(LR,IT,PN)))



def lambda_handler(event, context):
    
    
    WORKDIR = '/tmp'
    S3PHOTOFOLDER = 'photo'
    s3obj = event['Records'][0]['s3']
    bucketName = s3obj['bucket']['name']
    keyOfRAW = s3obj['object']['key']
    fileName = keyOfRAW.split('/')[-1]
    (baseName, suffix) = fileName.split('.')

    srcFile = WORKDIR + '/' + fileName
    dstFile = WORKDIR + '/' + baseName + '.jpg' 

    if suffix == 'raw':
        
        print("start to convert")
        print(s3obj)

        # convert RAW -> JPG
        s3 = boto3.resource('s3')
        s3.Object(bucketName,keyOfRAW).download_file(srcFile)
    
        convert(srcFile,dstFile)  # convert RAW -> JPG
        
        tz_jst = datetime.timezone(datetime.timedelta(hours=+9))
        dt = datetime.datetime.now(tz_jst)
        folderName = 'photo' + '/' + dt.strftime('%Y%m')
        fileName = baseName + ".jpg"
        keyOfJPG = folderName + '/' + fileName
        s3.Object(bucketName,keyOfJPG).upload_file(dstFile)
        
        
        #keyOfJPG = S3PHOTOFOLDER + "/"  + baseName + '.jpg'
        #s3.Object(bucketName,keyOfJPG).upload_file(dstFile)

        # push message via SNS
        urlForRAW = getURL(bucketName,keyOfRAW)
        urlForJPG = getURL(bucketName,keyOfJPG)
        pushMessage(bucketName,keyOfRAW,keyOfJPG,urlForRAW,urlForJPG)
        print("conversion completed")
        
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('converted RAW->JPEG')
    }


# convert of picture format
#  srcFile ... source picture is Bayer Format 
#  destFile .. converted file may be jpg or tiff or any format
#               picture format is decided by file name
#               e.g.  test.jpg ... converted to JPEG format
#                     test.tiff ... converted to TIFF format
def convert(srcFile,destFile):    

    im = Image.new("RGB", (WIDTH, HEIGHT))
    dr = ImageDraw.Draw(im)

    rawAry = [0] * HEIGHT
    with open(srcFile, 'rb') as f:
      raw = f.read()

    for y in range(HEIGHT):
       rawAry[y] = [pix for pix in raw[WIDTH * y : WIDTH * (y+1)]]

    # convert Bayer to RGB
    for y in range(HEIGHT):
       for x in range(WIDTH):
             picR = getColor(rawAry,(x,y),COLOR_R)
             picG = getColor(rawAry,(x,y),COLOR_G)
             picB = getColor(rawAry,(x,y),COLOR_B)
             dr.point((x,y),fill = (picR,picG,picB))

    # save JPEG or TIFF or any
    im.save(destFile)

#
#
# Push Message via SNS(Simple Notofication Service)
#
def pushMessage(bucket,keyOfRAW,keyOfJPG,urlRAW,urlJPG):

    sns=boto3.resource('sns')
    topic=sns.Topic(SNS_ARN)
    message =  '-------------------------------------\n'
    message += ' a raw format photo data is uploaded to S3\n'
    message += ' bucket:[{:s}]\n'.format(bucket)
    message += ' filePath:[{:s}]\n'.format(keyOfRAW)
    message += ' converted to JPEG\n'
    message += ' filePath:[{:s}]\n'.format(keyOfJPG)
    message += '-------------------------------------'
    message += '\n\n'
    message += 'to check JPEG Photo...\n'
    message += urlJPG + '\n'
    message += 'to download RAW Photo Data...\n'
    message += urlRAW + '\n'
    topic.publish(Message=message)


#
#  get color value with complementing neighbor pixels
#                                     
#  raw.. raw data array (Bayer Color Filter Array)
#  pos.. position of pixcel that requred color
#        notation of pos is (x,y)
#  color.. specify the color of RGB (COLOR_R or COLOR_G or COLOR_B)
#
#  return ... color value (0x00 - 0xFF)
def getColor(raw,pos,color):

    (x,y) = pos

    sourceCellList=[]
    source1=None
    source2=None
    source3=None
    source4=None

    rule = complRule[y%2][x%2][color]
    #print("rule..{:d}".format(rule))

    if rule == IT:
        source1=(x,y)
    elif rule == PN:
        source1=(x,y-1)
        source2=(x,y+1)
    elif rule == LR:
        source1=(x-1,y)
        source2=(x+1,y)
    elif rule == PNLR:
        source1=(x,y-1)
        source2=(x,y+1)
        source3=(x-1,y)
        source4=(x+1,y)
    elif rule == SQ:
        source1=(x-1,y-1)
        source2=(x+1,y-1)
        source3=(x-1,y+1)
        source4=(x+1,y+1)

    if (source1 is not None) and isInside(source1):
        sourceCellList.append(source1)
    if (source2 is not None) and isInside(source2):
        sourceCellList.append(source2)
    if (source3 is not None) and isInside(source3):
        sourceCellList.append(source3)
    if (source4 is not None) and isInside(source4):
        sourceCellList.append(source4)

    # check cell list
    if len(sourceCellList) == 0:
        print("Error in getColor")
        print("cannot find refer pixel")
        return 0

    complColor = 0
    #import pdb
    #pdb.set_trace()
    for sourceCell in sourceCellList:
       complColor += raw[sourceCell[POS_Y]][sourceCell[POS_X]]
    complColor = int( complColor / len(sourceCellList))

    return complColor


# check inside of Picture Array (WIDTH x HEIGHT)
# pos: (x,y)
#
def isInside(pos):
  (x,y) = pos
  if x >= 0 and x < WIDTH and y >= 0 and y < HEIGHT :
     return True
  else:
     return False



#
# get an authorized URL to access converted photo in S3 
#
# to avoid following error,
#   [Invalid date (should be seconds since epoch)]
# we must use signature version s3v4
# refer to...
#    http://uchimanajet7.hatenablog.com/category/lambda
#
def getURL(bucket, key):
    
    from botocore.client import Config
    #s3 = boto3.client('s3')
    s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
    url = s3.generate_presigned_url(
        ClientMethod = 'get_object',
        Params = {'Bucket' : bucket , 'Key' : key},
        ExpiresIn = 3 * 24 * 60 * 60,
        HttpMethod = 'GET')
    return url   


