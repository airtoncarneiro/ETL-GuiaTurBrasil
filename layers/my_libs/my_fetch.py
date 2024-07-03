from requests_html import HTMLSession, HTMLResponse


def fetch_data_from_url(url: str):
    session: HTMLSession = HTMLSession()
    return session.get(url=url)
