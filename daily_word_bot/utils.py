import re
import typing


def highlight(w: str) -> str:
    return f"<b>{w}</b>"


def highlight_in_sentence(s: str, terms: str) -> str:
    # quitar artculos
    regex = r"/die |das |der |el |la /g"
    terms_without_articles: typing.List[str] = [re.sub(regex, "", t, flags=re.IGNORECASE) for t in terms.split("/")]

    # highlight terms
    for t in terms_without_articles:
        s = re.sub(f"({t})", r"<b>\1</b>", s, flags=re.IGNORECASE)
    return s
