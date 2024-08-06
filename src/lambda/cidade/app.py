import os
from argparse import Namespace
import json
import logging
from typing import Dict, List, Union

from fetch_pagination import extract_accomodation, extract_gastronomy
from aux import extract_description_from_document, get_timestamp
from my_fetch import fetch_data_from_url
from my_sns import SNSTopicClient
from s3_operation import save_to_s3


logging.basicConfig(level=logging.INFO)


# S3
# Prefixo: cidades/
# Estrutura: cidades/estado=XX/cidade=nome_cidade/

# Prefixo: hospedagens/
# Estrutura: hospedagens/estado=XX/cidade=nome_cidade/id_hospedagem/

# Prefixo: gastronomia/
# Estrutura: gastronomia/estado=XX/cidade=nome_cidade/id_restaurante/


def lambda_handler(event, context):
    logging.info("Received event: %s", json.dumps(event))
    logging.info("Context: %s", context)

    url_base: str = os.environ["URL_BASE"]
    bucket_name: str = os.environ["BUCKET_NAME"]
    topic_arn: str = os.environ["SNS_TOPIC_ARN"]
    sns_client = SNSTopicClient(topic_arn)

    for record in event["Records"]:
        body = json.loads(record["body"])
        url: str = f"{url_base}{body['href']}"

        # Extrai a UF e nome da cidade
        uf = body["uf"]
        cidade = body["nome"]

        # Processamento dos dados
        document = fetch_data_from_url(url=url)
        page_description: Dict[str, List[str]] = extract_description_from_document(
            document=document
        )
        page_accommodation: Dict[str, List[str]] = extract_accomodation(url_base=url)
        page_gastronomy: Dict[str, List[str]] = extract_gastronomy(url_base=url)

        combined_data: Dict[str, Union[List[str], str]] = {
            **page_description,
            **page_accommodation,
            **page_gastronomy,
            "timestamp": get_timestamp(),
        }

        sns_client.send_to_sns(combined_data)

        # Salva os dados processados no S3
        save_to_s3(bucket_name=bucket_name, uf=uf, cidade=cidade, data=combined_data)

        return {
            "statusCode": 200,
            "body": json.dumps("Processamento concluído com sucesso!"),
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Processar um arquivo JSON.")
    parser.add_argument("json_file", type=str, help="Caminho para o arquivo JSON")
    args: Namespace = parser.parse_args()
    json_file_path = args.json_file

    with open(file=json_file_path, mode="r") as f:
        data = json.load(f)
        print(f"Conteúdo do arquivo JSON: {data}")

    lambda_handler(event=data, context=None)
