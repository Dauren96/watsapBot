import gspread
import logging
from datetime import datetime
import os

# Configure logger for this module
logger = logging.getLogger(__name__)
# Ensure basicConfig is called somewhere in your application's entry point,
# for example, in main.py, if you want to see logs from this module during standalone testing.
# logging.basicConfig(level=logging.INFO) # Example: Call this in main.py or if running this file directly

# Configuration
# SHEET_NAME: Name of the Google Sheet to use for orders.
# Default is "Бот_Заказы_Вышивка". Can be overridden by GOOGLE_SHEET_NAME environment variable.
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Бот_Заказы_Вышивка")

# GOOGLE_APPLICATION_CREDENTIALS environment variable should be set to the path of the
# service account JSON key file. gspread library automatically uses this variable.

def get_sheet_client():
    """
    Authenticates with Google Sheets API using service account credentials
    and returns a gspread.Worksheet object (the first sheet of the opened Spreadsheet).
    """
    try:
        # Attempt to authorize using gspread's default mechanism,
        # which typically relies on GOOGLE_APPLICATION_CREDENTIALS env var.
        gc = gspread.service_account()

        # Open the spreadsheet by its name.
        spreadsheet = gc.open(SHEET_NAME)
        logger.info(f"Successfully connected to Google Spreadsheet: '{SHEET_NAME}'")

        # Return the first worksheet.
        return spreadsheet.sheet1
    except gspread.exceptions.SpreadsheetNotFound:
        logger.error(f"Google Spreadsheet '{SHEET_NAME}' not found. "
                     "Please ensure the sheet exists and its name matches.")
        logger.error("Also, ensure the service account has been granted access to this sheet.")
    except Exception as e:
        logger.error(f"Failed to authenticate or connect to Google Spreadsheet '{SHEET_NAME}'. Error: {e}")
        logger.error("Ensure 'GOOGLE_APPLICATION_CREDENTIALS' environment variable is set correctly "
                     "to the path of your service account JSON key file, and that the service account "
                     "has necessary permissions (e.g., Editor) on the Google Sheet.")
    return None

def add_order_to_sheet(order_data: dict):
    """
    Adds a new order to the Google Sheet.

    Args:
        order_data (dict): A dictionary containing the order details.
                           Expected keys: 'client_id', 'item_name', 'price'.
                           Optional key: 'details'.
                           Timestamp and Status will be added automatically.

    Returns:
        bool: True if the order was added successfully, False otherwise.
    """
    worksheet = get_sheet_client()
    if not worksheet:
        logger.error("Cannot add order: Failed to get Google Sheet client/worksheet.")
        return False

    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "Новый"  # Default status for a new order

        # Columns: Timestamp, WhatsApp_ClientID, SelectedItem, ItemDetails, Price, Status
        row_to_add = [
            timestamp,
            order_data.get('client_id', 'N/A'),
            order_data.get('item_name', 'N/A'),
            order_data.get('details', ''),  # Default to empty string if no details
            order_data.get('price', 0.0),   # Default to 0.0 if no price
            status
        ]

        worksheet.append_row(row_to_add)
        logger.info(f"Order for client '{order_data.get('client_id')}' concerning item '{order_data.get('item_name')}' "
                    f"successfully added to Google Sheet '{SHEET_NAME}'.")
        return True
    except gspread.exceptions.APIError as e:
        logger.error(f"Google Sheets API error while adding order. Error: {e}. Data: {order_data}")
        logger.error(f"Response from API: {e.response.json() if e.response else 'No response details'}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while adding order to Google Sheet. Error: {e}. Data: {order_data}")

    return False

if __name__ == '__main__':
    # This block is for example usage and testing when running sheets_client.py directly.
    # For this to work:
    # 1. GOOGLE_APPLICATION_CREDENTIALS environment variable must be set to the path of your service account JSON.
    # 2. The service account must have "Editor" access to the Google Sheet named in SHEET_NAME.
    # 3. The required libraries (gspread, google-auth) must be installed.

    # Setup basic logging for the test
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("--- Testing Google Sheets Client Standalone ---")

    # Check if GOOGLE_APPLICATION_CREDENTIALS is set
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        logger.warning("Environment variable 'GOOGLE_APPLICATION_CREDENTIALS' is not set.")
        logger.warning("Skipping live test of add_order_to_sheet.")
    else:
        logger.info(f"Attempting to connect to sheet: {SHEET_NAME} using credentials from GOOGLE_APPLICATION_CREDENTIALS.")

        # Test getting the sheet client
        test_worksheet = get_sheet_client()
        if test_worksheet:
            logger.info(f"Successfully connected to worksheet '{test_worksheet.title}'.")

            # Test adding an order
            test_order_1 = {
                'client_id': 'whatsapp_test_user_001',
                'item_name': 'Test Item Alpha',
                'details': 'Size L, Color Red',
                'price': 19.99
            }
            logger.info(f"Attempting to add test order 1: {test_order_1}")
            if add_order_to_sheet(test_order_1):
                logger.info("Test order 1 added successfully.")
            else:
                logger.error("Failed to add test order 1.")

            test_order_2 = {
                'client_id': 'whatsapp_test_user_002',
                'item_name': 'Test Item Beta (No Details)',
                # 'details': '', # Intentionally missing
                'price': 25.50
            }
            logger.info(f"Attempting to add test order 2: {test_order_2}")
            if add_order_to_sheet(test_order_2):
                logger.info("Test order 2 added successfully.")
            else:
                logger.error("Failed to add test order 2.")
        else:
            logger.error("Failed to get worksheet client during standalone test. Check credentials and sheet sharing.")

    logger.info("--- Finished Standalone Test ---")
    # Note: The `if __name__ == '__main__':` block is primarily for direct script execution.
    # In the context of the larger Flask application, these functions will be imported and used.
    # The actual Google API calls will only succeed if the environment (credentials, permissions) is correctly configured.
```
