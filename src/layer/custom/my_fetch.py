"""
Busca dados de uma URL usando requests-html, com cabeçalhos personalizáveis, tempo limite e
tratamento de erros.
"""

from typing import Optional, Dict
from requests_html import HTMLSession


def fetch_data_from_url(
    url: str = "",
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 10,
):
    """
    Busca dados de uma URL fornecida.

    Args:
        url (str): A URL de onde buscar os dados.
        headers (dict, opcional): Um dicionário de cabeçalhos HTTP a incluir na solicitação.
        O padrão é {"User-Agent": "GuiaTurUserAgent"}.
        timeout (int, opcional): O tempo máximo em segundos para esperar por uma resposta antes de
        gerar um erro de tempo limite. O padrão é 10.

    Retorna:
        requests_html.HTML: O objeto de HTML contendo os dados buscados.

    Lança:
        ValueError: Se a URL não for fornecida ou for uma string vazia.
        requests.exceptions.RequestException: Se ocorrer um erro ao fazer a solicitação, como
        um tempo limite ou URL inválida.
    """
    if not url:
        raise ValueError("A URL deve ser fornecida e não pode ser uma string vazia.")

    if headers is None:
        headers = {"User-Agent": "GuiaTurUserAgent"}

    session = HTMLSession()
    try:
        response = session.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.html  # Retorna o objeto HTML para parsing com requests-html
    except requests.exceptions.ReadTimeout as e:
        raise SystemExit("A solicitação atingiu o tempo limite") from e
    except requests.exceptions.RequestException as e:
        raise SystemExit(e) from e


if __name__ == "__main__":
    url = "https://www.guiadoturismobrasil.com/cidade/AC/222/xapuri"
    document = fetch_data_from_url(url)
    print(document.text)
