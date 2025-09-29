import os
import pandas as pd
from services.cleaner import ContactCleaner

class FileHandler:
    def __init__(self, file, column_name: str, output_dir="output"):
        self.file = file
        self.column_name = column_name
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def process_file(self):
        df_original = pd.read_excel(self.file, dtype=str)
        cleaner = ContactCleaner(self.column_name)

        df_translated, df_valid, df_invalid = cleaner.process_dataframe(df_original)

        base_name = os.path.splitext(os.path.basename(self.file.name))[0]
        output_path = os.path.join(self.output_dir, f"{base_name}_processed.xlsx")

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df_original.to_excel(writer, sheet_name="Original", index=False)
            df_translated.to_excel(writer, sheet_name="Translated", index=False)
            df_valid.to_excel(writer, sheet_name="Valid Sorted", index=False)
            df_invalid.to_excel(writer, sheet_name="Invalid Sorted", index=False)

        return output_path, df_original, df_translated, df_valid, df_invalid
