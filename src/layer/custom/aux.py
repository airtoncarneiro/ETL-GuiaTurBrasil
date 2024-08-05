"""
Módulo para processar e enviar dados de cidades para a AWS SQS.
"""

from datetime import datetime
import json
import logging
import os
from typing import Dict, List, Callable, TypedDict
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


class SelectorInfo(TypedDict):
    selector: str
    extract: Callable[[List], List[str]]


def extract_data_from_document(document) -> Dict[str, str | List[str]]:
    # Define funções de extração para cada tipo de dado
    def extract_text(elements) -> List[str]:
        # return [element.text for element in elements]
        # Lista para armazenar os resultados finais
        elements = [element.text for element in elements]
        # Lista para armazenar os resultados finais
        result = []

        # Iterar sobre cada elemento para processar seu texto
        for element in elements:
            start = 0
            text_length = len(element)

            while start < text_length:
                # Define o fim do slice inicialmente para 80 caracteres após o início
                end = min(start + 80, text_length)
                # Se a última posição não for um espaço e não é o final do texto
                if end < text_length and element[end] != " ":
                    # Mover o end para trás até encontrar um espaço
                    while end > start and element[end] != " ":
                        end -= 1

                # Se não encontrou espaço (palavra maior que 80), fatiar mesmo assim
                if end == start:
                    end = start + 80

                # Adiciona o segmento ao resultado
                result.append(element[start:end])
                # Move o início para o próximo segmento
                start = end + 1

        return result

    def extract_href(elements) -> List[str]:
        return [element.attrs.get("href", "") for element in elements]

    def extract_value(elements) -> List[str]:
        return [element.attrs.get("value", "") for element in elements]

    # Dicionário de seletores CSS e suas funções de extração associadas
    css_selectors: Dict[str, SelectorInfo] = {
        "subtitulo": {"selector": ".subtitulo", "extract": extract_text},
        "descricao": {"selector": ".subtitulo + br + p", "extract": extract_text},
        "imagens": {"selector": "a.fancybox", "extract": extract_href},
        "acomodacoes": {
            "selector": "select.form-control > option[value^='/hospedagem']",
            "extract": extract_value,
        },
        "restaurantes": {
            "selector": "select.form-control > option[value^='/gastronomia']",
            "extract": extract_value,
        },
    }

    extracted_data: Dict[str, List[str]] = {}

    for data_type, info in css_selectors.items():
        elements = css_find(document=document, css=info["selector"])
        extract_function = info["extract"]
        extracted_data[data_type] = extract_function(elements)

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
