import pandas as pd
import re

class ContactCleaner:
    def __init__(self, column_name: str):
        self.column_name = column_name

    def _normalize_text(self, text: str) -> list:
        """Convert to digits only, handle multiple separators (comma, slash)."""
        if pd.isna(text):
            return []

        numbers = re.split(r"[,/]", str(text))
        cleaned_numbers = [re.sub(r"[^\d]", "", num) for num in numbers]
        return [num for num in cleaned_numbers if num]

    def _is_valid(self, number: str) -> bool:
        """Check if number is a valid Bangladeshi 11-digit mobile (01xxxxxxxxx)."""
        return bool(re.fullmatch(r"01\d{9}", number))

    def process_dataframe(self, df: pd.DataFrame):
        """Return three DataFrames: translated, valid, invalid."""
        translated_rows, valid_rows, invalid_rows = [], [], []

        for _, row in df.iterrows():
            raw_value = row[self.column_name]
            numbers = self._normalize_text(raw_value)

            valid_nums = [f"88{num}" for num in numbers if self._is_valid(num)]
            invalid_nums = [num for num in numbers if not self._is_valid(num)]

            translated_rows.append({
                **row,
                "Valid_Contacts": ", ".join(valid_nums),
                "Invalid_Contacts": ", ".join(invalid_nums)
            })

            if valid_nums:
                valid_rows.append({**row, "Valid_Contacts": ", ".join(valid_nums)})
            if numbers and not valid_nums:
                invalid_rows.append({**row, "Invalid_Contacts": ", ".join(invalid_nums)})

        df_translated = pd.DataFrame(translated_rows)
        df_valid = pd.DataFrame(valid_rows).sort_values(by="Valid_Contacts")
        df_invalid = pd.DataFrame(invalid_rows).sort_values(by="Invalid_Contacts")

        return df_translated, df_valid, df_invalid
