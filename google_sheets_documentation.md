# Google Sheets Integration Documentation

This document outlines the structure of the Google Sheet used for order management and explains how to use Google Cloud Platform (GCP) service account credentials for programmatic access via Python.

## 1. Google Sheet Structure

The Google Sheet will be used to store and manage customer orders.

*   **Sheet Name:** `Бот_Заказы_Вышивка` (Bot_Orders_Embroidery)
*   **First Sheet (Sheet1) Columns:**

    | Column | Header (Russian)      | Header (English)   | Description                                                                 | Example Data                     |
    |--------|-----------------------|--------------------|-----------------------------------------------------------------------------|----------------------------------|
    | A      | Время заказа          | `Timestamp`        | The date and time when the order was placed.                                | `2023-10-27 14:35:00`            |
    | B      | ID клиента WhatsApp   | `WhatsApp_ClientID`| Unique identifier for the client from WhatsApp.                             | `whatsapp:+14155238886`          |
    | C      | Выбранный товар/категория | `SelectedItem`     | The main item or category selected by the client.                           | `Футболка` (T-shirt)             |
    | D      | Детали товара/выбранные опции | `ItemDetails`      | Specific options chosen for the item, like size, color, custom text, etc. | `Размер: L, Цвет: Белый, Текст: "Happy"` (Size: L, Color: White, Text: "Happy") |
    | E      | Цена                  | `Price`            | The price of the selected item and options.                                 | `1500`                           |
    | F      | Статус заказа         | `Status`           | Current status of the order.                                                | `Новый` (New), `Обработан` (Processed), `Отправлен` (Shipped), `Отменен` (Cancelled) |

## 2. Service Account Credential Usage for Python

To allow the Python application to programmatically access and modify the Google Sheet, a GCP Service Account is used.

### 2.1. Prerequisites:

*   **GCP Project:** A Google Cloud Platform project must exist.
*   **Google Sheets API Enabled:** The Google Sheets API and Google Drive API must be enabled for the project.
*   **Service Account Created:** A service account must be created within the GCP project.
*   **Service Account Key:** A JSON key file for this service account must be generated and downloaded. This file is typically named something like `gcp_credentials.json`.
*   **Share Google Sheet:** The Google Sheet (`Бот_Заказы_Вышивка`) must be shared with the service account's email address (found in the service account details or the JSON key file, usually looks like `your-service-account-name@your-project-id.iam.gserviceaccount.com`), granting it "Editor" permissions.

### 2.2. Python Application Setup:

1.  **Place Key File:** The downloaded JSON key file (e.g., `gcp_credentials.json`) must be securely stored and accessible in the bot's deployment environment.

2.  **Install Libraries:** The Python application will require libraries to interact with Google Sheets and authenticate. The primary libraries are:
    *   `gspread`: For interacting with Google Sheets.
    *   `google-auth`: For handling authentication with Google Cloud services.
    *   `google-auth-oauthlib`: For OAuth 2.0 flow, often used with `gspread`.

    These can be installed via pip:
    ```bash
    pip install gspread google-auth google-auth-oauthlib
    ```

3.  **Authentication in Python:**

    There are two main ways to provide the credentials to the application:

    *   **Environment Variable (Recommended):**
        Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the absolute path of the JSON key file.
        ```bash
        export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/gcp_credentials.json"
        ```
        Many Google client libraries (including `gspread` when used with `google-auth`) will automatically detect and use this environment variable.

        ```python
        import gspread
        import google.auth

        # Authenticate using Application Default Credentials (ADC)
        # This automatically picks up the GOOGLE_APPLICATION_CREDENTIALS environment variable
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file' # Required by gspread
        ]
        creds, _ = google.auth.default(scopes=scopes)
        gc = gspread.authorize(creds)

        # Now you can open the sheet
        # spreadsheet = gc.open("Бот_Заказы_Вышивка")
        # worksheet = spreadsheet.sheet1
        # ... perform operations ...
        ```

    *   **Directly in Code (Less Secure for Production):**
        The path to the JSON file can be explicitly provided in the Python code when initializing the client. This is generally less secure for production environments as it hardcodes the path.

        ```python
        import gspread

        # Authenticate by directly passing the JSON key file path
        gc = gspread.service_account(filename="/path/to/your/gcp_credentials.json")

        # Now you can open the sheet
        # spreadsheet = gc.open("Бот_Заказы_Вышивка")
        # worksheet = spreadsheet.sheet1
        # ... perform operations ...
        ```

### 2.3. Security Note:

*   **Never commit the JSON key file directly into your version control system (e.g., Git).**
*   Use environment variables or secure secret management solutions to handle credentials in production.
*   Grant the service account only the necessary permissions (e.g., editor access to the specific sheet, not owner of the entire Drive).

This setup enables the Python bot to securely authenticate with Google Cloud and manage order data in the specified Google Sheet.
