import boto3


class SQSClient:
    _instance = None

    def __new__(cls, queue_url: str, region_name: str):
        if cls._instance is None:
            cls._instance = super(SQSClient, cls).__new__(cls)
            cls._instance._init_client(queue_url=queue_url, region_name=region_name)
        return cls._instance

    def _init_client(self, queue_url: str, region_name: str) -> None:
        self.sqs = boto3.client("sqs", region_name=region_name)
        self.queue_url = queue_url

    @classmethod
    def get_instance(cls, queue_url: str, region_name: str = "sua-regiao"):
        if cls._instance is None:
            cls._instance = cls(queue_url, region_name)
        return cls._instance

    def send_to_sqs(self, message: str) -> dict:
        response = self.sqs.send_message(QueueUrl=self.queue_url, MessageBody=message)
        print(f'Mensagem enviada para SQS: {response["MessageId"]}')
        return {"statusCode": 200, "body": "Mensagem enviada com sucesso!"}
