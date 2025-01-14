"""
Main handler for catalog shop
"""
import os
import simplejson
import boto3
import requests
import logging
logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.CRITICAL)
from uuid import uuid4
from googleapiclient.discovery import build
from update_db import CATALOG_ITEMS



DYNAMODB_CLIENT = boto3.resource('dynamodb')
CATALOG_TABLE = DYNAMODB_CLIENT.Table(os.getenv('CATALOG_TABLE'))
SNS_CLIENT = boto3.client('sns')
SES_CLIENT = boto3.client('ses', region_name='us-east-1')
GCS = build('customsearch', 'v1', developerKey=os.getenv('GOOGLE_KEY'), cache_discovery=False)


def get_items(event, context):
    """
    Get list of items from the CatalogDB
    """
    items = CATALOG_TABLE.scan()['Items']

    # Fetch image for each item.
    for item in items:
        #image_link = GCS.cse().list(q=item['name'], cx=os.getenv('GOOGLE_CX'), num=5).execute()['items'][0]['pagemap']['cse_image'][0]['src']
        # item['link'] = "https://images-na.ssl-images-amazon.com/images/I/61mcoYG4WTL._AC_SL1000_.jpg"
        item['link'] = item['image_url']

    return {
        'statusCode': 200,
        'body': simplejson.dumps(items, use_decimal=True),
        'headers': {
            'Access-Control-Allow-Origin': '*'
        }
    }


def set_items(event, context):
    """
    Get list of items from the CatalogDB
    """
    print(event)
    results = CATALOG_TABLE.scan()
    for item in results['Items']:
        CATALOG_TABLE.delete_item(
            Key={'item_id': item['item_id']}
        )

    # Add new
    for i in range(int(event['pathParameters']['count'])):
        CATALOG_TABLE.put_item(
            Item=CATALOG_ITEMS[i]
        )

    return {
        'statusCode': 200,
        'body': event['pathParameters']['count'],
        'headers': {
            'Access-Control-Allow-Origin': '*'
        }
    }


def payment(event, context):
    """
    Buy an item from the store
    """
    print(event)
    order_id = str(uuid4())
    temp_body = simplejson.loads(event['body'])
    temp_body['order_id'] = order_id
    event['body'] = simplejson.dumps(temp_body)
    requests.get('https://api.stripe.com/v1/charges', headers={'Authorization': 'Bearer sk_test_4eC39HqLyjWDarjtT1zdp7dc'})

    SNS_CLIENT.publish(
        TopicArn=os.getenv('PAYMENT_TOPIC'),
        Message=event['body'],
        Subject='New purchase - {}'.format(order_id),
    )

    return {
        'statusCode': 200,
        'body': simplejson.dumps({'order_id': order_id}),
        'headers': {
            'Access-Control-Allow-Origin': '*'
        }
    }
    
def order_fullfilment(event, context):
    """
    handles purchase
    """

    body = simplejson.loads(event['Records'][0]['Sns']['Message'])
    buyer_email = body['email']
    order_id = body['order_id']
    print('Handling new order from {}'.format(buyer_email))

    purchased_items = 'Purchased to following items: '

    for item in body['items']:
        purchased_items += '{} '.format(item['name'])
        response = CATALOG_TABLE.update_item(
            Key={'item_id': item['item_id']},
            UpdateExpression='ADD stock_left :dec',
            ExpressionAttributeValues={
                ':dec': -1,
                ':minimum': 0
            },
            ConditionExpression='stock_left > :minimum'
        )
        print(response)

    response = SES_CLIENT.send_email(
        Source='"The Serverless Shop" <support@epsagon.com>',
        Destination={'ToAddresses': [buyer_email]},
        Message={
            'Subject': {
                'Data': 'New purchase ({})'.format(order_id)
            },
            'Body': {
                'Html': {
                    'Data': purchased_items
                },
                'Text': {
                    'Data': purchased_items
                },
            }
        }
    )
    print(response)

    return {
        'statusCode': 200,
        'body': 'success',
        'headers': {
            'Access-Control-Allow-Origin': '*'
        }
    }
