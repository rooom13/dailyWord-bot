import unittest

from daily_word_bot.word_bank import WordBank

tc = unittest.TestCase()


def test_word_bank():
    word_bank = WordBank(local=True, local_path="tests/resources/word_bank.csv")
    random_word = word_bank.get_random(exclude=["WID1", "WID2", "WID3", "WID4"])
    tc.assertEqual(random_word.get("word_id"), "WID5")

    random_word = word_bank.get_random(exclude=["WID1", "WID2", "WID3", "WID4", "WID5"])
    tc.assertIn("word_id", random_word)
    tc.assertIn("es", random_word)
    tc.assertIn("de", random_word)
    tc.assertIn("examples", random_word)


def test_get_words():
    word_bank = WordBank(local=True, local_path="tests/resources/word_bank.csv")
    word_ids = ["WID1", "WID2", "WID3"]
    result = word_bank.get_words(word_ids)
    expected = [{"word_id": 'WID1', "de": 'ab und zu', "es": 'de vez en cuando'},
                {"word_id": 'WID2', "de": 'abändern', "es": 'modificar'},
                {"word_id": 'WID3', "de": 'abdrehen', "es": 'cerrar'}]
    assert result == expected
