from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# Chrome setup
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # Optional
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

driver = webdriver.Chrome(options=options)
driver.get("https://www.tradingview.com/markets/stocks-usa/market-movers-all-stocks/")
wait = WebDriverWait(driver, 20)

# Track how many times "Load More" clicked
click_count = 0

# Keep loading more until button disappears
while True:
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        load_more_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "button-SFwfC2e0")))
        driver.execute_script("arguments[0].click();", load_more_btn)
        click_count += 1

        # Show rows count after each click
        rows_now = driver.find_elements(By.CLASS_NAME, "row-RdUXZpkv")
        print(f"🔄 Clicked 'Load More' {click_count} times — Rows loaded: {len(rows_now)}")
        time.sleep(2)
    except:
        print("✅ No more 'Load More' button. All rows loaded.")
        break

# Final scrape
rows = driver.find_elements(By.CLASS_NAME, "row-RdUXZpkv")
print(f"\n📈 Final total rows found: {len(rows)}\n")

data = []
for index, row in enumerate(rows, 1):
    try:
        columns = row.find_elements(By.TAG_NAME, 'td')
        if len(columns) >= 12:
            symbol_elem = columns[0].find_element(By.CLASS_NAME, "tickerNameBox-GrtoTeat")
            security_elem = columns[0].find_element(By.CLASS_NAME, "tickerDescription-GrtoTeat")

            data.append([
                symbol_elem.text,
                security_elem.text,
                columns[1].text,
                columns[2].text,
                columns[3].text,
                columns[4].text,
                columns[5].text,
                columns[6].text,
                columns[7].text,
                columns[8].text,
                columns[9].text,
                columns[10].text,
                columns[11].text,
            ])

        # Show progress after every 50 rows
        if index % 50 == 0:
            print(f"💾 Scraped {index} rows so far...")
    except Exception as e:
        print(f"❌ Error reading row {index}:", e)

# Save to CSV
csv_file = 'tradingview_all_stocks.csv'
with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        'Symbol', 'Security Name', 'Price', 'Change %','Volume',
        'Rel Volume', 'Market Cap', 'P/E Ratio', 'EPS(TTM)', 'EPS Growth',
        'Div Yield', 'Sector', 'Analyst Rating'
    ])
    writer.writerows(data)

print(f"\n✅ Total 'Load More' Clicks: {click_count}")
print(f"✅ Total Rows Saved: {len(data)}")
print(f"✅ Data saved to '{csv_file}'")

driver.quit()
