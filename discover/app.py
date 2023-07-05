import streamlit as st
import pandas as pd
import openai

from helpers import upload_csv_to_s3, list_csv_files_in_s3, read_csv_from_s3


def main():
    # Set Page Layout
    st.set_page_config(layout="wide", page_icon="🧊", page_title="Discover AI")

    # Configure OpenAI model
    openai.api_key = st.secrets["OPENAI_API_KEY"]

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    DEFAULT_BUCKET_NAME = "streamlit-csv-demo"

    # Set App title
    st.title("Discover AI")
    st.text("An AI-powered data discovery tool for CSV files.")

    # Sidebar input
    st.sidebar.subheader("S3 Configuration")
    bucket_name = st.sidebar.text_input("S3 Bucket Name", DEFAULT_BUCKET_NAME)

    # Upload CSV file
    st.sidebar.subheader("Upload CSV")
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file")

    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_content = uploaded_file.read()
        upload_csv_to_s3(bucket_name, file_name, file_content)

    # List CSV files in the bucket
    csv_files = list_csv_files_in_s3(bucket_name)

    # Display list of CSV files
    selected_csv = st.sidebar.selectbox("Select CSV File", csv_files)

    # Display CSV data as DataFrame
    if selected_csv:
        df = read_csv_from_s3(bucket_name, selected_csv)
        if df is not None:
            # Display metrics
            st.subheader("Item Counts")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(label="Number of Records", value=len(df))
            with col2:
                st.metric(label="Number of Columns", value=df.shape[1])
            with col3:
                st.metric(label="Number of Rows", value=df.shape[0])

            # Display DataFrame
            st.subheader("Records")
            with st.expander("See data"):
                st.dataframe(df)

    # Chat with GPT-3
    st.subheader("Chat with GPT-3")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # React to user input
    if prompt := st.chat_input("Ask me anything about your data"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)

        # Augment prompt so that it contains the CSV information
        augmented_prompt = f"{prompt}. The CSV information is the following {df.to_csv(index=False)}. Be concise."

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": augmented_prompt})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            for response in openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )


if __name__ == "__main__":
    main()
