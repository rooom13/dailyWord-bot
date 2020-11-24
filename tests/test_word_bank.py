import unittest

from daily_word_bot.word_bank import WordBank

tc = unittest.TestCase()


def test_word_bank():
    word_bank = WordBank(local=True, local_path="tests/resources/word_bank.csv")
    random_word = word_bank.get_random(exclude=["WID1", "WID2", "WID3", "WID4"])
    tc.assertEqual(random_word.get("word_id"), "WID5")
