from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd

URL = "https://sarmaaya.pk/mutual-funds/"
WAIT_TIME = 3  

def start_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    return driver

def extract_visible_data(driver):
    rows = driver.find_elements(By.CSS_SELECTOR, "#funds-table tbody tr")
    data = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        visible_texts = []
        for col in cols:
            visible = driver.execute_script(
                "return (window.getComputedStyle(arguments[0]).display !== 'none') && (arguments[0].offsetParent !== null);",
                col
            )
            if visible:
                visible_texts.append(col.text.strip())
        if len(visible_texts) == 11:
            data.append(visible_texts)
        else:
            print(f"⚠️ Skipping row due to unexpected columns: found {len(visible_texts)} columns")
    return data

def click_next(driver):
    try:
        next_li = driver.find_element(By.ID, "funds-table_next")
        next_btn = next_li.find_element(By.TAG_NAME, "a")

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
        time.sleep(1) 

        # Check if disabled
        if "disabled" in next_li.get_attribute("class"):
            return False

        next_btn.click()
        return True
    except Exception as e:
        print(f"⚠️ Error clicking next: {e}")
        return False


def main():
    driver = start_browser()
    driver.get(URL)
    time.sleep(WAIT_TIME)

    all_data = []
    page = 1

    while True:
        print(f"📄 Scraping page {page}...")
        page_data = extract_visible_data(driver)
        all_data.extend(page_data)

        if not click_next(driver):
            print("🚫 No more pages. Stopping.")
            break
        
        page += 1
        time.sleep(WAIT_TIME)

    driver.quit()

    # Save data
    columns = ["Fund Name", "RP", "PM", "TER", "MF", "SAM", "ReturnMTD", "ReturnYTD", "NAV", "Date", "AUM"]
    df = pd.DataFrame(all_data, columns=columns)
    df.to_csv("mutual_funds_data.csv", index=False)
    print(f"✅ Saved {len(df)} records to mutual_funds_data.csv")

if __name__ == "__main__":
    main()