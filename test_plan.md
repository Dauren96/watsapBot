# WhatsApp Bot Test Plan

## I. Introduction

This document provides a test plan for validating the functionality of the deployed WhatsApp Bot. The purpose of these tests is to ensure that the bot operates as expected, including menu navigation, item selection, data recording in Google Sheets, and error handling.

## II. Prerequisites for Testing

Before starting the test cases, please ensure the following conditions are met:

1.  **Bot Deployed to GCF:** The Python Flask application (`main.py` and associated files) has been successfully deployed to Google Cloud Functions.
2.  **Webhook Configured:** The GCF Trigger URL is correctly set as the Callback URL in your WhatsApp Business API settings (via Meta for Developers portal).
3.  **Verify Token Match:** The `VERIFY_TOKEN` environment variable in GCF exactly matches the Verify Token set in the WhatsApp Business API configuration.
4.  **Webhook Subscription:** The webhook in the Meta for Developers portal is subscribed to the `messages` field.
5.  **Google Sheet Ready:**
    *   The Google Sheet (default name: "Бот_Заказы_Вышивка", or as configured by the `GOOGLE_SHEET_NAME` environment variable) has been created in your Google Drive.
    *   The first sheet within this spreadsheet is intended for order data.
6.  **Sheet Permissions:** The service account associated with your Google Cloud Function (specified during deployment) has "Editor" permissions (or at least permissions to read and append rows) on the Google Sheet. You can grant this by sharing the Google Sheet with the GCF's service account email address.
7.  **Testing WhatsApp Account:** You have a WhatsApp account (on a phone) that can send messages to the bot's registered WhatsApp number.

## III. Test Cases

### TC1: Webhook Verification & Initial Contact

*   **Description:** Tests the initial handshake between WhatsApp and GCF, and the display of the main menu upon a greeting or menu command.
*   **Steps:**
    1.  In the Meta for Developers portal (WhatsApp > Configuration), check that your webhook is shown with a green checkmark, indicating it's verified and subscribed to `messages`.
    2.  From your testing WhatsApp account, send the message "меню" to the bot's WhatsApp number. (Alternatively, try "/start" or "Привет").
*   **Expected Results:**
    1.  The bot replies with an interactive message displaying the main menu (e.g., "Добро пожаловать! Выберите категорию:" followed by options like "Наборы для вышивки", "Нитки для вышивки", "Связаться с менеджером").
    2.  In Google Cloud Functions logs for your function, you should see entries indicating:
        *   An incoming POST request for `/webhook`.
        *   Log messages showing the received text (e.g., "меню").
        *   Log messages indicating the main menu is being sent (e.g., "SIMULATING SENDING to [your_whatsapp_id] ... Payload: { ... main_menu ... }").

### TC2: Menu Navigation (Categories & Back)

*   **Description:** Tests navigating into a category submenu and then returning to the main menu.
*   **Steps:**
    1.  After completing TC1 (main menu is displayed), select the "Наборы для вышивки" option from the interactive message.
    2.  From the "Наборы для вышивки" menu that appears, select the "⬅️ Назад в главное меню" option.
*   **Expected Results:**
    1.  After step 1, the bot replies with an interactive message displaying the items in the "Наборы для вышивки" category (e.g., "Набор 'Весенние цветы'", "Набор 'Зимний пейзаж'", etc.).
    2.  After step 2, the bot replies with the main menu interactive message again.
    3.  GCF logs should reflect these interactions, showing the selected option IDs and the corresponding menu payloads being sent.

### TC3: Item Selection & Google Sheets Logging

*   **Description:** Tests selecting a purchasable item and verifies that the order data is correctly logged in the Google Sheet.
*   **Steps:**
    1.  Navigate to a category menu (e.g., "Наборы для вышивки" as in TC2, step 1).
    2.  Select a specific item from the category menu (e.g., "Набор 'Весенние цветы'").
*   **Expected Results:**
    1.  The bot sends a text confirmation message (e.g., "✅ 'Набор "Весенние цветы"' добавлен(о) в вашу корзину (Цена: 1500 руб)...").
    2.  The bot then re-displays the current category menu ("Наборы для вышивки").
    3.  Open your Google Sheet ("Бот_Заказы_Вышивка"). A new row should be appended with the following details:
        *   **Column A (Timestamp):** The current date and time (e.g., `2023-10-28 15:30:00`).
        *   **Column B (WhatsApp_ClientID):** Your WhatsApp ID (e.g., `whatsapp:+1XXXXXXXXXX`).
        *   **Column C (SelectedItem):** The name of the item selected (e.g., "Набор 'Весенние цветы'").
        *   **Column D (ItemDetails):** The description of the item (e.g., "Яркий и красивый набор.").
        *   **Column E (Price):** The price of the item (e.g., `1500`).
        *   **Column F (Status):** "Новый".
    4.  GCF logs should show:
        *   The selected item ID.
        *   The "Item added to cart" log message.
        *   Log messages from `sheets_client.py` indicating a successful call to `add_order_to_sheet` (e.g., "Order for client '...' concerning item '...' successfully added...").

### TC4: Multiple Item Selections

*   **Description:** Tests selecting multiple items, ensuring each is logged independently.
*   **Steps:**
    1.  Complete TC3 to select and log a first item.
    2.  From the currently displayed category menu, select a different item (e.g., "Набор 'Зимний пейзаж'").
    3.  Navigate back to the main menu, then to a different category (e.g., "Нитки для вышивки").
    4.  Select an item from this new category (e.g., "Набор мулине DMC (24 цвета)").
*   **Expected Results:**
    1.  Each item selection is confirmed by a text message from the bot.
    2.  After each selection, the current category menu is re-displayed.
    3.  Each selected item results in a **new, distinct row** in the Google Sheet, with details corresponding to that specific item. There should be three new rows in total from TC3 and TC4.

### TC5: "Contact Manager" Option

*   **Description:** Tests the functionality of the "Связаться с менеджером" option.
*   **Steps:**
    1.  Navigate to the main menu.
    2.  Select the "📞 Связаться с менеджером" option.
*   **Expected Results:**
    1.  The bot replies with the predefined text message: "Спасибо за ваше обращение! Менеджер скоро свяжется с вами по WhatsApp."
    2.  No new entry is created in the Google Sheet for this action.
    3.  GCF logs show the selection of the 'contact_manager' option and the sending of the corresponding message.

### TC6: Unrecognized Input (Fallback)

*   **Description:** Tests how the bot handles messages that are not part of defined commands or menu option IDs.
*   **Steps:**
    1.  Send a random text message to the bot (e.g., "сколько стоит доставка?" or "абракадабра").
*   **Expected Results:**
    1.  The bot replies with the fallback message (e.g., "Извините, я не понял ваш запрос. Пожалуйста, используйте кнопки меню для навигации или введите 'меню', чтобы начать сначала.").
    2.  GCF logs show the unrecognized input and the fallback message being sent.

### TC7: (Optional) Test with Different WhatsApp Accounts

*   **Description:** Ensures that user state (current menu, cart) is managed separately for different users. This test is optional and requires access to a second WhatsApp account/number.
*   **Steps:**
    1.  Using WhatsApp Account A, navigate to a specific category menu (e.g., "Нитки для вышивки").
    2.  Using WhatsApp Account B, send "меню" to the bot. Then, navigate to a different category menu (e.g., "Наборы для вышивки").
    3.  Using WhatsApp Account A, send another message or select an option from its current menu ("Нитки для вышивки").
    4.  Using WhatsApp Account B, select an item from its current menu ("Наборы для вышивки").
*   **Expected Results:**
    1.  The bot should respond correctly to each account based on their last interaction. Account A should still be in the "Нитки для вышивки" context, while Account B is in "Наборы для вышивки".
    2.  Item selections made by Account B should be logged to Google Sheets under Account B's WhatsApp ID and should not affect Account A's session or cart (which is currently only stored in memory in `user_states` in `main.py`).

## IV. Debugging and Troubleshooting

If you encounter issues during testing, refer to these steps:

1.  **Check GCF Logs:**
    *   This is your primary source for diagnosing application-level issues.
    *   Go to the Google Cloud Console > Cloud Functions > Click on your function's name > "Logs" tab.
    *   Look for error messages (e.g., Python exceptions, tracebacks), warnings, or your custom log messages from `logger.info()`, `logger.error()`, etc.
2.  **Inspect Google Sheet:**
    *   **Data Issues:** If data is missing or incorrect, verify the GCF logs for errors during the `add_order_to_sheet` call.
    *   **Sheet Name:** Ensure the `GOOGLE_SHEET_NAME` environment variable in GCF matches the actual name of your Google Sheet.
    *   **Permissions:** Double-check that the GCF service account email has "Editor" access to the sheet (via the "Share" button in Google Sheets).
3.  **WhatsApp Webhook Logs (Meta for Developers):**
    *   If messages sent to your bot don't seem to trigger any GCF logs, check the webhook delivery attempts in the Meta for Developers portal.
    *   Go to your App > WhatsApp > Webhooks. There should be a section to view recent delivery attempts or logs, which can indicate if Meta is failing to send requests to your GCF URL.
4.  **Verify Environment Variables in GCF:**
    *   In the Google Cloud Console, go to Cloud Functions > [Your Function Name] > "Variables" tab (or "Environment variables" under Edit).
    *   Confirm that `VERIFY_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_ACCESS_TOKEN`, and `GOOGLE_SHEET_NAME` (if used) are correctly set and have the intended values.
5.  **Local Testing with Ngrok (Advanced):**
    *   For more in-depth debugging where GCF logs are insufficient:
        1.  Run your Flask application (`main.py`) locally on your computer.
        2.  Ensure all required environment variables (`VERIFY_TOKEN`, `WHATSAPP_...`, `GOOGLE_APPLICATION_CREDENTIALS` pointing to your JSON key) are set in your local terminal session.
        3.  Use a tool like `ngrok` to expose your local Flask server (e.g., running on `http://localhost:8080`) to the internet with an HTTPS URL (`ngrok http 8080`).
        4.  Temporarily update the Callback URL in the Meta for Developers portal to this `ngrok` HTTPS URL.
        5.  Now, messages sent to your bot will hit your local server, allowing you to use a Python debugger, see live console output, etc.
        6.  **Remember to revert the Callback URL to your GCF URL after local debugging.**

## V. Reporting Issues

If you find bugs or issues during testing, please document them with the following information:

*   **Test Case ID:** (e.g., TC3)
*   **Description of Issue:** A clear and concise explanation of the problem.
*   **Steps to Reproduce:** The exact steps taken that led to the issue.
*   **Expected Result:** What should have happened.
*   **Actual Result:** What actually happened.
*   **Screenshots (if applicable):** Visual evidence of the issue (e.g., bot's reply, Google Sheet content).
*   **Relevant Logs:** Snippets from GCF logs (and browser console if applicable during setup) that show errors or relevant activity. Please remove any sensitive information before sharing logs.

This structured approach will help in efficiently diagnosing and resolving any problems.
```
