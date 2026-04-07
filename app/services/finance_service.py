import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "transactions.csv")


class FinanceService:
    def __init__(self):
        self.df = pd.read_csv(DATA_PATH)
        self.df.columns = self.df.columns.str.lower()

    # -----------------------------
    # 1. Extract Category from text
    # -----------------------------
    def extract_category(self, user_text: str):
        categories = self.df["category"].unique()

        user_text = user_text.lower()

        for cat in categories:
            if cat.lower() in user_text:
                return cat

        return None

    # -----------------------------
    # 2. Get total expense for category
    # -----------------------------
    def get_category_expense(self, category: str):
        filtered = self.df[self.df["category"].str.lower() == category.lower()]

        total = filtered["amount"].sum()

        return {
            "category": category,
            "total": round(total, 2)
        }

    # -----------------------------
    # 3. Get overall summary
    # -----------------------------
    def get_summary(self):
        total_spent = self.df["amount"].sum()

        category_breakdown = (
            self.df.groupby("category")["amount"]
            .sum()
            .to_dict()
        )

        return {
            "total_spent": round(total_spent, 2),
            "category_breakdown": category_breakdown
        }