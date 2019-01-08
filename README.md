## Raspberry Rekognition

## Prerequisiti:
* account aws
* python pip
* ansible
* boto


Questo lavoro si ispira al blog post https://amzn.to/2RiUmwo .

## Esecuzione

1. Installare: https://github.com/awslabs/amazon-kinesis-video-streams-producer-sdk-cpp

2. Creare le Access Key per la tua utenza e settarle usando __aws_configure --profile <profile_name>__

2. Create un bucket S3.

3. Esecuzione dei comandi:
    * aws cloudformation package --template-file raspberry-workshop.yml --output-template-file raspberry-workshop.out.yml --s3-bucket <bucket_name> --region <region> --profile <profile_name>*
    * aws cloudformation deploy --template-file <path_to_raspberry-workshop.out.yml> --stack-name rekognition-workshop --capabilities CAPABILITY_NAMED_IAM --profile <profile_name>*

4. Andare su Cloud Formation e copiare Kinesis Data Stream ARN.

5. Creare un Kinesis Video Stream, e copiate ARN.

6. Creare una Collection in Rekognition:
    * aws rekognition create-collection --collection-id <collection_id> --profile <profile_name>*

7. Modificare streaming/main.yaml e settare le variabili
    * __video_stream_arn__: # vedi step precedenti
    * __data_stream_arn__:  # vedi step precedenti
    * __collection_id__:    # nome della collection in rekognition
    * __profile__:          # nome del profilo aws <profile_name>

8. Modificare IP in streaming/inventory e settarlo pari all'ip della vostra raspberry

9. Lanciare Playbook Ansible
    * ansible-playbook streaming/main.yaml --ask-pass *

10. Lanciare
        python ./polly/main.py

