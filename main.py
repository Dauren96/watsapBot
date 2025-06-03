import logging
import json # For constructing payloads
import os # For environment variables
from flask import Flask, request, jsonify
from menu_data import MENU, get_menu, get_option_by_id # Import menu data and helpers
from sheets_client import add_order_to_sheet # Import Google Sheets function

# Configure logging (central configuration)
# This basicConfig should ideally be called only once.
# If run directly (__name__ == '__main__'), it might be called again, but usually harmless.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
# Get a logger specific to this module
logger = logging.getLogger(__name__)

app = Flask(__name__) # GCF entry point

# --- Configuration from Environment Variables ---
# For GCF, these MUST be set in the function's environment variables.
# For local development, set them in your shell or a .env file (using python-dotenv, for example).
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")

# GOOGLE_SHEET_NAME is handled in sheets_client.py via os.getenv
# GOOGLE_APPLICATION_CREDENTIALS for gspread:
# - In GCF: Not needed if the function's runtime service account has Sheets API permissions.
# - Locally: Must be set to the path of your service account JSON key file.

if not VERIFY_TOKEN:
    logger.warning("VERIFY_TOKEN environment variable is not set. Webhook verification will fail.")
if not WHATSAPP_PHONE_NUMBER_ID:
    logger.warning("WHATSAPP_PHONE_NUMBER_ID environment variable is not set. Message sending will be misconfigured.")
if not WHATSAPP_ACCESS_TOKEN:
    logger.warning("WHATSAPP_ACCESS_TOKEN environment variable is not set. Message sending will fail.")


# --- User State Management ---
user_states = {} # Stores user's current menu and cart, e.g., {'whatsapp_id': {'current_menu_id': 'main_menu', 'cart': []}}

# --- WhatsApp Message Sending Placeholder ---
def send_whatsapp_message(recipient_wa_id, message_data):
    """
    Simulates sending a WhatsApp message.
    In a real application, this function would make an HTTP POST request to the WhatsApp API.
    """
    if not message_data:
        logger.error(f"No message data provided for {recipient_wa_id}")
        return

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_wa_id,
        "type": message_data.get("type", "text")
    }

    if message_data["type"] == "text":
        payload["text"] = {"body": message_data.get("text", "Error: No text defined.")}
    elif message_data["type"] == "interactive":
        interactive_payload = {
            "type": message_data.get("interactive_type", "list"),
            "body": {"text": message_data.get("title", "Menu")},
            "action": {}
        }

        options = message_data.get("options", [])
        if message_data.get("interactive_type") == "button":
            buttons = []
            for opt in options[:3]:
                buttons.append({"type": "reply", "reply": {"id": opt["id"], "title": opt["title"][:20]}})
            interactive_payload["action"]["buttons"] = buttons

        elif message_data.get("interactive_type") == "list":
            interactive_payload["action"]["button"] = message_data.get("button_cta", "Выбрать")
            sections = [{"title": message_data.get("section_title", "Опции"), "rows": []}]
            for opt in options[:10]:
                row = {"id": opt["id"], "title": opt["title"][:24]}
                if opt.get("description"):
                    row["description"] = opt["description"][:72]
                sections[0]["rows"].append(row)
            interactive_payload["action"]["sections"] = sections
            if message_data.get("header"):
                 interactive_payload["header"] = {"type": "text", "text": message_data.get("header")}
            if message_data.get("footer"):
                interactive_payload["footer"] = {"type": "text", "text": message_data.get("footer")}
        payload["interactive"] = interactive_payload
    else:
        logger.error(f"Unsupported message type: {message_data['type']} for {recipient_wa_id}")
        return

    logger.info(f"SIMULATING SENDING to {recipient_wa_id} via PhoneID {WHATSAPP_PHONE_NUMBER_ID} with AccessToken {WHATSAPP_ACCESS_TOKEN[:5]}...")
    logger.info(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")


def handle_user_message(sender_id, message_content):
    """
    Main logic for handling incoming messages and user interactions.
    """
    user_state = user_states.get(sender_id, {'current_menu_id': 'main_menu', 'cart': []})
    current_menu_id = user_state.get('current_menu_id', 'main_menu')

    selected_option_id = None
    user_text_input = None

    if message_content.get('type') == 'interactive':
        selected_option_id = message_content.get('interactive_reply_id')
        logger.info(f"User {sender_id} selected option: {selected_option_id} from menu: {current_menu_id}")
    elif message_content.get('type') == 'text':
        user_text_input = message_content.get('text', '').strip().lower()
        logger.info(f"User {sender_id} sent text: {user_text_input}")
        if user_text_input in ["меню", "start", "привет", "здравствуйте", "hi", "hello", "/start"]:
            current_menu_id = 'main_menu'
            user_state['current_menu_id'] = current_menu_id
            menu_to_send = get_menu(current_menu_id)
            if menu_to_send:
                menu_to_send['interactive_type'] = menu_to_send.get('type', 'list')
                send_whatsapp_message(sender_id, menu_to_send)
            user_states[sender_id] = user_state
            return

    option_details = None
    if selected_option_id:
        option_details = get_option_by_id(current_menu_id, selected_option_id)

    if option_details:
        if option_details.get('next_menu_id'):
            next_menu_id = option_details['next_menu_id']
            user_state['current_menu_id'] = next_menu_id
            menu_to_send = get_menu(next_menu_id)
            if menu_to_send:
                menu_to_send['interactive_type'] = menu_to_send.get('type', 'list')
                send_whatsapp_message(sender_id, menu_to_send)

        elif option_details.get('action'):
            action = option_details['action']
            if action == 'select_item':
                item_name = option_details.get('title', 'Неизвестный товар')
                item_price = option_details.get('price', 0)
                item_description = option_details.get('description', '') # Get description for details

                user_state.setdefault('cart', []).append({'id': option_details['id'], 'name': item_name, 'price': item_price, 'description': item_description})
                logger.info(f"Item '{item_name}' added to cart for user {sender_id}. Cart: {user_state['cart']}")

                # --- Add to Google Sheets ---
                order_data_for_sheets = {
                    'client_id': sender_id,
                    'item_name': item_name,
                    'details': item_description, # Using item's menu description as details
                    'price': item_price
                }
                if add_order_to_sheet(order_data_for_sheets):
                    logger.info(f"Order for {sender_id} (Item: {item_name}) successfully recorded in Google Sheets.")
                else:
                    logger.error(f"Failed to record order for {sender_id} (Item: {item_name}) in Google Sheets.")
                # --- End Google Sheets ---

                confirmation_msg_template = get_menu('item_selected_confirmation')
                if confirmation_msg_template:
                    confirmation_text = confirmation_msg_template['text'].format(item_name=item_name, item_price=item_price)
                    send_whatsapp_message(sender_id, {'type': 'text', 'text': confirmation_text})

                current_display_menu = get_menu(current_menu_id)
                if current_display_menu:
                     current_display_menu['interactive_type'] = current_display_menu.get('type', 'list')
                     send_whatsapp_message(sender_id, current_display_menu)

            elif action == 'contact_manager':
                contact_msg = get_menu('contact_manager_message')
                if contact_msg:
                    send_whatsapp_message(sender_id, contact_msg)
        else:
            logger.warning(f"Option {selected_option_id} has no next_menu_id or action defined.")
            menu_to_send = get_menu(current_menu_id)
            if menu_to_send:
                 menu_to_send['interactive_type'] = menu_to_send.get('type', 'list')
                 send_whatsapp_message(sender_id, menu_to_send)

    elif user_text_input and not selected_option_id :
        fallback_msg = get_menu('default_fallback_message')
        if fallback_msg:
            send_whatsapp_message(sender_id, fallback_msg)

    user_states[sender_id] = user_state


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        logger.info("Received GET request for webhook verification.")
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            logger.info(f"Webhook verified successfully. Responding with challenge: {challenge}")
            return challenge, 200
        else:
            logger.warning("Webhook verification failed. Mode or token mismatch.")
            return jsonify({"status": "error", "message": "Verification token mismatch"}), 403

    elif request.method == 'POST':
        logger.info("Received POST request (incoming message).")
        data = request.get_json()
        logger.info(f"Received data: {json.dumps(data, indent=2, ensure_ascii=False)}")

        try:
            if data.get('object') == 'whatsapp_business_account':
                for entry in data.get('entry', []):
                    for change in entry.get('changes', []):
                        value = change.get('value', {})
                        if change.get('field') == 'messages':
                            contacts = value.get('contacts', [{}])
                            sender_id = contacts[0].get('wa_id')

                            message_object = value.get('messages', [{}])[0]
                            message_type = message_object.get('type')

                            parsed_message_content = {}

                            if message_type == 'text':
                                parsed_message_content = {
                                    'type': 'text',
                                    'text': message_object.get('text', {}).get('body')
                                }
                            elif message_type == 'interactive':
                                interactive_data = message_object.get('interactive', {})
                                reply_type = interactive_data.get('type')
                                if reply_type == 'button_reply':
                                    parsed_message_content = {
                                        'type': 'interactive',
                                        'interactive_reply_id': interactive_data.get('button_reply', {}).get('id')
                                    }
                                elif reply_type == 'list_reply':
                                    parsed_message_content = {
                                        'type': 'interactive',
                                        'interactive_reply_id': interactive_data.get('list_reply', {}).get('id')
                                    }
                                else:
                                    logger.warning(f"Unknown interactive reply type: {reply_type}")
                                    parsed_message_content = {'type': 'unknown_interactive'}

                            elif message_type == 'button':
                                 parsed_message_content = {
                                    'type': 'text',
                                    'text': message_object.get('button', {}).get('text')
                                }
                            else:
                                logger.info(f"Received unhandled message type: {message_type} from {sender_id}")
                                fallback_msg = get_menu('default_fallback_message')
                                if fallback_msg and sender_id:
                                     send_whatsapp_message(sender_id, fallback_msg)
                                return jsonify({"status": "success", "message": "Webhook received, unhandled message type"}), 200

                            if sender_id and parsed_message_content and parsed_message_content.get('type') != 'unknown_interactive':
                                if sender_id not in user_states or \
                                   (parsed_message_content.get('type') == 'text' and \
                                    parsed_message_content.get('text', '').lower() in ["меню", "start", "привет", "здравствуйте", "hi", "hello", "/start"]):

                                    logger.info(f"New user {sender_id} or explicit menu request: {parsed_message_content.get('text', '')}")
                                    user_states[sender_id] = {'current_menu_id': 'main_menu', 'cart': []}
                                    main_menu_data = get_menu('main_menu')
                                    if main_menu_data:
                                        main_menu_data['interactive_type'] = main_menu_data.get('type', 'list')
                                        send_whatsapp_message(sender_id, main_menu_data)
                                else:
                                    handle_user_message(sender_id, parsed_message_content)
                            elif parsed_message_content.get('type') == 'unknown_interactive':
                                logger.warning(f"Not processing unknown interactive message for {sender_id}")
                                # Optionally send a message like "I didn't understand that button."
                            else:
                                logger.warning(f"Could not extract sender_id or valid message content for data: {message_object}")

            return jsonify({"status": "success", "message": "Webhook processed"}), 200
        except Exception as e:
            logger.error(f"Error processing POST request: {e}", exc_info=True)
            logger.error(f"Problematic data: {data}")
            return jsonify({"status": "error", "message": "Internal server error during processing"}), 200

    else:
        logger.warning(f"Received request with unsupported method: {request.method}")
        return jsonify({"status": "error", "message": "Method Not Allowed"}), 405

if __name__ == '__main__':
    # This block runs only when the script is executed directly (e.g., for local development).
    # It will not run when deployed to Google Cloud Functions (GCF).
    # For local development, ensure you have set the required environment variables:
    # VERIFY_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN,
    # GOOGLE_APPLICATION_CREDENTIALS (pointing to your JSON key file),
    # and optionally GOOGLE_SHEET_NAME.

    # Re-apply basicConfig here IF you want a different level/format for local CLI execution,
    # otherwise the one at the top of the file is sufficient if it's already INFO.
    # For consistency, we can ensure it's set if this module is the entry point.
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )

    logger.info("--- Starting Flask Development Server (main.py executed directly) ---")

    if not all([VERIFY_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN]):
        logger.critical("CRITICAL: One or more required environment variables (VERIFY_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN) are NOT set.")
        logger.critical("The application may not function correctly for webhook verification or message sending.")

    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        logger.warning("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set for local development.")
        logger.warning("Google Sheets integration will likely fail locally unless the gcloud CLI is authenticated with Application Default Credentials having Sheets access.")

    # Use PORT environment variable if available (common for cloud platforms), default to 8080.
    local_port = int(os.getenv('PORT', 8080))

    # Setting debug=True is useful for development but should be False in production.
    # GCF manages the production environment, so this debug setting is only for local.
    app.run(host='0.0.0.0', port=local_port, debug=True)
```
