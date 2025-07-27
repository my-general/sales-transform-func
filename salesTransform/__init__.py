import logging
import pandas as pd
from io import StringIO
import azure.functions as func

def main(inputBlob: func.InputStream, outputBlob: func.Out[str]):
    logging.info(f"🟡 Triggered by blob: {inputBlob.name}, Size: {inputBlob.length} bytes")

    try:
        # Step 1: Read the blob
        blob_bytes = inputBlob.read()
        logging.info("✅ Blob read successfully.")

        try:
            csv_data = blob_bytes.decode('utf-8')
            logging.info("✅ Blob decoded to UTF-8 string.")
        except UnicodeDecodeError as decode_err:
            logging.error(f"❌ UTF-8 decode failed: {decode_err}")
            return

        # Step 2: Load into DataFrame
        try:
            df = pd.read_csv(StringIO(csv_data))
            logging.info(f"✅ CSV parsed into DataFrame with columns: {df.columns.tolist()}")
        except Exception as e:
            logging.error(f"❌ Failed to parse CSV: {e}")
            return

        # Step 3: Validate required columns
        required_columns = {'TotalRevenue', 'OrderQuantity', 'UnitPrice'}
        if not required_columns.issubset(df.columns):
            logging.error(f"❌ Missing required columns. Found: {df.columns.tolist()}")
            return
        logging.info("✅ Required columns are present.")

        # Step 4: Apply transformation
        df = df[df['TotalRevenue'] > 0]
        df['Profit'] = df['TotalRevenue'] - (df['OrderQuantity'] * df['UnitPrice'])
        logging.info("✅ Transformation applied successfully.")

        # Step 5: Write to output
        output_csv = df.to_csv(index=False)
        outputBlob.set(output_csv)
        logging.info("✅ Output blob written successfully.")

    except Exception as e:
        logging.error(f"❌ Unhandled exception in function: {e}")
