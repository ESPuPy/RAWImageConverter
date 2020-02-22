# RAW Image Converter 

RAW Image Conver は RAW形式の画像をJPEG形式に変換するWeb サービスです。本サービスは AWS Lambda Functions　で実装されています

RAW Image ConverterのLambda Function用ソースは以下の２種類です。

1. uploader.py<br>WebAPIを提供するとともに、アップロードされたRAW形式画像をS3に保存します
1. convertRawToJPG.py<br>RAW形式画像をS3から取得してJPEG画像に変換しS3に保存します。<br>S3に保存された画像を参照するためのURLをSNS (Amazon Simple Notofication Service)を用いてユーザにメール連絡します

All files are subject to MIT license.
