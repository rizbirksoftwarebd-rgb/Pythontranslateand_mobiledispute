import streamlit as st
import pandas as pd
import re
import os

st.set_page_config(page_title="Mobile Cleaner", page_icon="📊", layout="centered")
st.title("📊 Excel Mobile Cleaner with 88 Prefix")
st.write("Upload an Excel file, preview it, select the mobile column, and generate a cleaned Excel file.")

# -------------------- CLASS DEFINITION --------------------
class MobileCleaner:
    def __init__(self):
        # Translator for Bangla → English digits
        self.bangla_to_english = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")

    def normalize(self, num: str) -> str:
        """Convert Bangla → English digits and remove symbols (+, -, space, etc.)."""
        if pd.isna(num):
            return ""
        num = str(num).translate(self.bangla_to_english)
        return re.sub(r"[^\d]", "", num)  # keep digits only

    def validate_and_format(self, num: str):
        """Return (is_valid, formatted_number)."""
        if not num:
            return False, ""
        # Case 1: Already with 88 prefix
        if num.startswith("88") and len(num) == 13 and num[2:4] == "01":
            return True, num
        # Case 2: Local 11-digit number
        if num.startswith("01") and len(num) == 11:
            return True, "88" + num
        return False, num

    def process_contacts(self, text: str):
        """Process row text: handle multiple contacts separated by ',' or '/'."""
        if pd.isna(text):
            return [], []
        raw_numbers = [x.strip() for x in re.split(r"[,/]", str(text)) if x.strip()]
        valid, invalid = [], []
        for raw in raw_numbers:
            cleaned = self.normalize(raw)
            is_valid, formatted = self.validate_and_format(cleaned)
            if is_valid:
                valid.append(formatted)
            elif cleaned:
                invalid.append(cleaned)
        return sorted(set(valid)), sorted(set(invalid))


# -------------------- FILE UPLOAD --------------------
uploaded_file = st.file_uploader("📂 Upload Excel File (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df_original = pd.read_excel(uploaded_file, dtype=str)
        st.subheader("Preview of Uploaded Data (First 5 Rows)")
        st.dataframe(df_original.head())

        # Dropdown to select mobile column
        column_choice = st.selectbox("📞 Select Column Containing Mobile Numbers", options=df_original.columns)

        if st.button("🔄 Process File"):
            cleaner = MobileCleaner()

            # Use apply for faster processing
            def process_row(text):
                valid, invalid = cleaner.process_contacts(text)
                return pd.Series({
                    "Translated_Contacts": ", ".join(valid + invalid),
                    "Valid_Contacts": ", ".join(valid) if valid else "",
                    "Invalid_Contacts": ", ".join(invalid) if invalid else ""
                })

            processed = df_original[column_choice].apply(process_row)
            translated_df = pd.concat([df_original, processed], axis=1)

            # Extract valid/invalid separately (faster than looping)
            valid_df = translated_df[translated_df["Valid_Contacts"] != ""].copy()
            invalid_df = translated_df[translated_df["Invalid_Contacts"] != ""].copy()

            if not valid_df.empty:
                valid_df = valid_df.sort_values(by="Valid_Contacts")
            if not invalid_df.empty:
                invalid_df = invalid_df.sort_values(by="Invalid_Contacts")

            # Save output
            folder = os.getcwd()
            name, ext = os.path.splitext(uploaded_file.name)
            output_path = os.path.join(folder, f"{name}_processed{ext}")

            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                df_original.to_excel(writer, sheet_name="Input_Data", index=False)
                translated_df.to_excel(writer, sheet_name="Translated_Data", index=False)
                if not valid_df.empty:
                    valid_df.to_excel(writer, sheet_name="Valid_Output", index=False)
                if not invalid_df.empty:
                    invalid_df.to_excel(writer, sheet_name="Invalid_Output", index=False)

            st.success("✅ Processing complete!")
            st.download_button(
                label="📥 Download Processed Excel",
                data=open(output_path, "rb").read(),
                file_name=f"{name}_processed{ext}",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"❌ Error: {e}")

st.markdown("---")
st.markdown("""
👨‍💻 **Developer Info**  
**Name:** Rizbi Islam  
**Role:** QA Engineer & Data Processing Enthusiast  
**Location:** Bangladesh  
""")
