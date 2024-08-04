"""
Módulo para processar e enviar dados de cidades para a AWS SQS.
"""

from datetime import datetime
import json
import logging
import os
from typing import Dict, List
from my_sqs import SQSQueueClient


def css_find(document, css):
    return document.find(css)


def extract_cidades_from_page(document):
    """
    Busca e processa dados de cidades do site Guia do Turismo Brasil.
    """
    # Use find ao invés de cssselect
    cidades_link = css_find(document=document, css="a.link-cidades")
    cidades_list = []

    for cidade in cidades_link:
        _href = cidade.attrs.get("href")
        _title = cidade.attrs.get("title")
        if _title:
            _nome, _uf = _title.split("/")
            cidades_list.append({"uf": _uf, "nome": _nome, "href": _href})
            if len(cidades_list) == 5:
                break

    return cidades_list


def extract_data_from_document(document) -> Dict[str, List[str]]:
    # Dicionário de seletores CSS para diferentes tipos de dados
    css_selectors: dict[str, str] = {
        "subtitles": ".subtitulo",
        "descriptions": ".subtitulo + br + p",
        "image_links": "a.fancybox",
        "accommodations": "select.form-control > option[value^='/hospedagem']",
        "restaurants": "select.form-control > option[value^='/gastronomia']",
    }

    extracted_data: Dict[str, List[str]] = {}
    data_list: List[str]

    for data_type, css_selector in css_selectors.items():
        elements = css_find(document=document, css=css_selector)

        if data_type in ["subtitles", "descriptions"]:
            data_list = [element.text for element in elements]
        elif data_type == "image_links":
            data_list = [element.attrs["href"] for element in elements]
        elif data_type in ["accommodations", "restaurants"]:
            data_list = [element.attrs["value"] for element in elements]
        else:
            data_list = []

        extracted_data[data_type] = data_list

    return extracted_data


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
        logging.info("Mensagem enviada.")

    return {"statusCode": 200, "body": "Mensagens enviadas com sucesso!"}
