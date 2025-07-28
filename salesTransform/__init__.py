import logging
import pandas as pd
from io import StringIO
import azure.functions as func

# Get a logger for the function
# Using __name__ ensures the log messages are associated with this function
logger = logging.getLogger(__name__)

# The main function entry point for the Azure Function
# inputBlob: func.InputStream for reading the incoming blob
# outputBlob: func.Out[bytes] for writing the transformed data as bytes to an output blob
def main(inputBlob: func.InputStream, outputBlob: func.Out[bytes]):
    # Log information about the incoming blob
    logger.info(f"📥 Processing blob: {inputBlob.name}, Size: {inputBlob.length} bytes")

    try:
        # Step 1: Read CSV data from the input blob
        # The blob data is typically bytes, so decode it to a UTF-8 string
        csv_data = inputBlob.read().decode('utf-8')
        logger.info("📄 Raw CSV content loaded.")
        # Log the first 200 characters for debugging purposes (useful for large files)
        logger.debug(f"🔍 First 200 characters of CSV:\n{csv_data[:200]}")

        # Step 2: Parse the CSV string into a Pandas DataFrame
        # StringIO is used to treat the string as a file-like object for pandas.read_csv
        df = pd.read_csv(StringIO(csv_data))
        logger.info(f"🧮 DataFrame loaded with {len(df)} rows and columns: {list(df.columns)}")

        # Step 3: Validate the presence of required columns
        # Define a set of column names that must be present in the DataFrame
        required_columns = {'TotalRevenue', 'OrderQuantity', 'UnitPrice'}
        # Check if all required columns are a subset of the DataFrame's columns
        if not required_columns.issubset(df.columns):
            # If any required column is missing, raise a ValueError
            raise ValueError(f"❌ Missing required columns. Found: {df.columns.tolist()}. Required: {list(required_columns)}")

        # Step 4: Perform data transformation
        # Filter rows where 'TotalRevenue' is greater than 0
        df = df[df['TotalRevenue'] > 0]
        # Calculate a new 'Profit' column
        df['Profit'] = df['TotalRevenue'] - (df['OrderQuantity'] * df['UnitPrice'])
        logger.info(f"📊 Transformed DataFrame now has {len(df)} rows.")

        # Step 5: Convert the transformed DataFrame back to CSV format
        # index=False prevents pandas from writing the DataFrame index as a column
        output_csv = df.to_csv(index=False)
        # Set the output blob content, encoding the string back to bytes
        outputBlob.set(output_csv.encode('utf-8'))

        logger.info("✅ Transformation complete. Data written to processed output blob.")

    except Exception as e:
        # Catch any exceptions that occur during processing and log them
        # exc_info=True will include the full stack trace in the log, which is vital for debugging
        logger.error("❌ Exception during blob processing:", exc_info=True)
        # Re-raise the exception to indicate failure to the Azure Functions host
        # This will mark the function execution as 'Failed'
        raise # Important to re-raise if you want the trigger to retry based on host.json settings
