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
        self.bangla_to_english = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")

    def normalize(self, num: str) -> str:
        if pd.isna(num):
            return ""
        num = str(num).translate(self.bangla_to_english)
        return re.sub(r"[^\d]", "", num)

    def validate_and_format(self, num: str):
        if not num:
            return False, ""
        if num.startswith("88") and len(num) == 13 and num[2:4] == "01":
            return True, num
        if num.startswith("01") and len(num) == 11:
            return True, "88" + num
        return False, num

    def process_contacts(self, text: str):
        if pd.isna(text):
            return [], []
        # split by comma or slash
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

        column_choice = st.selectbox("📞 Select Column Containing Mobile Numbers", options=df_original.columns)

        if st.button("🔄 Process File"):
            cleaner = MobileCleaner()
            total_rows = len(df_original)
            batch_size = 100
            translated_rows = []

            progress_bar = st.progress(0)
            status_text = st.empty()

            valid_list, invalid_list = [], []

            for start in range(0, total_rows, batch_size):
                end = min(start + batch_size, total_rows)
                batch = df_original.iloc[start:end].copy()

                for _, row in batch.iterrows():
                    valid, invalid = cleaner.process_contacts(row[column_choice])
                    # store for final extra sheet
                    if valid:
                        valid_list.append(", ".join(valid))
                    else:
                        valid_list.append("")
                    if invalid:
                        invalid_list.append(", ".join(invalid))
                    else:
                        invalid_list.append("")

                progress_bar.progress(end / total_rows)
                status_text.text(f"Processing rows {start+1} to {end} of {total_rows}")

            # Final sheet with valid & invalid contacts
            final_sheet = pd.DataFrame({
                "Valid_Contacts": valid_list,
                "Invalid_Contacts": invalid_list
            })

            # Save output
            folder = os.getcwd()
            name, ext = os.path.splitext(uploaded_file.name)
            output_path = os.path.join(folder, f"{name}_processed{ext}")

            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                df_original.to_excel(writer, sheet_name="Input_Data", index=False)
                final_sheet.to_excel(writer, sheet_name="Processed_Contacts", index=False)

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
