# Zepto E-commerce Automation Workflow (n8n + Selenium)

## Overview

Designed a scheduled agent that integrates messaging-based user input with full browser automation to autonomously order products from Zepto, an e-commerce platform, and initiate online payments.

---

## Folder Structure

```
zepto_automation
│── n8n_workflow.json   # n8n workflow with Telegram trigger + HTTP node
│── server.py           # Flask server AND Selenium automation script for Zepto
│── test.py             # Script to save Chrome profile + Zepto login session
│── requirements.txt    # Python dependencies
│── README.md
│── venv/               # Optional virtual environment for Python dependencies
```

---

## Prerequisites

* Python 3.x
* pip
* Google Chrome + matching chromedriver
* n8n instance (Docker or local)
* Telegram Bot (created through BotFather)
* Ngrok (for exposing your Flask endpoint to Internet)
* (Optional) Python virtual environment

---

## Installation & Configuration

### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Run `/newbot` and follow the instructions
3. Copy the **Bot Token** (you’ll need it in n8n)

### 2. Setup Python Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
```

### 3. Install Python Dependencies

Create a `requirements.txt` file with the following content:

```
selenium
requests
pyTelegramBotAPI
flask
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 4. Configure n8n

1. Add a **Telegram Trigger** node and provide your Bot Token
2. Add an **HTTP Request** node with:

   * **Method**: POST
   * **URL**: `http://<ngrok-url>/order`
   * **Body**: `{ "item": {{$json["message"]["text"] }} }`
3. Connect Telegram Trigger → HTTP Request
4. Activate the workflow

### 5. Setup & Run Flask Server

```bash
python server.py
```

> The server exposes a single endpoint `/order` that accepts `POST` requests with the JSON body: `{ "item": "apple" }`

### 6. Configure Ngrok

```bash
ngrok http 5000
```

Copy the **https** URL from ngrok and update the URL in the n8n HTTP Request node.

### 7. Save Chrome Profile and Zepto Login

```bash
python test.py
```

This opens Chrome → manually log in to Zepto → close the browser. Your Chrome profile will be saved and reused for automation.

### 8. Run the Automation Script

The `server.py` script directly runs the Selenium automation logic. It:

* Loads the saved Chrome profile
* Opens Zepto
* Searches for the item (passed from Telegram)
* Adds it to cart
* Proceeds to payment and selects UPI
* Uses your hard-coded UPI ID for payment
* Waits for you to approve the transaction on your phone

Once payment is complete, the script prints `Order Confirmed`.

---

## Usage

1. Open Telegram and send your bot a message (e.g., `apple`)
2. The n8n flow triggers and calls `/order`
3. Selenium opens Zepto, adds the item to the cart, and waits for UPI confirmation
4. Once the transaction is approved, the order is successfully placed.

---

## Notes

* The UPI ID and token are **hard-coded** in `server.py`. Exercise caution if sharing or publishing the code.
* Ngrok free tier rotates URLs, so update n8n whenever ngrok restarts.
* Telegram can be leveraged for additional functionality (e.g., cancel order, check status, schedule orders).
* Using a virtual environment is recommended to isolate dependencies.

---

## Example (Telegram to Zepto Order Flow)

```
User → Telegram Bot:  "apple"
Telegram Trigger → HTTP Request → server.py → Selenium → Zepto → Add to cart → UPI payment → User approves → Order Completed
```

---

## Future Improvements

* Store UPI credentials securely using environment variables or a vault
* Integrate Scheduler in n8n to place orders automatically (e.g., every morning at 6 AM)
* Add error handling and retry logic in Selenium
* Support multiple items in a single order
* Use Playwright instead of Selenium for improved reliability

---

## Conclusion

This project is a fully working proof of concept that uses n8n, Telegram, and Selenium to automate Zepto orders. With a few enhancements, it can evolve into a production-grade personal automation tool.
