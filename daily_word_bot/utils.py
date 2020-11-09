import re
import typing

from daily_word_bot import utils


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

def build_word_msg(word_data: dict) -> str:

    examples: list = (word_data.get("examples") or [])
    word_de = word_data.get("de", "")
    word_es = word_data.get("es", "")

    examples_str: str = ("\n".join([(
        f"\n🇩🇪 {utils.highlight_in_sentence(ex.get('de', ''), word_de)}"
        f"\n🇪🇸 {utils.highlight_in_sentence(ex.get('es', ''), word_es)}"
    ) for ex in examples]))

    return (
        f"\n🇩🇪 {word_de}"
        f"\n🇪🇸 {word_es}"
        f"\n{examples_str}"
    )