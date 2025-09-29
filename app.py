import streamlit as st
from services.file_handler import FileHandler

st.set_page_config(page_title="📊 Mobile Cleaner", page_icon="📱", layout="centered")
st.title("📊 Excel Mobile Cleaner with 88 Prefix")

uploaded_files = st.file_uploader("📂 Upload Excel Files (.xlsx)", type=["xlsx"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.subheader(f"File: {uploaded_file.name}")
        try:
            # Preview
            file_handler = FileHandler(uploaded_file, column_name=None)
            df_original = file_handler.file.read()
        except Exception as e:
            st.error(f"❌ Error loading file: {e}")
            continue

        # Reset pointer after read
        uploaded_file.seek(0)
        df_preview = None
        try:
            import pandas as pd
            df_preview = pd.read_excel(uploaded_file, dtype=str)
            st.write(df_preview.head())
        except Exception as e:
            st.error(f"Error previewing file: {e}")
            continue

        # Column selection
        column_choice = st.selectbox(f"📞 Select mobile column for {uploaded_file.name}", df_preview.columns)

        if st.button(f"🔄 Process {uploaded_file.name}"):
            handler = FileHandler(uploaded_file, column_choice)
            output_path, df_original, df_translated, df_valid, df_invalid = handler.process_file()

            st.success(f"✅ Processing complete! Saved at {output_path}")

            st.subheader("Translated Data (Sample)")
            st.dataframe(df_translated.head())

            with open(output_path, "rb") as f:
                st.download_button(
                    label=f"📥 Download {uploaded_file.name} Processed",
                    data=f,
                    file_name=f"{uploaded_file.name.replace('.xlsx', '_processed.xlsx')}",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
