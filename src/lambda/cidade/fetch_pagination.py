from my_fetch import fetch_data_from_url
from aux import css_find


def mount_url(city_url: str, fetch_url) -> str:
    uf: str
    city_name: str
    city_cod: str
    uf, city_name, city_cod = city_url.split("/")[-3:]

    return fetch_url + f"{uf}/{city_cod}/{city_name}"


def count_pagination(document) -> int:
    css: str = "ul.pagination > li"
    qtd: int = len(css_find(document=document, css=css))

    return qtd - 2


def extract_links(url: str) -> list[str]:
    document = fetch_data_from_url(url=url)

    total_page: int = count_pagination(document=document)
    current_page: int = 0
    css: str = "div.col-xs-10.text-left > a"

    links_list: list[str] = list()
    while current_page < total_page:
        links = css_find(document=document, css=css)
        for link in links:
            links_list.append(link.attrs.get("href"))
        current_page += 1
        document = fetch_data_from_url(url=f"{url}/{current_page}")
        break

    return links_list


def extract_accomodation(url_base: str) -> dict[str, list[str]]:
    fetch_url: str = "https://www.guiadoturismobrasil.com/hospedagem/2/"
    url: str = mount_url(city_url=url_base, fetch_url=fetch_url)
    url = "https://www.guiadoturismobrasil.com/hospedagem/2/SP/sao-paulo/193"

    links: list[str] = extract_links(url=url)

    return {"hospedagem": links}


def extract_gastronomy(url_base: str) -> dict[str, list[str]]:
    fetch_url: str = "https://www.guiadoturismobrasil.com/gastronomia/3"
    url: str = mount_url(city_url=url_base, fetch_url=fetch_url)
    url = "https://www.guiadoturismobrasil.com/gastronomia/3/SP/sao-paulo/193"

    links: list[str] = extract_links(url=url)

    return {"gastronomia": links}
