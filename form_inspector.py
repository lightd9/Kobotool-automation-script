#!/usr/bin/env python3


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json


class FormInspector:
    def __init__(self, form_url):
        self.form_url = form_url
        self.driver = None
        
    def setup_driver(self):
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        
    def inspect_form(self):
        try:
            print("Loading form...")
            self.driver.get(self.form_url)
            time.sleep(5)
            
            print("\n" + "="*80)
            print("FORM INSPECTION REPORT")
            print("="*80 + "\n")
            
            # Get all input fields
            print("INPUT FIELDS:")
            print("-" * 80)
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            for idx, inp in enumerate(inputs, 1):
                input_type = inp.get_attribute("type")
                input_name = inp.get_attribute("name")
                input_id = inp.get_attribute("id")
                input_class = inp.get_attribute("class")
                print(f"\n{idx}. Input Field:")
                print(f"   Type: {input_type}")
                print(f"   Name: {input_name}")
                print(f"   ID: {input_id}")
                print(f"   Class: {input_class}")
            
            print("\n\nSELECT/DROPDOWN FIELDS:")
            print("-" * 80)
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            for idx, sel in enumerate(selects, 1):
                select_name = sel.get_attribute("name")
                select_id = sel.get_attribute("id")
                select_class = sel.get_attribute("class")
                options = sel.find_elements(By.TAG_NAME, "option")
                print(f"\n{idx}. Select Field:")
                print(f"   Name: {select_name}")
                print(f"   ID: {select_id}")
                print(f"   Class: {select_class}")
                print(f"   Options: {[opt.text for opt in options[:5]]}")
            
            print("\n\nTEXTAREA FIELDS:")
            print("-" * 80)
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            for idx, ta in enumerate(textareas, 1):
                ta_name = ta.get_attribute("name")
                ta_id = ta.get_attribute("id")
                ta_class = ta.get_attribute("class")
                print(f"\n{idx}. Textarea Field:")
                print(f"   Name: {ta_name}")
                print(f"   ID: {ta_id}")
                print(f"   Class: {ta_class}")
            
            print("\n\nBUTTONS:")
            print("-" * 80)
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for idx, btn in enumerate(buttons, 1):
                btn_type = btn.get_attribute("type")
                btn_text = btn.text
                btn_class = btn.get_attribute("class")
                print(f"\n{idx}. Button:")
                print(f"   Type: {btn_type}")
                print(f"   Text: {btn_text}")
                print(f"   Class: {btn_class}")
            
            print("\n\nQUESTION LABELS:")
            print("-" * 80)
            labels = self.driver.find_elements(By.TAG_NAME, "label")
            for idx, label in enumerate(labels[:20], 1):  # First 20 labels
                label_text = label.text.strip()
                label_for = label.get_attribute("for")
                if label_text:
                    print(f"\n{idx}. {label_text}")
                    print(f"   For: {label_for}")
            
            print("\n" + "="*80)
            print("INSPECTION COMPLETE")
            print("="*80 + "\n")
            
            print("Saving page HTML for detailed inspection...")
            with open("C:\\Users\\HP\\Downloads\\files\\form_html.txt", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print("HTML saved to: C:\\Users\\HP\\Downloads\\files\\form_html.txt")
            
            print("\nBrowser will remain open for 60 seconds for manual inspection...")
            print("Press Ctrl+C to close earlier.")
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n\nInspection interrupted by user.")
        except Exception as e:
            print(f"Error during inspection: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()


def main():
    FORM_URL = ""
    
    inspector = FormInspector(FORM_URL)
    inspector.setup_driver()
    inspector.inspect_form()


if __name__ == "__main__":
    main()
