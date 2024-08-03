import boto3
import os
import json
import requests

sns_client = boto3.client("sns")


def lambda_handler(event, context):

    for record in event["Records"]:

        message_body = json.loads(record["body"])

        uf = message_body["uf"]
        nome = message_body["nome"]
        href = message_body["href"]
        timestamp = message_body["timestamp"]

        base_url = "https://example.com"
        full_url = f"{base_url}{href}"

        try:

            response = requests.get(full_url)
            response.raise_for_status()

            content = response.text

            sns_message = {
                "uf": uf,
                "nome": nome,
                "conteudo": content,
                "timestamp": timestamp,
            }

            sns_response = sns_client.publish(
                TopicArn=os.environ["CIDADE_TOPIC_ARN"], Message=json.dumps(sns_message)
            )

            print(f"Mensagem enviada para SNS: {sns_response}")

        except requests.exceptions.RequestException as e:
            print(f"Erro ao fazer a requisição para {full_url}: {e}")

    return {"statusCode": 200, "body": "Processamento completo"}
