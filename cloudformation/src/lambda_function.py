import json, os, base64, logging
from datetime import datetime
import boto3, time

SHUTUPDELAY = os.environ['SHUTUPDELAY']
SQSQUEUE = os.environ['SQSQUEUE']
PARAMETER = os.environ['PARAMETER']

sqs_client = boto3.client('sqs')
ssm_client = boto3.client('ssm')
current_milli_time = lambda: int(round(time.time() * 1000))

def lambda_handler(event, context):
    try:
        response = ssm_client.get_parameter(Name=PARAMETER, WithDecryption=False)
        parameter = json.loads(response['Parameter']['Value'])
        #{
        #    "ExternalImageId_1" : Timestamp_1,
        #    "ExternalImageId_1" : Timestamp_1
        #}
        for record in event['Records']:
            data = json.loads(base64.b64decode(record['kinesis']['data']).decode('utf-8'))
            logging.warning(data['FaceSearchResponse'])
            ts = int(float(record['kinesis']['approximateArrivalTimestamp']))
            for face_search in data['FaceSearchResponse']:
                for matched_faces in face_search['MatchedFaces']:
                    matched_face = matched_faces['Face']['ExternalImageId']

                    if matched_face not in parameter or current_milli_time() > (parameter[matched_face] + int(SHUTUPDELAY)):
                        response = sqs_client.send_message(
                            QueueUrl=SQSQUEUE,
                            MessageBody='Vedo {}.'.format(matched_face) if matched_face else 'Vedo un viso ma non so chi è.'
                        )
                        logging.warning(response)
                        parameter[matched_face] = current_milli_time()
                        response = ssm_client.put_parameter(Name=PARAMETER,Value=json.dumps(parameter),Type='String',Overwrite=True)

                        return response['ResponseMetadata']['HTTPStatusCode']
    except Exception as error:
        logging.exception(error)

if __name__ == '__main__':
    b64event = "ewogICJSZWNvcmRzIjogWwogICAgewogICAgICAia2luZXNpcyI6IHsKICAgICAgICAia2luZXNpc1NjaGVtYVZlcnNpb24iOiAiMS4wIiwKICAgICAgICAicGFydGl0aW9uS2V5IjogIjI1MWFiNGM2LTU4OGEtNDZjOC04MDc4LTA4ZGVlMDM2ZGNiYyIsCiAgICAgICAgInNlcXVlbmNlTnVtYmVyIjogIjQ5NTkxNzk2Mzg4OTg5NTAzNjM0NDUzNzM3NDk2MzE5OTEyODExMzQ2NDg1NDY2NzQ1NTM2NTE0IiwKICAgICAgICAiZGF0YSI6ICJleUpKYm5CMWRFbHVabTl5YldGMGFXOXVJanA3SWt0cGJtVnphWE5XYVdSbGJ5STZleUpUZEhKbFlXMUJjbTRpT2lKaGNtNDZZWGR6T210cGJtVnphWE4yYVdSbGJ6cGxkUzEzWlhOMExURTZPRE14TmpVd09ERTROVEV6T25OMGNtVmhiUzkzYjNKcmMyaHZjQzh4TlRRMU16azRNekExTVRFMklpd2lSbkpoWjIxbGJuUk9kVzFpWlhJaU9pSTVNVE0wTXpnMU1qTXpNekU0TWpBMk1USTJOakl5TWpBeE9UVTVNRE15TkRnd01UWXlOVGswTURjeE5UazJPU0lzSWxObGNuWmxjbFJwYldWemRHRnRjQ0k2TVM0MU5EWTROelEwTXpBeE9EbEZPU3dpVUhKdlpIVmpaWEpVYVcxbGMzUmhiWEFpT2pFdU5UUTJPRGMwTkRJNU56WTFSVGtzSWtaeVlXMWxUMlptYzJWMFNXNVRaV052Ym1Seklqb3dMakI5ZlN3aVUzUnlaV0Z0VUhKdlkyVnpjMjl5U1c1bWIzSnRZWFJwYjI0aU9uc2lVM1JoZEhWeklqb2lVbFZPVGtsT1J5SjlMQ0pHWVdObFUyVmhjbU5vVW1WemNHOXVjMlVpT2x0N0lrUmxkR1ZqZEdWa1JtRmpaU0k2ZXlKQ2IzVnVaR2x1WjBKdmVDSTZleUpJWldsbmFIUWlPakF1TURjeE56YzVNalVzSWxkcFpIUm9Jam93TGpBME5UWTNPVGsxTENKTVpXWjBJam93TGpRME9UUTRORFFzSWxSdmNDSTZNQzR5TlRRM01qazVObjBzSWtOdmJtWnBaR1Z1WTJVaU9qazVMams1T1RJNExDSk1ZVzVrYldGeWEzTWlPbHQ3SWxnaU9qQXVORFk1TWpZNE5EUXNJbGtpT2pBdU1qZzJNekl4TXpjc0lsUjVjR1VpT2lKbGVXVk1aV1owSW4wc2V5SllJam93TGpRNE56RTVNREV6TENKWklqb3dMakk1TURNMU1qTXNJbFI1Y0dVaU9pSmxlV1ZTYVdkb2RDSjlMSHNpV0NJNk1DNDBOalV5TWprek5pd2lXU0k2TUM0ek1UQXpPRFkxTkN3aVZIbHdaU0k2SW0xdmRYUm9UR1ZtZENKOUxIc2lXQ0k2TUM0ME9EQXlOVEV5TlN3aVdTSTZNQzR6TVRNME5qYzNMQ0pVZVhCbElqb2liVzkxZEdoU2FXZG9kQ0o5TEhzaVdDSTZNQzQwTnpnNU5EVTVMQ0paSWpvd0xqTXdOamc1TVRnekxDSlVlWEJsSWpvaWJtOXpaU0o5WFN3aVVHOXpaU0k2ZXlKUWFYUmphQ0k2TFRNMExqa3pNVFk0TXl3aVVtOXNiQ0k2TlM0NE5EWTBNREUzTENKWllYY2lPakl5TGpRek5URTNNWDBzSWxGMVlXeHBkSGtpT25zaVFuSnBaMmgwYm1WemN5STZPRE11T1RJeE5qZzBMQ0pUYUdGeWNHNWxjM01pT2pVekxqTXpNREEwT0gxOUxDSk5ZWFJqYUdWa1JtRmpaWE1pT2x0ZGZTeDdJa1JsZEdWamRHVmtSbUZqWlNJNmV5SkNiM1Z1WkdsdVowSnZlQ0k2ZXlKSVpXbG5hSFFpT2pBdU1EY3hNVGMyTVRVc0lsZHBaSFJvSWpvd0xqQTBNRGcyTmpNM05Td2lUR1ZtZENJNk1DNDJOakF5TmpNNE5Dd2lWRzl3SWpvd0xqSTNORGMyTnpjemZTd2lRMjl1Wm1sa1pXNWpaU0k2T1RrdU9UazVNelEwTENKTVlXNWtiV0Z5YTNNaU9sdDdJbGdpT2pBdU5qZ3pNVGM0TlRRc0lsa2lPakF1TXpBMU16YzVOemdzSWxSNWNHVWlPaUpsZVdWTVpXWjBJbjBzZXlKWUlqb3dMalk1T0RVMk16WTBMQ0paSWpvd0xqTXdOekV5T0RZM0xDSlVlWEJsSWpvaVpYbGxVbWxuYUhRaWZTeDdJbGdpT2pBdU5qZ3dPRFE0TlN3aVdTSTZNQzR6TXpJMU1qTTJOQ3dpVkhsd1pTSTZJbTF2ZFhSb1RHVm1kQ0o5TEhzaVdDSTZNQzQyT1RNME16VTFOU3dpV1NJNk1DNHpNek0yTlRNNUxDSlVlWEJsSWpvaWJXOTFkR2hTYVdkb2RDSjlMSHNpV0NJNk1DNDJPVFEyTkRZeExDSlpJam93TGpNeU16UXlNemMwTENKVWVYQmxJam9pYm05elpTSjlYU3dpVUc5elpTSTZleUpRYVhSamFDSTZMVEkwTGpJMU16Z3dNeXdpVW05c2JDSTZNQzR6TkRjM01qQTBMQ0paWVhjaU9qTTBMak15TURRMk5YMHNJbEYxWVd4cGRIa2lPbnNpUW5KcFoyaDBibVZ6Y3lJNk5qTXVOekl5T0RJMExDSlRhR0Z5Y0c1bGMzTWlPak00TGpnNU5qQXhmWDBzSWsxaGRHTm9aV1JHWVdObGN5STZXM3NpVTJsdGFXeGhjbWwwZVNJNk9Ua3VOekUwTlRVMExDSkdZV05sSWpwN0lrSnZkVzVrYVc1blFtOTRJanA3SWtobGFXZG9kQ0k2TUM0ME16TXhNalVzSWxkcFpIUm9Jam93TGpJeE5EQTNOQ3dpVEdWbWRDSTZNQzR6TnpZME9EUXNJbFJ2Y0NJNk1DNHpORFF3T1RkOUxDSkdZV05sU1dRaU9pSXdOelF4WW1ZeE5TMHpaVEU1TFRSaE5UY3RZalUzTmkxak9EUXlOalkxTldWalpUWWlMQ0pEYjI1bWFXUmxibU5sSWpveE1EQXVNQ3dpU1cxaFoyVkpaQ0k2SW1Kak1tWTBNalkxTFRNME1tUXRNMkppWlMwNU9UTTFMVFJtTXpjMllUYzBZVGN5TlNJc0lrVjRkR1Z5Ym1Gc1NXMWhaMlZKWkNJNklteHZjbVZ1ZW04aWZYMWRmVjE5IiwKICAgICAgICAiYXBwcm94aW1hdGVBcnJpdmFsVGltZXN0YW1wIjogMTU0Njg3NDQzMy43NjMKICAgICAgfSwKICAgICAgImV2ZW50U291cmNlIjogImF3czpraW5lc2lzIiwKICAgICAgImV2ZW50VmVyc2lvbiI6ICIxLjAiLAogICAgICAiZXZlbnRJRCI6ICJzaGFyZElkLTAwMDAwMDAwMDAwMDo0OTU5MTc5NjM4ODk4OTUwMzYzNDQ1MzczNzQ5NjMxOTkxMjgxMTM0NjQ4NTQ2Njc0NTUzNjUxNCIsCiAgICAgICJldmVudE5hbWUiOiAiYXdzOmtpbmVzaXM6cmVjb3JkIiwKICAgICAgImludm9rZUlkZW50aXR5QXJuIjogImFybjphd3M6aWFtOjo4MzE2NTA4MTg1MTM6cm9sZS9sYW1iZGFfYmFzaWNfZXhlY3V0aW9uIiwKICAgICAgImF3c1JlZ2lvbiI6ICJldS13ZXN0LTEiLAogICAgICAiZXZlbnRTb3VyY2VBUk4iOiAiYXJuOmF3czpraW5lc2lzOmV1LXdlc3QtMTo4MzE2NTA4MTg1MTM6c3RyZWFtL3dvcmtzaG9wIgogICAgfQogIF0KfQ=="
    event = json.loads(base64.b64decode(b64event))
    lambda_handler(event, False)
