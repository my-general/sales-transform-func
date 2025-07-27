import logging
import pandas as pd
from io import StringIO
import azure.functions as func

def main(inputBlob: func.InputStream, outputBlob: func.Out[bytes]):
    logging.info(f"📥 Processing blob: {inputBlob.name}, Size: {inputBlob.length} bytes")

    try:
        # Step 1: Read CSV from blob
        csv_data = inputBlob.read().decode('utf-8')
        logging.info("📄 Raw CSV content loaded.")
        logging.debug(f"🔍 First 200 characters of CSV:\n{csv_data[:200]}")

        # Step 2: Parse CSV into DataFrame
        df = pd.read_csv(StringIO(csv_data))
        logging.info(f"🧮 DataFrame loaded with {len(df)} rows and columns: {list(df.columns)}")

        # Step 3: Validate required columns
        required_columns = {'TotalRevenue', 'OrderQuantity', 'UnitPrice'}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"❌ Missing required columns. Found: {df.columns.tolist()}")

        # Step 4: Data transformation
        df = df[df['TotalRevenue'] > 0]
        df['Profit'] = df['TotalRevenue'] - (df['OrderQuantity'] * df['UnitPrice'])
        logging.info(f"📊 Transformed DataFrame now has {len(df)} rows.")

        # Step 5: Write to output blob as CSV
        output_csv = df.to_csv(index=False)
        outputBlob.set(output_csv.encode('utf-8'))

        logging.info("✅ Transformation complete. Data written to processed output blob.")

    except Exception as e:
        logging.error("❌ Exception during blob processing:", exc_info=True)
