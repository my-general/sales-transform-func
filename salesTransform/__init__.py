import logging
import pandas as pd
from io import StringIO
import azure.functions as func

def main(inputBlob: func.InputStream, outputBlob: func.Out[func.InputStream]):
    logging.info(f"Processing blob: {inputBlob.name}, Size: {inputBlob.length} bytes")

    # Read CSV from blob
    csv_data = inputBlob.read().decode('utf-8')
    df = pd.read_csv(StringIO(csv_data))

    # Sample transformation: filter & calculate profit
    df = df[df['TotalRevenue'] > 0]
    df['Profit'] = df['TotalRevenue'] - (df['OrderQuantity'] * df['UnitPrice'])

    # Output transformed CSV
    output_csv = df.to_csv(index=False)
    outputBlob.set(output_csv.encode('utf-8'))

    logging.info("Transformation completed and blob written to processed-sales/")

