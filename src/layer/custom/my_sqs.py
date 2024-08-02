"""
Este módulo fornece uma implementação de um cliente SQS monostate usando boto3.

A classe SQSClient permite enviar mensagens para uma fila SQS especificada.
"""

import boto3


class SQSQueueClient:
    """
    Classe SQSClient para enviar mensagens para uma fila SQS.

    Esta classe implementa o padrão Monostate para garantir que todas as instâncias do cliente SQS
    compartilhem o mesmo estado. Utiliza o boto3 para interagir com o serviço SQS da AWS.
    """

    _shared_state = {}

    def __init__(self, queue_url: str, region_name: str) -> None:
        """
        Inicializa o cliente SQS e compartilha o estado entre todas as instâncias.

        Args:
            queue_url (str): A URL da fila SQS.
            region_name (str): A região onde a fila SQS está localizada.
        """
        self.__dict__ = self._shared_state
        if not hasattr(self, "initialized"):
            self.sqs = boto3.client("sqs", region_name=region_name)
            self.queue_url = queue_url
            self.initialized = True

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


# # Exemplo de uso
# if __name__ == "__main__":
#     PARAM_QUEUE_URL = "sua-url-da-fila"
#     PARAM_REGION_NAME = "sua-regiao"
#     client1 = SQSClient(queue_url=PARAM_QUEUE_URL, region_name=PARAM_REGION_NAME)

#     # Envia mensagem para SQS
#     client1.send_to_sqs(message="Hello, SQS!")
