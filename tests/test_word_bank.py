import unittest

from daily_word_bot.word_bank import WordBank

tc = unittest.TestCase()


def test_word_bank():
    # user excludes some words and has all levels assigned
    word_bank = WordBank(local=True, local_path="tests/resources/word_bank.csv")
    random_word = word_bank.get_random(['beginner', 'intermediate', 'advanced'], exclude=["WID1", "WID2", "WID3", "WID4"])
    tc.assertEqual(random_word.get("word_id"), "WID5")

    # user excludes some words, has only one level assigned, which there are no words for
    word_bank = WordBank(local=True, local_path="tests/resources/word_bank.csv")
    random_word = word_bank.get_random(['advanced'], exclude=["WID1", "WID2", "WID3", "WID4"])
    tc.assertEqual(random_word, {})

    # user excludes some words, has only one level assigned, which there are words for
    random_word = word_bank.get_random(['intermediate'], exclude=["WID1", "WID2", "WID3", "WID4", "WID5"])
    tc.assertIn("word_id", random_word)
    tc.assertIn("es", random_word)
    tc.assertIn("de", random_word)
    tc.assertIn("examples", random_word)

    # user excludes no words and has only one level assigned, which there are words for (including a word with no level)
    random_word = word_bank.get_random(['intermediate'], exclude=[])
    tc.assertIn("word_id", random_word)
    tc.assertIn("es", random_word)
    tc.assertIn("de", random_word)
    tc.assertIn("examples", random_word)
    tc.assertTrue("WID1" == random_word.get("word_id") or "WID2" == random_word.get("word_id"))

    # user excludes no words, and has no levels assigned
    random_word = word_bank.get_random([], exclude=[])
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
