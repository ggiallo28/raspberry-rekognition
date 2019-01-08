import boto3
import json

defaultRegion = 'eu-west-1'
queueName = 'example-queue-12345'
max_queue_messages = 1

def connectToSqs(queueName=queueName, regionName=defaultRegion):
    sqs = boto3.resource('sqs', region_name=defaultRegion)
    return sqs.get_queue_by_name(QueueName=queueName)

def getMessages(queue, max_queue_messages=max_queue_messages):
    messages_to_delete = []
    message_bodies = []
    for message in queue.receive_messages(MaxNumberOfMessages=max_queue_messages):
        # process message body
        try:
            body = json.loads(message.body)
        except ValueError:
            body = message.body
        message_bodies.append(body)
        # add message to delete
        messages_to_delete.append({
            'Id': message.message_id,
            'ReceiptHandle': message.receipt_handle
        })
    return message_bodies, messages_to_delete

def deleteMessages(queue, messages_to_delete):
    # if you don't receive any notifications the
    # messages_to_delete list will be empty
    if len(messages_to_delete) == 0:
        return
    # delete messages to remove them from SQS queue
    # handle any errors
    else:
        delete_response = queue.delete_messages(Entries=messages_to_delete)
