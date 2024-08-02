"""
Busca dados de uma URL usando requests, com cabeçalhos personalizáveis, tempo limite e
tratamento de erros.
"""

from typing import Optional, Dict
import requests
from lxml import html


def fetch_data_from_url(
    url: str = "",
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 10,
) -> requests.Response:
    """
    Busca dados de uma URL fornecida.

    Args:
        url (str): A URL de onde buscar os dados.
        headers (dict, opcional): Um dicionário de cabeçalhos HTTP a incluir na solicitação.
        O padrão é {"User-Agent": "GuiaTurUserAgent"}.
        timeout (int, opcional): O tempo máximo em segundos para esperar por uma resposta antes de
        gerar um erro de tempo limite. O padrão é 10.

    Retorna:
        requests.Response: O objeto de resposta contendo os dados buscados.

    Lança:
        ValueError: Se a URL não for fornecida ou for uma string vazia.
        requests.exceptions.RequestException: Se ocorrer um erro ao fazer a solicitação, como
        um tempo limite ou URL inválida.
    """
    if not url:
        raise ValueError("A URL deve ser fornecida e não pode ser uma string vazia.")

    if headers is None:
        headers = {"User-Agent": "GuiaTurUserAgent"}

    try:
        response: requests.Response = requests.get(
            url, headers=headers, timeout=timeout
        )
        response.raise_for_status()
        return html.fromstring(response.content)
    except requests.exceptions.ReadTimeout as e:
        raise SystemExit("A solicitação atingiu o tempo limite") from e
    except requests.exceptions.RequestException as e:
        raise SystemExit(e) from e
