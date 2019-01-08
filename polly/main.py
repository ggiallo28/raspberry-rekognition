import PollyApi, SqsApi
import time

def callbackSpeak(client, userdata, message):
    print("Topic="+message.topic)
    print("Message="+message.payload)
    if not message.payload:
        msg = "Nothing to say, sorry"
    else:
        msg = message.payload
    global polly
    PollyApi.speak(polly, msg)



if __name__ == '__main__':
    polly = PollyApi.connectToPolly()
    sqs = SqsApi.connectToSqs('XPeppers-Workshop-Raspberry-SQS-v0')

    while True:
        message_bodies, messages_to_delete = SqsApi.getMessages(sqs)
        for body in message_bodies:
            PollyApi.speak(polly, text=body)
        SqsApi.deleteMessages(sqs, messages_to_delete)
