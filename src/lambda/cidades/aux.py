"""
Módulo para processar e enviar dados de cidades para a AWS SQS.
"""

from datetime import datetime
import json
import logging
import os

from my_sqs import SQSQueueClient


def extract_cidades_from_page(document):
    """
    Busca e processa dados de cidades do site Guia do Turismo Brasil.
    """
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
    """
    Envia uma lista de cidades para uma fila SQS da AWS.

    Args:
        cidades_list (list): A lista de dicionários contendo informações das cidades.

    Returns:
        dict: Um dicionário com o código de status e uma mensagem de sucesso.

    Raises:
        ValueError: Se as variáveis de ambiente AWS_REGION ou SQS_QUEUE_CIDADES_URL não estiverem definidas.
    """
    region_name: str = os.getenv(key="REGION_NAME", default="")
    cidades_queue_url: str = os.getenv(key="CIDADES_QUEUE_URL", default="")

    if "" in {region_name, cidades_queue_url}:
        raise ValueError("REGION_NAME and SQS_QUEUE_CIDADES_URL must be set")

    sqs_client = SQSQueueClient(queue_url=cidades_queue_url, region_name=region_name)

    # sqs_client = SQSClient.get_instance(queue_url=queue_url, region_name=region_name)
    for cidade_data in cidades_list:
        cidade_data["timestamp"] = datetime.now().isoformat()
        message_body = json.dumps(cidade_data)
        logging.info("Enviando mensagem para SQS: %s", message_body)
        sqs_client.send_to_sqs(message=message_body)
        logging.info("Mensagem envianda.")

    return {"statusCode": 200, "body": "Mensagens enviadas com sucesso!"}
