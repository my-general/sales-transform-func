import logging
import pandas as pd
from io import StringIO
import azure.functions as func

def main(inputBlob: func.InputStream, outputBlob: func.Out[func.InputStream]):
    logging.info(f"Processing blob: {inputBlob.name}, Size: {inputBlob.length} bytes")

    try:
        # Read CSV from blob
        csv_data = inputBlob.read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_data))

        # Validate expected columns
        required_columns = {'TotalRevenue', 'OrderQuantity', 'UnitPrice'}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"Missing required columns. Found: {df.columns.tolist()}")

        # Apply transformation
        df = df[df['TotalRevenue'] > 0]
        df['Profit'] = df['TotalRevenue'] - (df['OrderQuantity'] * df['UnitPrice'])

        # Output CSV
        output_csv = df.to_csv(index=False)
        outputBlob.set(output_csv.encode('utf-8'))

        logging.info("✅ Blob transformed and written to processed folder.")

    except Exception as e:
        logging.error(f"❌ Error processing blob: {e}")
