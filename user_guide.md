# WhatsApp Bot User Guide

This guide provides simple instructions for interacting with the WhatsApp Bot and for administrators viewing the recorded orders in Google Sheets.

## I. Interacting with the WhatsApp Bot

Our WhatsApp bot is designed to help you easily browse items and make selections.

*   **How to Start:**
    To begin interacting with the bot, send a message like "Привет", "Меню", or "/start" to its WhatsApp number. The bot will greet you and present the main menu.

*   **Navigating Menus:**
    The bot will present you with interactive menus (often as lists or buttons within WhatsApp). Simply tap on the option you wish to select from the choices provided. This will either take you to another menu or perform an action.

*   **Making Selections:**
    When you navigate to items you are interested in (e.g., specific embroidery kits or thread sets), selecting an item will typically confirm your choice and, for items intended for purchase, it will be recorded by our system. The bot will usually send a confirmation message like "✅ '[Item Name]' добавлен(о) в вашу корзину..."

*   **Contacting Support:**
    If you need assistance, have questions, or wish to speak to a person, please use the "📞 Связаться с менеджером" option, usually found in the main menu. The bot will provide further instructions or confirm that a manager will contact you.

## II. Viewing Recorded Orders in Google Sheets

For administrators or team members managing orders:

*   **Sheet Name:**
    Selected items and preliminary order details are recorded in a Google Sheet. The default name for this sheet is "**Бот_Заказы_Вышивка**". However, this name might have been customized during the bot's deployment (check the `GOOGLE_SHEET_NAME` environment variable in the Google Cloud Function settings if you are unsure).

*   **Accessing the Sheet:**
    You can access this Google Sheet directly via your Google Drive or by searching for its name in Google Sheets. You must be logged into a Google account that has been granted permission to view and/or edit the sheet. Typically, this would be the Google account that created the sheet or the service account associated with the bot (if you have direct access to view what the service account can see, though usually sharing with relevant user accounts is preferred).

*   **Understanding the Columns:**
    The data in the sheet is organized into the following columns:

    *   **A: `Timestamp` (Время заказа):** The date and time when the user selected the item.
    *   **B: `WhatsApp_ClientID` (ID клиента WhatsApp):** The unique WhatsApp identifier of the user who made the selection.
    *   **C: `SelectedItem` (Выбранный товар/категория):** The name of the item or category chosen by the user.
    *   **D: `ItemDetails` (Детали товара/выбранные опции):** A description or any further details associated with the selected item (often taken from the item's description in the bot's menu).
    *   **E: `Price` (Цена):** The price of the selected item.
    *   **F: `Status` (Статус заказа):** The initial status of the order, which defaults to "**Новый**" (New) when an item is first selected. This status may be updated manually in the sheet as the order is processed.

## III. If You Encounter Issues

*   **Bot Not Responding or Errors:** If the bot doesn't respond as expected, or if you see error messages, it's possible there's a temporary issue.
*   **Troubleshooting:** For technical issues, please refer to the troubleshooting section in the `deployment_guide.md` document provided with the bot's source files. This guide contains steps for diagnosing common problems.
*   **Contact Administrator:** If you are an end-user, please notify the person or team responsible for administering the bot about the issue. If you are the administrator, consult the deployment guide and check the Google Cloud Function logs.

We hope you find the bot easy and convenient to use!
```
