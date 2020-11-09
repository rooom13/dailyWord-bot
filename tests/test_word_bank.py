import unittest
import pytest

from daily_word_bot.word_bank import WordBank

tc = unittest.TestCase()


def test_word_bank():
    word_bank = WordBank()
    word_bank.df.to_csv("./resources/word_bank.csv", sep=";")

    df = word_bank.df.head(5)
    print(word_bank.get_random(exclude=["WID1", "WID2", "WID3", "WID4"]))

 