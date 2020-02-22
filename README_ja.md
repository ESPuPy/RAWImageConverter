# RAW Image Converter 

RAW Image Conver は RAW形式の画像をJPEG形式に変換するWeb サービスです。本サービスは AWS Lambda Functions　で実装されています

RAW Image ConverterのLambda Function用ソースは以下の２種類です。

1. uploader.py<br>WebAPIを提供するとともに、アップロードされたRAW形式画像をS3に保存します
1. convertRawToJPG.py<br>RAW形式画像をS3から取得してJPEG画像に変換しS3に保存します。<br>S3に保存された画像を参照するためのURLをSNS (Amazon Simple Notofication Service)を用いてユーザにメール連絡します

AWS Lambdaの設定手順が複雑なため、設定手順を以下にまとめています。分かりにくいレベルですがご参照ください。
1. docs/AWS_Lambda_SetupGuide_ja.pdf
1. docs/setup_Lambda_uploader_ja.pdf
1. docs/setup_Lambda_convertRAWtoJPG_ja.pdf

converRawToJPG.pyを実行する上で画像変換ライブラリ(PIL)が必要です。AWS Lambda環境で使えるPILパッケージを作りました。以下から取得してください。
PILPackage/

すべてのファイル、ソースはMITライセンスに従っています。
All files are subject to MIT license.
