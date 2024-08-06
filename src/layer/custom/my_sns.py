from typing import Dict, List, Union
import logging
import boto3


class SNSTopicClient:
    def __init__(self, topic_arn: str):
        self.sns_client = boto3.client("sns")
        self.topic_arn: str = topic_arn

    def _send_to_sns(self, message: str):
        """
        Publica uma mensagem no tópico SNS especificado.

        :param message: Dicionário de dados a serem enviados, com valores que podem ser listas de strings ou strings
        """
        try:
            response = self.sns_client.publish(
                TopicArn=self.topic_arn, Message=message, Subject="Dados da Cidade"
            )

            logging.info("Mensagem enviada para SNS: %s", response["MessageId"])
        except Exception as e:
            logging.error("Erro ao enviar mensagem para SNS: %s", e)

    def send_to_sns(self, message: Dict[str, Union[List[str], str]]):
        keys_to_send: List[str] = ["hospedagem", "gastronomia"]

        for key, value in message.items():
            if key in keys_to_send:
                for message in value:
                    self._send_to_sns(message=message)
