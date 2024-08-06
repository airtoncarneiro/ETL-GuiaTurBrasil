import boto3
import json
from typing import Dict, List, Union
import logging

# Inicialize o cliente do S3
s3_client = boto3.client("s3")


def save_to_s3(
    bucket_name: str, uf: str, cidade: str, data: Dict[str, Union[List[str], str]]
) -> None:
    """
    Salva os dados processados no S3 em um caminho particionado por UF e cidade.

    :param bucket_name: Nome do bucket S3
    :param uf: Unidade federativa (estado)
    :param cidade: Nome da cidade
    :param data: Dados a serem salvos
    """
    # Crie o caminho do arquivo no S3 usando o prefixo sugerido
    s3_key = f"cidades/estado={uf}/cidade={cidade}/detalhes.json"

    # Convertendo os dados para JSON
    json_data = json.dumps(data, ensure_ascii=False)

    try:
        # Salva os dados no S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=json_data,
            ContentType="application/json",
        )
        logging.info(f"Dados salvos com sucesso no S3: s3://{bucket_name}/{s3_key}")
    except Exception as e:
        logging.error(f"Erro ao salvar dados no S3: {e}")
