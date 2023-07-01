import streamlit as st
import boto3
import pandas as pd


def read_csv_from_s3(bucket_name, file_name):
    s3 = boto3.client("s3")
    try:
        obj = s3.get_object(Bucket=bucket_name, Key=file_name)
        df = pd.read_csv(obj["Body"])
        return df
    except Exception as e:
        st.error(f"Error reading CSV file: {str(e)}")
        return None


def list_csv_files_in_s3(bucket_name):
    s3 = boto3.client("s3")
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        if "Contents" in response:
            csv_files = [
                obj["Key"]
                for obj in response["Contents"]
                if obj["Key"].lower().endswith(".csv")
            ]
            return csv_files
        else:
            st.warning("No CSV files found in the bucket.")
            return []
    except Exception as e:
        st.error(f"Error listing CSV files: {str(e)}")
        return []


def upload_csv_to_s3(bucket_name, file_name, file_content):
    s3 = boto3.client("s3")
    try:
        s3.put_object(Body=file_content, Bucket=bucket_name, Key=file_name)
        st.success("CSV file uploaded successfully!")
    except Exception as e:
        st.error(f"Error uploading CSV file: {str(e)}")
