"""
Este módulo fornece uma implementação de um cliente SQS singleton usando boto3.

A classe SQSClient permite enviar mensagens para uma fila SQS especificada.
"""

import boto3


class SQSClient:
    """
    Classe SQSClient para enviar mensagens para uma fila SQS.

    Esta classe implementa o padrão Singleton para garantir que apenas uma instância do cliente SQS
    seja criada. Utiliza o boto3 para interagir com o serviço SQS da AWS.
    """

    _instance = None

    def __new__(cls, queue_url: str, region_name: str):
        """
        Cria uma nova instância da classe SQSClient se ainda não existir.

        Args:
            queue_url (str): A URL da fila SQS.
            region_name (str): A região onde a fila SQS está localizada.

        Returns:
            SQSClient: A instância única da classe SQSClient.
        """
        if cls._instance is None:
            cls._instance = super(SQSClient, cls).__new__(cls)
            cls._instance.__init__(queue_url=queue_url, region_name=region_name)
        return cls._instance

    def __init__(self, queue_url: str, region_name: str) -> None:
        """
        Inicializa o cliente SQS.

        Args:
            queue_url (str): A URL da fila SQS.
            region_name (str): A região onde a fila SQS está localizada.
        """
        if not hasattr(self, "sqs"):
            self.sqs = boto3.client("sqs", region_name=region_name)
            self.queue_url = queue_url

    @classmethod
    def get_instance(cls, queue_url: str, region_name: str = "sua-regiao"):
        """
        Retorna a instância única da classe SQSClient.

        Args:
            queue_url (str): A URL da fila SQS.
            region_name (str): A região onde a fila SQS está localizada. O padrão é "sua-regiao".

        Returns:
            SQSClient: A instância única da classe SQSClient.
        """
        if cls._instance is None:
            cls._instance = cls(queue_url, region_name)
        return cls._instance

    def send_to_sqs(self, message: str) -> dict:
        """
        Envia uma mensagem para a fila SQS.

        Args:
            message (str): A mensagem a ser enviada para a fila SQS.

        Returns:
            dict: Um dicionário contendo o código de status e uma mensagem de sucesso.
        """
        response = self.sqs.send_message(QueueUrl=self.queue_url, MessageBody=message)
        print(f'Mensagem enviada para SQS: {response["MessageId"]}')
        return {"statusCode": 200, "body": "Mensagem enviada com sucesso!"}
