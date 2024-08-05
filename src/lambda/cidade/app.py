import json
import logging
from typing import Dict, List

# from aux import get_items_from_page
from aux import extract_data_from_document

from my_fetch import fetch_data_from_url

logging.basicConfig(level=logging.INFO)

URL_BASE = "https://www.guiadoturismobrasil.com"


# s3://your-bucket/principal/UF=AC/cidade=xapuri/
# s3://your-bucket/restaurante/UF=AC/cidade=xapuri/
# s3://your-bucket/hotel/UF=AC/cidade=xapuri/


def lambda_handler(event, context):
    logging.info("Received event: %s", json.dumps(event))
    logging.info("Context: %s", context)

    for record in event["Records"]:
        body = json.loads(record["body"])
        url: str = f"{URL_BASE}{body['href']}"

        document = fetch_data_from_url(url=url)

        items_from_page: Dict[str, str | List[str]] = extract_data_from_document(
            document=document
        )

        result = {
            "uf": body["uf"],
            "nome": body["nome"],
            "url": url,
            "data": items_from_page,
        }

        # result_send_sqs = send_to_sqs(cidades_list=cidades_list)

        return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Processar um arquivo JSON.")
    parser.add_argument("json_file", type=str, help="Caminho para o arquivo JSON")
    args = parser.parse_args()
    json_file_path = args.json_file

    with open(json_file_path, "r") as f:
        data = json.load(f)
        print(f"Conteúdo do arquivo JSON: {data}")

    lambda_handler(event=data, context=None)
