import os
import json
from datetime import datetime

from aws_lambda_powertools.utilities.parser import BaseModel
from aws_lambda_powertools.utilities.typing import LambdaContext


from my_fetch import fetch_data_from_url
from my_sqs import SQSClient
from my_types import (
    TYPE_CIDADES_LIST,
    TYPE_ELEMENT,
    TYPE_ERROR_RESPONSE,
    TYPE_LAMBDA_RESPONSE,
    TYPE_LAMBDA_RESPONSE_OR_ERROR_RESPONSE,
    requests_html,
)


class Cidade(BaseModel):
    uf: str
    nome: str
    href: str


def fetch_cidades() -> TYPE_CIDADES_LIST:
    url = "https://www.guiadoturismobrasil.com/cidades"
    response = fetch_data_from_url(url=url)

    cidades_link: TYPE_ELEMENT = response.html.find(".link-cidades", first=False)
    cidades_list: TYPE_CIDADES_LIST = []

    if isinstance(cidades_link, requests_html.Element):
        cidades_link = [cidades_link]

    for cidade in cidades_link:
        _href = next(iter(cidade.absolute_links))
        _nome, _uf = cidade.attrs["title"].split("/")

        cidade_obj: Cidade = Cidade(uf=_uf, nome=_nome, href=_href)
        cidade_dct: dict[str, str] = cidade_obj.dict()
        cidades_list.append(cidade_dct)

        if len(cidades_list) == 5:
            break

    return cidades_list


def send_to_sqs(cidades_list: list[dict[str, str]]) -> TYPE_LAMBDA_RESPONSE:

    region_name = os.getenv(key="AWS_REGION", default="")
    queue_url = os.getenv(key="SQS_QUEUE_URL", default="")

    if "" in {region_name, queue_url}:
        raise ValueError("AWS_REGION and SQS_QUEUE_URL must be set")

    sqs_client = SQSClient.get_instance(queue_url=queue_url, region_name=region_name)

    for json_data in cidades_list:
        json_data["timestamp"] = datetime.now().isoformat()

        message_body = json.dumps(json_data)
        print(message_body)

        sqs_client.send_to_sqs(message=message_body)

    return {"statusCode": 200, "body": "Hello from Lambda!"}


def handle_error(e: Exception) -> TYPE_ERROR_RESPONSE:
    print(f"Error: {e}")
    return {
        "statusCode": 500,
        "body": json.dumps(obj={"message": "Error occurred", "error": str(e)}),
    }


def lambda_handler(
    event: dict, context: LambdaContext
) -> TYPE_LAMBDA_RESPONSE_OR_ERROR_RESPONSE:
    try:
        cidades_list = fetch_cidades()
        return send_to_sqs(cidades_list=cidades_list)
    except Exception as e:
        return handle_error(e)
