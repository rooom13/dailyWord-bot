import typing

from datetime import datetime

import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from gspread import Spreadsheet, Worksheet


class WordBank:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    spreadsheet_name: str = "Must learn Deutsch Worten"
    worksheet_name: str = "words"

    df: pd.DataFrame = None
    last_updated_at = None

    def __init__(self, local: bool = False, local_path: typing.Union[str] = "resources/word_bank.csv"):
        self.local = local
        self.local_path = local_path
        self.update()

    def update(self) -> None:
        """Updates the df by fetching current Google Spreadsheets document"""

        if self.local:
            df = pd.read_csv(self.local_path, sep=";").set_index("word_id").head(5)
        else:  # pragma: no cover
            credentials: ServiceAccountCredentials = ServiceAccountCredentials.from_json_keyfile_name('service-account.json', self.scope)
            gc: gspread.client.Client = gspread.authorize(credentials)
            spreadsheet: Spreadsheet = gc.open(self.spreadsheet_name)
            worksheet: Worksheet = spreadsheet.worksheet(self.worksheet_name)
            data: list = worksheet.get_all_values()

            data.pop(0)  # discard explanation row
            header = data.pop(0)
            df = pd.DataFrame(data, columns=header)

            cols_de = df.columns[df.columns.str.startswith("Deutsch")].to_list()
            cols_es = df.columns[df.columns.str.startswith("Spanisch")].to_list()
            cols = ["word_id"] + cols_de + cols_es

            df = pd.DataFrame(data, columns=header)[cols].set_index("word_id")
        self.df = df
        self.last_updated_at = str(datetime.now())

    def get_random(self, exclude: list = []) -> dict:
        if len(exclude) >= len(self.df.index):
            exclude = []

        df_candidates = self.df.loc[~self.df.index.isin(exclude)]
        row = df_candidates.sample().iloc[0]

        examples: typing.List[dict] = []
        for i in range(1, 5):
            ex_de = row[f"Deutscher Ausdruck {i}"]
            ex_es = row[f"Spanischer Ausdruck {i}"]
            if isinstance(ex_de, str) and isinstance(ex_es, str) and ex_de != "" and ex_es != "":
                examples.append({"es": ex_es, "de": ex_de})

        word_data = {
            "de": row["Deutsch"],
            "es": row["Spanisch"],
            "word_id": row.name,  # index
            "examples": examples
        }

        return word_data
