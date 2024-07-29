"""
Este módulo fornece funcionalidades para buscar dados de cidades do site Guia do Turismo Brasil,
enviar esses dados para uma fila SQS da AWS e lidar com erros de execução. Ele inclui funções
para buscar dados da web, processar os dados e enviá-los para a fila SQS, além de um handler para
execução em um ambiente Lambda da AWS.
"""

import os
import json
import logging
from datetime import datetime

import requests
from lxml import html
from my_sqs import SQSClient

logging.basicConfig(level=logging.INFO)


def fetch_data_from_url(url, timeout=10):
    """
    Busca dados de uma URL e retorna o conteúdo HTML como um documento lxml.

    Args:
        url (str): A URL de onde buscar os dados.
        timeout (int): O tempo máximo em segundos para esperar por uma resposta. Padrão é 10.

    Returns:
        lxml.html.HtmlElement: O documento HTML parseado.

    Raises:
        requests.exceptions.RequestException: Se ocorrer um erro ao fazer a solicitação.
    """
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return html.fromstring(response.content)


def get_page_cidades():
    """
    Busca e processa dados de cidades do site Guia do Turismo Brasil.

    Returns:
        list: Uma lista de dicionários contendo informações das cidades.

    Exemplo de retorno:
        [
            {"uf": "SP", "nome": "sao-paulo", "href": "/cidades/sp/sao-paulo"},
            ...
        ]
    """
    url = "https://www.guiadoturismobrasil.com/cidades"
    document = fetch_data_from_url(url=url)

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
        ValueError: Se as variáveis de ambiente AWS_REGION ou SQS_QUEUE_URL não estiverem definidas.
    """
    region_name = os.getenv(key="AWS_REGION", default="")
    queue_url = os.getenv(key="SQS_QUEUE_URL", default="")

    if "" in {region_name, queue_url}:
        raise ValueError("REGION_NAME and SQS_QUEUE_URL must be set")

    sqs_client = SQSClient.get_instance(queue_url=queue_url, region_name=region_name)

    for json_data in cidades_list:
        json_data["timestamp"] = datetime.now().isoformat()
        message_body = json.dumps(json_data)
        logging.info(message_body)
        sqs_client.send_to_sqs(message=message_body)

    return {"statusCode": 200, "body": "Hello from Lambda!"}


def handle_error(error):
    """
    Lida com erros, registrando a mensagem de erro e retornando uma resposta adequada.

    Args:
        error (Exception): A exceção que ocorreu.

    Returns:
        dict: Um dicionário com o código de status e uma mensagem de erro.
    """
    logging.error("Error: %s", error)
    return {
        "statusCode": 500,
        "body": json.dumps({"message": "Error occurred", "error": str(error)}),
    }


def lambda_handler(event, context):
    """
    Handler principal para execução em um ambiente Lambda da AWS.

    Args:
        event (dict): O evento que aciona o Lambda.
        context (object): O contexto de execução do Lambda.

    Returns:
        dict: A resposta resultante da execução das funções de busca e envio de dados.
    """
    logging.info("Received event: %s", json.dumps(event))
    logging.info("Context: %s", context)

    try:
        cidades_list = get_page_cidades()
        return send_to_sqs(cidades_list=cidades_list)
    except requests.exceptions.HTTPError as http_err:
        return handle_error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        return handle_error(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        return handle_error(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        return handle_error(f"An error occurred with the request: {req_err}")
    except ValueError as val_err:
        return handle_error(f"Value error occurred: {val_err}")
    except Exception as error:
        return handle_error(f"An unexpected error occurred: {error}")


if __name__ == "__main__":
    lambda_handler({}, None)
