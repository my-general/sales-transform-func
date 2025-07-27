import logging
import pandas as pd
from io import StringIO
import azure.functions as func

def main(inputBlob: func.InputStream, outputBlob: func.Out[str]):
    logging.info(f"🔥 Triggered by blob: {inputBlob.name}, Size: {inputBlob.length} bytes")

    try:
        # Read and decode blob content
        raw_bytes = inputBlob.read()
        logging.info(f"✅ Read {len(raw_bytes)} bytes from blob")

        try:
            csv_data = raw_bytes.decode('utf-8')
        except UnicodeDecodeError as ude:
            logging.error(f"❌ UTF-8 decoding failed: {ude}")
            raise

        # Convert to DataFrame
        try:
            df = pd.read_csv(StringIO(csv_data))
        except Exception as pe:
            logging.error(f"❌ Error parsing CSV with pandas: {pe}")
            raise

        logging.info(f"📊 Loaded DataFrame with shape: {df.shape}")

        # Validate required columns
        required_columns = {'TotalRevenue', 'OrderQuantity', 'UnitPrice'}
        missing = required_columns - set(df.columns)
        if missing:
            raise ValueError(f"❌ Missing required columns: {missing}. Found columns: {df.columns.tolist()}")

        # Transform data
        df = df[df['TotalRevenue'] > 0]
        df['Profit'] = df['TotalRevenue'] - (df['OrderQuantity'] * df['UnitPrice'])
        logging.info(f"✅ Transformation complete. Final shape: {df.shape}")

        # Output transformed CSV
        output_csv = df.to_csv(index=False)
        outputBlob.set(output_csv)

        logging.info("📁 Transformed data written to output blob.")

    except Exception as e:
        logging.error(f"❌ salesTransform function failed: {e}")
        raise
