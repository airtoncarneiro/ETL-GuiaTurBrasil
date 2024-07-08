import os
import json
from datetime import datetime

import requests
from lxml import html
from my_sqs import SQSClient


def fetch_data_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return html.fromstring(response.content)


def get_page_cidades():
    URL = "https://www.guiadoturismobrasil.com/cidades"
    document = fetch_data_from_url(url=URL)

    cidades_link = document.xpath("//a[contains(@class, 'link-cidades')]")
    cidades_list = []

    for cidade in cidades_link:
        _href = cidade.get("href")
        _title = cidade.get("title")
        if _title:
            _nome, _uf = _title.split("/")

            cidades_list.append({"uf": _uf, "nome": _nome, "href": _href})

            if len(cidades_list) == 5:
                break

    return cidades_list


def send_to_sqs(cidades_list):
    region_name = os.getenv(key="AWS_REGION", default="")
    queue_url = os.getenv(key="SQS_QUEUE_URL", default="")

    if "" in {region_name, queue_url}:
        raise ValueError("REGION_NAME and SQS_QUEUE_URL must be set")

    sqs_client = SQSClient.get_instance(queue_url=queue_url, region_name=region_name)

    for json_data in cidades_list:
        json_data["timestamp"] = datetime.now().isoformat()
        message_body = json.dumps(json_data)
        print(message_body)
        sqs_client.send_to_sqs(message=message_body)

    return {"statusCode": 200, "body": "Hello from Lambda!"}


def handle_error(e):
    print(f"Error: {e}")
    return {
        "statusCode": 500,
        "body": json.dumps({"message": "Error occurred", "error": str(e)}),
    }


def lambda_handler(event, context):
    try:
        cidades_list = get_page_cidades()
        return send_to_sqs(cidades_list=cidades_list)
    except Exception as e:
        return handle_error(e)


if __name__ == "__main__":
    lambda_handler(event={}, context=None)
