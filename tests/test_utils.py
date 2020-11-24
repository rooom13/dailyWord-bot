import pytest
import unittest

from daily_word_bot import utils


tc = unittest.TestCase()


def test_highlight():
    res = utils.highlight("a")
    tc.assertEqual(res, "<b>a</b>")


@pytest.mark.parametrize("terms,expected", [
    ("el Pato/la pata", ["Pato", "pata"]),
    ("der Pato/die pata/das Pate", ["Pato", "pata", "Pate"]),
    ("El Pato/La pata", ["Pato", "pata"]),
    ("Der Pato/Die pata/Das Pate", ["Pato", "pata", "Pate"]),
])
def test_get_terms_without_articles(terms, expected):

    res = utils.get_terms_without_articles(terms)
    tc.assertEqual(res, expected)


@pytest.mark.parametrize("terms,sentence,expected", [
    ("el pato", "Ella besó al Pato", "Ella besó al <b>Pato</b>"),
    ("la pata", "Ella besó Pata", "Ella besó <b>Pata</b>"),
])
def test_highlight_in_sentence(terms, sentence, expected):
    res = utils.highlight_in_sentence(sentence, terms)
    tc.assertEqual(res, expected)


def test_build_word_msg():
    word_data = {
        "es": "el pato/la pata",
        "de": "der pato/die pata",
        "examples": [
            {
                "es": "el pato baila",
                "de": "der pato baila"
            },
            {
                "es": "una pata baila",
                "de": "Nein pata baila"
            }
        ]
    }

    res = utils.build_word_msg(word_data)

    tc.assertEqual(res,
                   "\n🇩🇪 der pato/die pata"
                   "\n🇪🇸 el pato/la pata"
                   "\n"
                   "\n🇩🇪 der <b>pato</b> baila"
                   "\n🇪🇸 el <b>pato</b> baila"
                   "\n"
                   "\n🇩🇪 Nein <b>pata</b> baila"
                   "\n🇪🇸 una <b>pata</b> baila")
