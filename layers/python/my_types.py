from typing import Dict, Union, List
import requests_html

TYPE_LAMBDA_RESPONSE = Dict[str, Union[int, str]]
TYPE_ERROR_RESPONSE = Dict[str, Union[int, str, dict]]
TYPE_ELEMENT = Union[List[requests_html.Element], requests_html.Element]
TYPE_CIDADES_LIST = list[dict[str, str]]
TYPE_LAMBDA_RESPONSE_OR_ERROR_RESPONSE = Union[
    TYPE_LAMBDA_RESPONSE, TYPE_ERROR_RESPONSE
]
