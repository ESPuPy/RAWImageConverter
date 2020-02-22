# RAW Image Converter 

This system offers Image Convert API Service. That executes on AWS Lambda Functions.

This service consists following 2 Lambda Functions.

1. uploader.py<br>provide API and receive RAW Image data and save to S3
1. convertRawToJPG.py<br>get RAW Image datafrom S3 and convert to JPEG format and save to S3. And notify to user via SNS (Amazon Simple Notofication Service).

All files are subject to MIT license.



