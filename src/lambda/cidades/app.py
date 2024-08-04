"""
Este módulo fornece funcionalidades para buscar dados de cidades do site Guia do Turismo Brasil,
enviar esses dados para uma fila SQS da AWS e lidar com erros de execução. Ele inclui funções
para buscar dados da web, processar os dados e enviá-los para a fila SQS, além de um handler para
execução em um ambiente Lambda da AWS.
"""

import json
import logging

from aux import extract_cidades_from_page, send_to_sqs
from my_fetch import fetch_data_from_url

logging.basicConfig(level=logging.INFO)

URL = "https://www.guiadoturismobrasil.com/cidades"


def lambda_handler(event, context):
    """
    Handler principal para execução em um ambiente Lambda da AWS.
    """
    logging.info("Received event: %s", json.dumps(event))
    logging.info("Context: %s", context)

    document = fetch_data_from_url(url=URL)
    cidades_list = extract_cidades_from_page(document)
    result_send_sqs = send_to_sqs(cidades_list=cidades_list)

    return result_send_sqs


if __name__ == "__main__":
    lambda_handler({}, None)
