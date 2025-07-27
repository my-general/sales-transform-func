import logging
import pandas as pd
from io import StringIO
import azure.functions as func

def main(inputBlob: func.InputStream, outputBlob: func.Out[func.InputStream]):
    logging.info(f"🚀 Triggered by blob: {inputBlob.name}, Size: {inputBlob.length} bytes")

    try:
        # Read CSV from blob
        csv_data = inputBlob.read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_data))
        logging.info(f"📊 Read CSV with shape: {df.shape}, columns: {df.columns.tolist()}")

        # Validate required columns
        required_columns = {'TotalRevenue', 'OrderQuantity', 'UnitPrice'}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"❌ Missing required columns. Found: {df.columns.tolist()}")

        # Transformation logic
        df = df[df['TotalRevenue'] > 0]
        df['Profit'] = df['TotalRevenue'] - (df['OrderQuantity'] * df['UnitPrice'])

        if df.empty:
            logging.warning("⚠️ No rows remain after filtering. Skipping blob write.")
            return

        # Output to CSV
        output_csv = df.to_csv(index=False)
        outputBlob.set(output_csv.encode('utf-8'))

        logging.info(f"✅ Transformation complete. Wrote output blob to: processed/{inputBlob.name.split('/')[-1]}")

    except Exception as e:
        logging.error(f"❌ Exception in blob processing: {str(e)}", exc_info=True)
