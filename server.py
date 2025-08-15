from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import threading
import time
import requests

# -------------------- CONFIG --------------------
TELEGRAM_TOKEN = "your-telegram-token"
UPI_ID = "your-upi-id"
CHROME_PROFILE_PATH = r"your-chrome-profile-path"
# ------------------------------------------------

app = Flask(__name__)

# --------------- SAFE CLICK FUNCTION ---------------
def safe_click(driver, element):
    try:
        # Scroll into center view
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)
        # Simulate real user click
        ActionChains(driver).move_to_element(element).pause(0.3).click().perform()
    except:
        # Fallback to JS click
        driver.execute_script("arguments[0].click();", element)
# ----------------------------------------------------

def run_zepto(items, chat_id):
    print(f"Starting automation for items: {items}")
    
    if not items:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": chat_id, "text": "❌ No items provided for automation"}
        )
        return

    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")
    options.add_experimental_option("detach", True)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        # Navigate to Zepto
        driver.get("https://www.zeptonow.com/")
        driver.maximize_window()
        time.sleep(5)

        # Close popup if present
        try:
            popup_close = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".absolute.right-3.top-3.z-10.flex.h-7.w-7.items-center.justify-center.rounded-full.bg-[#0b0c0e99].p-1"))
            )
            safe_click(driver, popup_close)
            time.sleep(1)
        except:
            pass

        # -------------------- ADD ITEMS --------------------
        for item in items:
            try:
                print(f"Searching for item: {item}")
                search_url = f"https://www.zeptonow.com/search?query={item.replace(' ', '%20')}"
                driver.get(search_url)
                time.sleep(5)

                add_button_selectors = [
                    "//button[contains(text(), 'ADD')]",
                    "//button[contains(@class, 'add-to-cart')]"
                ]

                added = False
                for selector in add_button_selectors:
                    try:
                        add_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        print(f"Found ADD button using selector: {selector}")
                        safe_click(driver, add_button)
                        print(f"✅ Successfully added {item} to cart")
                        added = True
                        time.sleep(2)
                        break
                    except Exception as e:
                        print(f"❌ Click failed for selector {selector}: {e}")
                        continue

                if not added:
                    print(f"⚠ Could not add {item} to cart")

            except Exception as e:
                print(f"Failed for item '{item}': {e}")
                continue

        # -------------------- GO TO CHECKOUT --------------------
        try:
            print("Looking for cart button...")
            cart_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='cart-btn']"))
            )
            safe_click(driver, cart_button)
            time.sleep(5)
            print("Cart button clicked")

            try:
                WebDriverWait(driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Cart')]")),
                        EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Cart')]"))
                    )
                )
                print("On cart page")
            except:
                print("Not fully loaded, continuing...")

            pay_button_selectors = [
                "//span[contains(text(), 'Click to Pay')]//parent::button",
                "//button[contains(text(), 'Click to Pay')]"
            ]

            pay_clicked = False
            for selector in pay_button_selectors:
                try:
                    pay_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    safe_click(driver, pay_button)
                    pay_clicked = True
                    time.sleep(5)
                    print("Clicked pay button")
                    break
                except:
                    continue

            if not pay_clicked:
                print("⚠ Pay button not found")

        except Exception as e:
            print(f"Cart/Pay process failed: {e}")

        # -------------------- HANDLE PAYMENT --------------------
        try:
            time.sleep(5)
            current_url = driver.current_url
            if "zeptonow.com" not in current_url:
                print("Redirected to payment gateway")
                try:
                    upi_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "20000025"))
                    )
                    safe_click(driver, upi_button)
                    print("✅ Clicked UPI payment option ")

                    # Enter UPI ID
                    upi_input = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//input[contains(@placeholder, 'e.g rakesh@upi') or contains(@aria-label, 'UPI')]"))
                    )
                    upi_input.clear()
                    upi_input.send_keys(UPI_ID)
                    print(f"✅ Entered UPI ID: {UPI_ID}")

                    # Click verify and Pay button
                    try:
                        pay_btn = WebDriverWait(driver, 15).until(
                            EC.element_to_be_clickable((By.ID, "20000270"))
                        )
                        safe_click(driver, pay_btn)
                        print("✅ Clicked verify and Pay button")
                    except Exception as e:
                        print(f"❌ Could not find/click Pay button: {e}")
                except Exception as e:
                    print(f"❌ Could not complete UPI payment flow: {e}")
        except Exception as e:
            print(f"Error on payment page: {e}")
        
        # Telegram confirmation
        msg = f"✅ '{', '.join(items)}' ready for checkout! Complete payment manually."
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": chat_id, "text": msg}
        )

    except Exception as e:
        error_msg = f"❌ Automation failed for '{', '.join(items)}': {str(e)}"
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": chat_id, "text": error_msg}
        )

@app.route("/order", methods=["POST"])
def order():
    try:
        data = request.json
        items = data.get("items", [])
        if not items and "item" in data:
            single_item = data.get("item")
            if isinstance(single_item, str):
                items = [single_item]
            elif isinstance(single_item, list):
                items = single_item

        chat_id = data.get("chat_id")
        if not chat_id:
            return {"status": "error", "message": "chat_id is required"}, 400
        if not items:
            return {"status": "error", "message": "No items provided"}, 400

        threading.Thread(target=run_zepto, args=(items, chat_id)).start()
        return {"status": "success", "message": f"Started automation for {len(items)} items"}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route("/test", methods=["POST", "GET"])
def test():
    if request.method == "POST":
        data = request.json
        return {"received_data": data, "status": "success"}
    else:
        return {"message": "Test endpoint working", "status": "success"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

