# WhatsApp Bot Deployment Guide for Google Cloud Functions

This guide provides step-by-step instructions to deploy the Python Flask-based WhatsApp bot to Google Cloud Functions (GCF) and configure the WhatsApp webhook.

## A. Prerequisites

Before you begin, ensure you have the following:

1.  **Google Cloud Project:**
    *   A Google Cloud Platform (GCP) project set up. If you don't have one, create one at [console.cloud.google.com](https://console.cloud.google.com/).
    *   Billing enabled for your project.
2.  **`gcloud` Command-Line Tool:**
    *   The Google Cloud SDK (which includes `gcloud`) installed and initialized. Instructions can be found [here](https://cloud.google.com/sdk/docs/install).
    *   Authenticate `gcloud` with your GCP account: `gcloud auth login`
    *   Set your default project: `gcloud config set project YOUR_PROJECT_ID`
3.  **Google APIs Enabled:**
    *   Ensure the following APIs are enabled for your project (you can enable them from the GCP console under "APIs & Services" > "Library"):
        *   Cloud Functions API
        *   Google Sheets API
        *   Cloud Build API (usually enabled by default, required for deploying functions)
        *   IAM API (Identity and Access Management)
4.  **Service Account for the Function:**
    *   It's recommended to create a dedicated service account for your Cloud Function to run with the principle of least privilege.
        *   In GCP Console, navigate to "IAM & Admin" > "Service Accounts".
        *   Click "Create Service Account". Name it (e.g., `whatsapp-bot-gcf-sa`).
        *   **Grant this service account the following roles:**
            *   **Google Sheets API User** (or a custom role with `spreadsheets.read` and `spreadsheets.write` permissions if you want to be more granular. For simplicity, you might initially grant "Editor" role on *just the specific Google Sheet* you are using, directly via the Sheet's sharing settings).
            *   **Cloud Functions Invoker** (if you plan to restrict access to your function later; not strictly needed if using `--allow-unauthenticated`).
            *   **Logs Writer** (for writing logs to Cloud Logging, usually granted by default).
        *   Note down the email address of this service account (e.g., `whatsapp-bot-gcf-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com`). You'll use this when deploying.
5.  **WhatsApp Business API Access:**
    *   A configured WhatsApp Business Account (WABA).
    *   A registered phone number associated with your WABA.
    *   Access to the Meta for Developers portal (or Facebook App Dashboard) to configure webhooks.
    *   Obtain your **WhatsApp Business API Access Token** and **WhatsApp Phone Number ID**.

## B. Application Files

Ensure the following files are in your project directory:

1.  `main.py`: The main Flask application with webhook logic.
2.  `menu_data.py`: Defines the menu structure for the bot.
3.  `sheets_client.py`: Handles communication with Google Sheets.
4.  `requirements.txt`: Lists Python package dependencies.

```
your-project-directory/
├── main.py
├── menu_data.py
├── sheets_client.py
└── requirements.txt
```

**Important Note on Credentials (`gcp_credentials.json`):**
You do **not** need to package a `gcp_credentials.json` file with your deployment if you use the function's runtime service account as recommended above. The `gspread` library will automatically use the permissions of the service account under which the Cloud Function executes.

## C. Deploying to Google Cloud Functions

1.  **Open your terminal or Google Cloud Shell.**
2.  **Navigate to your project directory** (where `main.py` and other files are located).
3.  **Run the deployment command:**

    ```bash
    gcloud functions deploy YOUR_FUNCTION_NAME \
        --runtime python310 \
        --trigger-http \
        --entry-point app \
        --region YOUR_REGION \
        --service-account YOUR_FUNCTION_SERVICE_ACCOUNT_EMAIL \
        --allow-unauthenticated \
        --set-env-vars \
    GOOGLE_SHEET_NAME="Бот_Заказы_Вышивка",\
    VERIFY_TOKEN="YOUR_SECRET_VERIFY_TOKEN",\
    WHATSAPP_PHONE_NUMBER_ID="YOUR_WHATSAPP_PHONE_NUMBER_ID",\
    WHATSAPP_ACCESS_TOKEN="YOUR_WHATSAPP_ACCESS_TOKEN"
    ```

4.  **Explanation of Placeholders:**
    *   `YOUR_FUNCTION_NAME`: Choose a name for your function (e.g., `whatsapp-bot-webhook`).
    *   `python310`: Specify the Python runtime. You can choose other supported Python versions like `python39`, `python311`, etc.
    *   `app`: This is the name of the Flask application instance in `main.py` (`app = Flask(__name__)`).
    *   `YOUR_REGION`: The GCP region where you want to deploy your function (e.g., `us-central1`, `europe-west1`).
    *   `YOUR_FUNCTION_SERVICE_ACCOUNT_EMAIL`: The email of the service account you created in the prerequisites (e.g., `whatsapp-bot-gcf-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com`).
    *   `--allow-unauthenticated`: This makes your function's HTTPS endpoint publicly accessible, which is required for WhatsApp webhooks. For restricted access, you would omit this and configure IAM and authentication, which is more complex.
    *   **Environment Variables (`--set-env-vars`):**
        *   `GOOGLE_SHEET_NAME`: The name of your Google Sheet (e.g., "Бот_Заказы_Вышивка"). This can be omitted if you are using the default name hardcoded in `sheets_client.py`, but setting it as an env var is more flexible.
        *   `VERIFY_TOKEN`: **Crucial.** This is the secret token you will also set in the Meta for Developers portal to verify webhook requests. Choose a strong, unique string.
        *   `WHATSAPP_PHONE_NUMBER_ID`: Your WhatsApp Business phone number ID from the Meta portal.
        *   `WHATSAPP_ACCESS_TOKEN`: Your WhatsApp Business API access token from the Meta portal.

5.  **After deployment, `gcloud` will output information, including the HTTPS Trigger URL.** Copy this URL. It will look something like: `https://YOUR_REGION-YOUR_PROJECT_ID.cloudfunctions.net/YOUR_FUNCTION_NAME`.

## D. Configuring WhatsApp Webhook

1.  **Go to your Facebook App Dashboard / Meta for Developers portal.**
2.  Navigate to your app, then find "WhatsApp" in the products list and click on **Configuration**.
3.  **Webhook Configuration:**
    *   Click "Edit" for the Callback URL.
    *   **Callback URL:** Paste the HTTPS Trigger URL you obtained from the GCF deployment.
    *   **Verify token:** Enter the *exact same* `VERIFY_TOKEN` string you set in the environment variables during GCF deployment.
    *   Click "Verify and Save". Meta will send a `GET` request to your GCF endpoint. Your function's `GET` handler should process this verification.
4.  **Subscribe to Message Events:**
    *   After verification, under "Webhook fields" (or a similar section), click "Manage".
    *   Subscribe to the `messages` field. This tells Meta to send notifications to your webhook whenever your WhatsApp number receives a message.

## E. Testing

1.  **Send a Message:** Send a message from any WhatsApp account to your bot's registered WhatsApp phone number.
    *   Try sending "меню" or "start" to initialize the interaction.
    *   Navigate through the menus by selecting options.
    *   Select an item to purchase.
2.  **Check Google Cloud Function Logs:**
    *   In the GCP Console, navigate to "Cloud Functions".
    *   Click on your function's name.
    *   Go to the "Logs" tab. You should see logs from your Python application, including received messages, processing steps, and simulated message sending.
    *   Look for any errors or warnings.
3.  **Verify Data in Google Sheets:**
    *   Open the Google Sheet you configured (`Бот_Заказы_Вышивка`).
    *   When you select an item in the bot, a new row with the order details (Timestamp, Client ID, Item Name, Details, Price, Status="Новый") should appear in the sheet.

## Troubleshooting Tips

*   **5xx Errors from Webhook:** Check GCF logs for application errors.
*   **Verification Fails:**
    *   Ensure `VERIFY_TOKEN` in GCF environment variables exactly matches the one in Meta settings.
    *   Check GCF logs for any errors during the `GET` request.
*   **No Messages Received by Bot:**
    *   Confirm webhook subscription to `messages` is active.
    *   Ensure the GCF endpoint is publicly accessible (`--allow-unauthenticated` or proper IAM).
*   **Sheets Not Updating:**
    *   Verify the `GOOGLE_SHEET_NAME` environment variable is correct.
    *   Ensure the GCF service account (`YOUR_FUNCTION_SERVICE_ACCOUNT_EMAIL`) has "Editor" permissions on the Google Sheet (share the sheet with this email).
    *   Check GCF logs for errors from `sheets_client.py`.
*   **Environment Variables:** Double-check all environment variables are correctly set in the GCF deployment configuration. You can view them in the GCF console under your function's "Variables" tab.

This completes the deployment and configuration process. Your WhatsApp bot should now be running on Google Cloud Functions!
```
