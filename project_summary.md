# Project Summary: WhatsApp Order Bot

## Project Overview

This project implements a WhatsApp bot designed for taking orders for embroidery items. Users can interact with the bot through a menu-driven interface on WhatsApp. Selected items are recorded in a Google Sheet for order fulfillment. The bot is built using Python and Flask, and is intended for deployment on Google Cloud Functions (GCF).

## Generated Files

This project consists of the following key files:

*   **`main.py`**:
    *   The core Python Flask application that serves as the webhook for the WhatsApp Business API.
    *   Handles incoming messages (`GET` for verification, `POST` for user messages).
    *   Manages user state (current menu, conceptual cart).
    *   Orchestrates responses by sending interactive menus or text messages.
    *   Integrates with `sheets_client.py` to record orders.

*   **`menu_data.py`**:
    *   Defines the structure, content, and navigation logic of the interactive menus presented to the user via WhatsApp.
    *   Includes menu titles, options, actions (like selecting an item or navigating to another menu), and prices.

*   **`sheets_client.py`**:
    *   A Python module responsible for all communication with the Google Sheets API.
    *   Handles authentication using Google Cloud service account credentials.
    *   Provides functions to connect to the specified Google Sheet and append new order rows with relevant details (timestamp, client ID, item name, details, price, status).

*   **`requirements.txt`**:
    *   Lists all necessary Python package dependencies for the project (e.g., `flask`, `gspread`, `google-auth`, `google-auth-oauthlib`).
    *   Used to install the correct packages in the deployment environment.

*   **`google_sheets_documentation.md`**:
    *   Provides detailed documentation on the expected Google Sheet structure (columns, sheet name).
    *   Explains how service account credentials are used by the Python application to interact with Google Sheets, including setup and security best practices.

*   **`deployment_guide.md`**:
    *   A comprehensive guide for deploying the WhatsApp bot application to Google Cloud Functions.
    *   Includes prerequisites, packaging instructions, `gcloud` deployment commands, environment variable setup, service account configuration, and steps for configuring the webhook in the Meta for Developers portal.

*   **`test_plan.md`**:
    *   A detailed plan for testing the deployed WhatsApp bot.
    *   Includes prerequisites for testing, specific test cases (covering webhook verification, menu navigation, item selection, Google Sheets logging, error handling), expected results, and troubleshooting tips.

*   **`user_guide.md`**:
    *   Simple instructions for end-users on how to interact with the WhatsApp bot.
    *   Provides guidance for administrators on how to view and understand the recorded orders in the Google Sheet.

## Key Technologies

*   **Python:** The primary programming language used for development.
*   **Flask:** A micro web framework used to build the webhook endpoint.
*   **Google Cloud Functions (GCF):** The serverless platform for deploying the bot.
*   **Google Sheets API:** Used for storing order data in a Google Sheet.
*   **gspread & google-auth Libraries:** Python libraries for interacting with the Google Sheets API and handling authentication.
*   **WhatsApp Business API:** The platform that enables communication with users via WhatsApp.

## Potential Next Steps & Further Enhancements

While this project provides a functional foundation, here are some potential areas for future development:

*   **Full Shopping Cart & Checkout:** Implement a more complete shopping cart where users can add multiple items, view their cart, modify quantities, and proceed to a formal checkout.
*   **Persistent State Management:** Replace the in-memory `user_states` dictionary with a more robust and scalable solution like Redis, Firestore, or a database for managing user sessions and cart data, especially if the bot needs to handle many concurrent users or remember state across function invocations.
*   **Order Management & Status Updates:** Allow administrators to update order statuses in the Google Sheet (e.g., "Processing", "Shipped") and potentially notify users of these changes via WhatsApp.
*   **Menu Management System:** Develop an administrative interface (web-based or via commands) for easier management of menu items, categories, and prices without direct code changes.
*   **Payment Integration:** Integrate with payment gateways to allow users to pay for their orders directly through the bot flow.
*   **Advanced NLP:** Incorporate Natural Language Processing (NLP) to understand more free-form user requests instead of relying solely on button clicks.
*   **Inventory Management:** Link item availability to an inventory system.
*   **User Accounts & Order History:** Allow users to create accounts and view their past order history.
```
