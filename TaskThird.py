from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

# Setup headless browser
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

# All desired fields including new ones
desired_fields = [
    "Symbol",
    "Next report date",
    "Report period",
    "EPS estimate",
    "Revenue estimate",
    "Market capitalization",
    "Dividend yield (indicated)",
    "Price to earnings Ratio (TTM)",
    "Basic EPS (TTM)",
    "Net income (FY)",
    "Revenue (FY)",
    "Shares float",
    "Beta (1Y)",
    "Employees (FY)",
    "Change (1Y)",
    "Revenue / Employee (1Y)",
    "Net income / Employee (1Y)",
    # New fields
    "Sector",
    "Industry",
    "CEO",
    "Website",
    "Headquarters",
    "Founded",
    "FIGI"
]

# Load symbols from file
symbols = []
with open("tradingview_all_stocks.csv", 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)  # Skip header
    for row in reader:
        symbols.append(row[0])

all_data = []

for idx, symbol in enumerate(symbols[:50], 1):  # Change as needed
    url = f"https://www.tradingview.com/symbols/{symbol}/"
    driver.get(url)
    print(f"🔄 {idx}. Fetching {symbol} from {url}")
    time.sleep(2)

    row_data = {field: "" for field in desired_fields}
    row_data["Symbol"] = symbol

    try:
        # Wait for main financial blocks
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "block-QCJM7wcY")))
        blocks = driver.find_elements(By.CLASS_NAME, "block-QCJM7wcY")

        for block in blocks:
            try:
                label = block.find_element(By.CLASS_NAME, "label-QCJM7wcY").text.strip()
                try:
                    value = block.find_element(By.CLASS_NAME, "container--highlighted-Zvbuvzhn").text.strip()
                except:
                    value = block.find_element(By.CLASS_NAME, "value-QCJM7wcY").text.strip()

                if label in row_data:
                    row_data[label] = value

            except Exception:
                continue

        # Scrape company profile info - usually in a different block, e.g. with "company-profile__info"
        try:
            profile_section = driver.find_element(By.CLASS_NAME, "company-profile__info")

            # For each field try to find it by its label on the profile block
            # Profile info labels often are in spans or dt/dd pairs, so we search by text

            profile_items = profile_section.find_elements(By.XPATH, ".//div[contains(@class,'company-profile__item')]")
            for item in profile_items:
                try:
                    label = item.find_element(By.CLASS_NAME, "company-profile__label").text.strip()
                    value = item.find_element(By.CLASS_NAME, "company-profile__value").text.strip()
                    # Match label text to desired fields, some might need mapping if label names differ
                    if label in row_data:
                        row_data[label] = value
                except Exception:
                    continue

        except Exception:
            # If profile section not found, pass
            pass

        # Scrape FIGI - often under identifiers or somewhere on the page, try this:
        try:
            # Example: Find the FIGI under identifiers section
            identifiers = driver.find_elements(By.CLASS_NAME, "company-profile__identifiers-item")
            for ident in identifiers:
                text = ident.text
                if "FIGI" in text:
                    # Extract FIGI code
                    figi_value = text.split("FIGI")[-1].strip(": ").strip()
                    row_data["FIGI"] = figi_value
                    break
        except Exception:
            pass

        all_data.append(row_data)
        print(f"✅ Success: {symbol}")

    except Exception as e:
        print(f"❌ Failed: {symbol} - {e}")
        all_data.append({"Symbol": symbol, "Error": "Not Found"})

# Write to CSV
with open("symbol_detailed_stats.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=desired_fields)
    writer.writeheader()
    writer.writerows(all_data)

print("\n✅ All data saved in 'symbol_detailed_stats.csv'")
driver.quit()
