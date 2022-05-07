import json
import boto3
import datetime
import botocore
from botocore.exceptions import ClientError
import os
from pprint import pprint


client_ec2 = boto3.client('ec2')
client_sns = boto3.client('sns')
sns_arn = os.environ['sns_arn']
account_alias = os.environ['account_alias']

def create_tag(resource, key, value):
    try:
        response = client_ec2.create_tags(
            Resources=[resource],
            Tags=[
                {
                    'Key': key,
                    'Value': value
                }]
        )   
    except botocore.exceptions.ClientError as e:
        print(e)
    else:
        return response

def publish_message(topic_arn, message, subject):
    try:
        response = client_sns.publish(
            TopicArn = topic_arn,
            Message = message,
            Subject = subject,
        )['MessageId']

    except botocore.exceptions.ClientError as e:
        print(e)
    else:
        return response

def lambda_handler(event, context):
    print(event)
    instance_id = event['detail']['requestParameters']['instanceId']
    volume_id = event['detail']['requestParameters']['volumeId']
    print(instance_id)
    print(volume_id)

    liste_tags = {'Name':'vol-ebs-data', 'departement':'operations', 'domaine':'data', 'lambda':'check_ebs'}
    email_body = "#### Ajout tags à un volume ebs data sur {} #### \n".format(account_alias)
    topic_arn = sns_arn
    subject = 'Création tag sur volume ebs data'


    instance_details = client_ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
    tags = instance_details['Tags']
    print(tags)
    for tag in tags:
        if tag['Key']=="domaine":
            tag_hit = tag['Value']

    print(tag_hit)
    if tag_hit == 'data':
        print("EBS éligible pour le tagging")
        for key, value in liste_tags.items():
            create_tag(volume_id, key, value)
            email_body = email_body + "\n  Ajout tag key : {} value : {} au volume Id : {}".format(key,value,volume_id)
            #create_tag(volume_id, 'Name', 'vol-ebs-data')
            #create_tag(volume_id, 'departement', 'operations')
        message = email_body
        message_id = publish_message(topic_arn, message, subject)
        print("Message envoyé au topic - {} avec pour message Id - {}".format(topic_arn,message_id))

    else:
        print("EBS non eligible")