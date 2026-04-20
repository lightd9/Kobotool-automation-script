#!/usr/bin/env python3
"""
READY-TO-USE KoboToolbox Form Automation
with custom logic 
"""

import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


# CONFIGURATION 

FORM_URL = ""      #Kobo link
NUM_RESPONSES = 25      
DURATION_HOURS = 1.5      
HEADLESS = False        

# DATA GENERATION FUNCTIONS
def distribute_household_members(total_household, is_married=False):
    """
    Distribute household members across age groups and genders
    If married, ensures EXACTLY 1 male AND 1 female aged 18-60
    Returns dict with male/female counts for each age group
    """
    distribution = {
        "0_5_male": 0,
        "0_5_female": 0,
        "5_18_male": 0,
        "5_18_female": 0,
        "18_60_male": 0,
        "18_60_female": 0,
        "60_plus_male": 0,
        "60_plus_female": 0
    }
    
    remaining = total_household
    
    if is_married:
        distribution["18_60_male"] = 1
        distribution["18_60_female"] = 1
        remaining -= 2
    else:
        if random.random() > 0.5:
            distribution["18_60_male"] = 1
        else:
            distribution["18_60_female"] = 1
        remaining -= 1
    
    # Distribute the rest - prioritize 0-5 and 5-18 age groups
    age_groups_weighted = [
        ("0_5_male", "0_5_female"),      
        ("0_5_male", "0_5_female"),      
        ("5_18_male", "5_18_female"),    
        ("5_18_male", "5_18_female"),    
        ("5_18_male", "5_18_female"),    
        ("18_60_male", "18_60_female"),  
        ("60_plus_male", "60_plus_female")  
    ]
    
    while remaining > 0:
        age_group = random.choice(age_groups_weighted)
        gender_field = random.choice(age_group)
        distribution[gender_field] += 1
        remaining -= 1
    
    return distribution

def generate_round_number(min_val, max_val):
    base_numbers = [25000, 50000, 75000, 100000, 150000, 200000, 250000, 300000, 400000, 500000]
    valid_numbers = [n for n in base_numbers if min_val <= n <= max_val]
    if valid_numbers:
        return random.choice(valid_numbers)
    return round(random.randint(min_val, max_val) / 10000) * 10000

def generate_correlated_farm_data():
    farm_categories = {
        "<1 hectare": {
            "size": "<1 hectare",
            "annual_incomes": ["<300,000", "300,000-500,000"],
            "harvest_range": (40, 150),  # kg
            "price_per_kg": (500, 1000)  # Lower prices for smaller farms
        },
        "1-2": {
            "size": "1-2",
            "annual_incomes": ["300,000-500,000", "500,000-1,000,000"],
            "harvest_range": (100, 300),
            "price_per_kg": (600, 1200)
        },
        "2-5": {
            "size": "2-5",
            "annual_incomes": ["500,000-1,000,000", "1,000,000- 2,000,000"],
            "harvest_range": (250, 500),
            "price_per_kg": (700, 1300)
        },
        "5-10": {
            "size": "5-10",
            "annual_incomes": ["1,000,000- 2,000,000", ">2,000,000"],
            "harvest_range": (400, 700),
            "price_per_kg": (800, 1400)
        },
        ">10": {
            "size": ">10",
            "annual_incomes": [">2,000,000"],
            "harvest_range": (600, 800),
            "price_per_kg": (900, 1500)
        }
    }
    
    farm_size = random.choice(list(farm_categories.keys()))
    category = farm_categories[farm_size]
    
    annual_income = random.choice(category["annual_incomes"])
    if random.randint(1, 10) == 1:
        possible_harvests = [40, 50, 60, 70, 80, 90, 100]
        total_harvest = random.choice(possible_harvests)
        
        return {
            "farm_size": farm_size,
            "annual_income": annual_income,
            "sold_produce": "No",
            "total_harvest": total_harvest,
            "amount_sold": 0,
            "sales_income": 0
        }
    else:
        min_harvest, max_harvest = category["harvest_range"]
        
        possible_harvests = []
        current = min_harvest
        while current <= max_harvest:
            possible_harvests.append(current)
            if current < 100:
                current += 10
            else:
                current += 50
        
        total_harvest = random.choice(possible_harvests)
        
        sold_percentage = random.uniform(0.8, 1.0)
        amount_sold_raw = total_harvest * sold_percentage
        
        amount_sold = round(amount_sold_raw / 10) * 10
        if amount_sold > total_harvest:
            amount_sold = total_harvest
        if amount_sold == 0:
            amount_sold = 10
        
        min_price, max_price = category["price_per_kg"]
        price_per_kg = random.randint(min_price, max_price)
        sales_income = amount_sold * price_per_kg
        
        sales_income = round(sales_income / 100000) * 100000
        
        income_ranges = {
            "<300,000": (0, 300000),
            "300,000-500,000": (300000, 500000),
            "500,000-1,000,000": (500000, 1000000),
            "1,000,000- 2,000,000": (1000000, 2000000),
            ">2,000,000": (2000000, 5000000)
        }
        
        min_income, max_income = income_ranges[annual_income]
        
        min_sales = int(min_income * 0.4)
        max_sales = int(max_income * 0.8)
        
        if sales_income < min_sales:
            sales_income = random.randint(min_sales, int(min_income * 0.6))
            sales_income = round(sales_income / 1000) * 1000
        elif sales_income > max_sales:
            sales_income = random.randint(int(max_income * 0.5), max_sales)
            sales_income = round(sales_income / 1000) * 1000
        
        return {
            "farm_size": farm_size,
            "annual_income": annual_income,
            "sold_produce": "Yes",
            "total_harvest": total_harvest,
            "amount_sold": amount_sold,
            "sales_income": sales_income
        }
    
def generate_farmer_data():
    
    age = random.randint(22, 65)
    
    if age >= 55:
        marital_status = random.choice(["Married", "Married","Married","Married", "Widowed"])
    elif age >= 28:
        marital_status = "Married"
    elif age >= 24:        marital_status = random.choice(["Single", "Single", "Single", "Married"])
    else:
        marital_status = "Single"
    
    if marital_status == "Married":
        household_size = random.randint(3, 10)
    else:
        household_size = random.randint(1, 7)
    
    household_dist = distribute_household_members(household_size, is_married=(marital_status == "Married"))
    
    farming_years = random.choice(["0-5", "5-10", "10-15", "10-15","15 years and above"])
    
    if farming_years == "15 years and above":
        farming_reason = random.choice(["Farming tradition", "source of income", "Farming Tradition", "Farming trandition", "source of income"])
    else:
        farming_reason = random.choice([
            "Farming tradition", "source of income",
            "No other job available", "Personal Interest"
        ])
    
    own_land = random.choice(["Yes", "Yes", "Yes", "No"])
    if own_land == "Yes":
        land_acquisition = random.choice(["Inherited", "Purchased"])
    else:
        land_acquisition = random.choice(["Rented", "Communal"])
    
    if random.randint(1, 20) == 1:
        received_loan = "Yes"
        loan_amount = random.choice([25000, 50000, 75000, 100000, 150000, 200000])
    else:
        received_loan = "No"
        loan_amount = ""
    
    has_insecurity = random.choice(["Yes", "No"])
    
    if has_insecurity == "No":
        insecurity_types = ["Theft of farm produce"]  
    else:
        insecurity_types = random.sample([
            "Theft of farm produce", "Destruction of crops", "Herdsmen/farmers clashes",
             "Communal conflict"
        ], k=random.randint(1, 3))
    
    suffered_loss = random.choice(["Yes", "Yes", "No", "No", "No", "No"])
    if suffered_loss == "Yes":
        loss_value = random.choice([50000, 100000, 150000, 200000, 250000, 300000, 400000, 500000])
    else:
        loss_value = ""
    
    farm_data = generate_correlated_farm_data()
    
    hectares_lost = 0 if random.randint(1, 20) != 1 else 1
    
    if random.randint(1, 10) == 1:
        crops_discontinued = random.choice(["1", "2"])
    else:
        crops_discontinued = "0"
    
    switched_livestock = "No" if random.randint(1, 10) <= 9 else "Yes"
    
    cooperative_participation = "No" if random.randint(1, 20) <= 14 else "Yes"
    
    data = {
        # Demographics
        "lga": "Ijebu East",  # Constant as requested
        "gender": random.choice(["Male", "Female"]),
        "age": age,
        "marital_status": marital_status,
        "household_size": household_size,
        "household_dist": household_dist,
        "education": random.choice(["No formal education", "Primary", "Secondary", "Secondary", "Tertiary"]),
        
        # Farming background
        "farming_years": farming_years,
        "own_land": own_land,
        "land_acquisition": land_acquisition,
        "other_income": random.choice(["Yes", "No"]),
        "other_work": random.choice(["Civil service", "Self employed"]),
        
        # Farm details - NOW CORRELATED
        "farm_size": farm_data["farm_size"],
        "annual_income": farm_data["annual_income"],
        "farming_reason": farming_reason,
        "farmers_association": random.choice(["Yes", "No"]),
        "received_loan": received_loan,
        "loan_amount": loan_amount,
        
        # Insecurity
        "has_insecurity": has_insecurity,
        "insecurity_types": insecurity_types,
        "insecurity_frequency": random.choice(["Very often", "Often", "Sometimes", "Rarely"]),
        "safety_feeling": random.choice(["Very safe", "Safe"]),
        "police_distance": random.choice(["< 1km", "1-3km", "4-6km", "7-10km", ">10km"]),
        "hospital_time": random.choice([
            "Less than 10min", "10-20mins", "21-30mins", "31-60mins", "more than 60mins"
        ]),
        "suffered_loss": suffered_loss,
        "loss_value": loss_value,
        
        # Cropping
        "crops": random.sample(["Tubers", "Cereals", "Legumes", "Cash crops", "Vegetables"], 
                              k=random.randint(1, 3)),
        "insecurity_influenced": random.choice(["Yes", "No", "No","No"]),
        "influence_types": random.sample([
            "Switched to crops that mature faster", "Reduced farm size",
            "Avoided distant farmland", "left part of land uncultivated",
            "Practiced mixed cropping"
        ], k=random.randint(0, 2)),
        "land_change": random.choice(["Increased", "Increased", "Increased", "Increased", "Remained the same"]),
        "abandoned_land": "No",
        "abandoned_size": "",
        "affected_timing": random.choice(["Yes", "No"]),
        "cropping_system": random.choice([
            "Mono-cropping", "Mixed cropping", "Inter-cropping", "Crop rotation"
        ]),
        
        # Market
        "sold_produce": farm_data["sold_produce"],
        "total_harvest": str(farm_data["total_harvest"]),
        "amount_sold": str(farm_data["amount_sold"]),
        "sales_income": str(farm_data["sales_income"]),
        "market_affected": random.choice(["Yes", "No"]),
        "market_distance": random.choice(["<1km", "1-3km", "4-6km", "7-10km", ">10km"]),
        "market_effects": random.sample([
            "increased transport cost", "Buyers no longer come", "Fear of traveling",
            "Road blockages", "Reduced market days"
        ], k=random.randint(0, 2)),
        "selling_location": random.choice([
            "Farm gate", "Local market", "Urban market", "Through middlemen", "Cooperative"
        ]),
        
        # Additional decisions
        "hectares_lost": str(hectares_lost),
        "crops_discontinued": crops_discontinued,
        "switched_livestock": switched_livestock,
        "joined_vigilante": "No",
        "hired_security": "No",
        "diversified_non_farm": random.choice(["Yes", "No"]),
        "early_harvest": random.choice(["Yes", "No"]),
        "temp_relocation": "No",
        "financial_contribution": random.choice(["Yes", "No"]),
        "cooperative_participation": cooperative_participation,
        "received_assistance": "No",
        "assistance_when": random.choice(["A year ago", "2 years ago", "3 years ago"]),
        "security_opinion": random.choice([
            "Government support", "Community vigilante groups", "Resolution of conflicts",
            "Use of charm", "Setting of traps for thieves, herdsmen and their cattle",
            "Use of sticks for Fencing", "Grants from government to support farmers at loss", "Continuous visiting of the farm",
            "More OPC", "Reporting to CDS"
        ])
    }
    
    return data


# FORM FILLING CLASS

class FormFiller:
    def __init__(self, url, headless=False):
        self.url = url
        self.headless = headless
        self.driver = None
        self.wait = None
        
    def setup(self):
        """Initialize browser"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)
        self.driver.maximize_window()
        
    def random_wait(self, min_sec=0.5, max_sec=2):
        time.sleep(random.uniform(min_sec, max_sec))
        
    def safe_click(self, element):
        """Click with fallback"""
        try:
            element.click()
        except:
            self.driver.execute_script("arguments[0].click();", element)
    
    def scroll_to_element(self, element):
        """Scroll element into view"""
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
            element
        )
        self.random_wait(0.3, 0.7)
            
    def fill_text(self, selector, value):
        """Fill text input"""
        try:
            element = self.wait.until(EC.presence_of_element_located(selector))
            self.scroll_to_element(element)
            self.random_wait(2, 4)  
            element.clear()
            element.send_keys(str(value))
            return True
        except Exception as e:
            logger.warning(f"✗ Could not fill text: {e}")
            return False
            
    def click_radio(self, selector):
        """Click radio button"""
        try:
            element = self.wait.until(EC.element_to_be_clickable(selector))
            self.scroll_to_element(element)
            self.random_wait(2, 4)  # 5 second delay before clicking
            self.safe_click(element)
            return True
        except Exception as e:
            logger.warning(f"✗ Could not click radio: {e}")
            return False
            
    def click_checkbox(self, selector):
        """Click checkbox"""
        try:
            element = self.wait.until(EC.element_to_be_clickable(selector))
            self.scroll_to_element(element)
            self.random_wait(2, 4)  
            self.safe_click(element)
            return True
        except Exception as e:
            logger.warning(f"✗ Could not click checkbox: {e}")
            return False
    
    def handle_unsaved_record(self):
        try:
            self.random_wait(1, 2)
            
            discard_button = None
            try:
                discard_button = self.driver.find_element(
                    By.XPATH, 
                    "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'discard')]"
                )
            except:
                pass
            
            if discard_button and discard_button.is_displayed():
                logger.info("Found 'unsaved record' dialog, clicking Discard...")
                self.safe_click(discard_button)
                self.random_wait(1, 2) 
                return True
            
            return False
        except Exception as e:
            logger.debug(f"No unsaved record dialog found: {e}")
            return False
            
    def fill_complete_form(self, data):
        try:
            logger.info("="*60)
            logger.info("Starting new form submission")
            logger.info("="*60)
            
            # Navigate to form
            self.driver.get(self.url)
            self.random_wait(2, 4)
            
            # Handle unsaved record dialog if it appears
            self.handle_unsaved_record()
            





            # SECTION A: SOCIO-ECONOMIC CHARACTERISTICS
            logger.info("Section A: Demographics")
            
            # Local Government Area
            logger.info(f"Filling LGA: {data['lga']}")
            self.fill_text(
                (By.NAME, "/amw8cha2r83Vs2o7cTBSgY/Local_Government_Area"),
                data["lga"]
            )
            
            
            # Gender
            logger.info(f"Filling Gender: {data['gender']}")
            gender_value = "male" if data["gender"] == "Male" else "female"
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Gender'][@value='{gender_value}']")
            )
            
            # Age
            logger.info(f"Filling Age: {data['age']}")
            self.fill_text(
                (By.NAME, "/amw8cha2r83Vs2o7cTBSgY/How_old_are_you"),
                data["age"]
            )
            
            # Marital Status
            logger.info(f"Filling Marital Status: {data['marital_status']}")
            marital_value = data["marital_status"].lower()
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/what_is_your_marital_status'][@value='{marital_value}']")
            )
            
            # Household Size
            logger.info(f"Filling Household Size: {data['household_size']}")
            self.fill_text(
                (By.NAME, "/amw8cha2r83Vs2o7cTBSgY/How_many_people_live_in_your_household"),
                data["household_size"]
            )
            
            # HOUSEHOLD COMPOSITION (NEW)
            logger.info("Filling Household Composition")
            hh = data["household_dist"]
            
            # 0-5 years: Male, Female
            self.fill_text(
                (By.NAME, "/amw8cha2r83Vs2o7cTBSgY/group_yn3lz88_row/group_yn3lz88_row_column"),
                hh["0_5_male"]
            )
            self.fill_text(
                (By.NAME, "/amw8cha2r83Vs2o7cTBSgY/group_yn3lz88_row/group_yn3lz88_row_column_1"),
                hh["0_5_female"]
            )
            
            # 5-18 years: Male, Female
            self.fill_text(
                (By.NAME, "/amw8cha2r83Vs2o7cTBSgY/group_yn3lz88_row_1/group_yn3lz88_row_1_column"),
                hh["5_18_male"]
            )
            self.fill_text(
                (By.NAME, "/amw8cha2r83Vs2o7cTBSgY/group_yn3lz88_row_1/group_yn3lz88_row_1_column_1"),
                hh["5_18_female"]
            )
            
            # 18-60 years: Male, Female
            self.fill_text(
                (By.NAME, "/amw8cha2r83Vs2o7cTBSgY/group_yn3lz88_row_2/group_yn3lz88_row_2_column"),
                hh["18_60_male"]
            )
            self.fill_text(
                (By.NAME, "/amw8cha2r83Vs2o7cTBSgY/group_yn3lz88_row_2/group_yn3lz88_row_2_column_1"),
                hh["18_60_female"]
            )
            
            # Above 60 years: Male, Female
            self.fill_text(
                (By.NAME, "/amw8cha2r83Vs2o7cTBSgY/group_yn3lz88_row_3/group_yn3lz88_row_3_column"),
                hh["60_plus_male"]
            )
            self.fill_text(
                (By.NAME, "/amw8cha2r83Vs2o7cTBSgY/group_yn3lz88_row_3/group_yn3lz88_row_3_column_1"),
                hh["60_plus_female"]
            )
            
            # Education Level
            logger.info(f"Filling Education: {data['education']}")
            education_map = {
                "No formal education": "no_formal_education",
                "Primary": "primary",
                "Secondary": "secondary",
                "Tertiary": "tertiary"
            }
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/What_is_your_level_of_education'][@value='{education_map[data['education']]}']")
            )
            
            # Farming Years
            logger.info(f"Filling Farming Years: {data['farming_years']}")
            years_map = {
                "0-5": "0_5",
                "5-10": "5_10",
                "10-15": "10_15",
                "15 years and above": "15_years_and_above"
            }
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/How_many_years_have_you_been_farming'][@value='{years_map[data['farming_years']]}']")
            )
            
            # Own Land
            logger.info(f"Filling Own Land: {data['own_land']}")
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Do_you_own_a_land'][@value='{data['own_land'].lower()}']")
            )
            
            # Land Acquisition
            logger.info(f"Filling Land Acquisition: {data['land_acquisition']}")
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/How_did_you_acquire_your_land'][@value='{data['land_acquisition'].lower()}']")
            )
            
            # Other Income
            logger.info(f"Filling Other Income: {data['other_income']}")
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Apart_from_farming_her_source_of_income'][@value='{data['other_income'].lower()}']")
            )
            
            # Other Work (conditional)
            if data["other_income"] == "Yes":
                logger.info(f"Filling Other Work: {data['other_work']}")
                work_value = data["other_work"].lower().replace(" ", "_")
                self.click_checkbox(
                    (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/If_yes_what_other_work_do_you_do'][@value='{work_value}']")
                )
            
            # Farm Size
            logger.info(f"Filling Farm Size: {data['farm_size']}")
            size_map = {
                "<1 hectare": "_1_hectare",
                "1-2": "1_2",
                "2-5": "2_5",
                "5-10": "5_10",
                ">10": "_10"
            }
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/How_large_was_your_farm'][@value='{size_map[data['farm_size']]}']")
            )
            
            # Annual Income
            logger.info(f"Filling Annual Income: {data['annual_income']}")
            income_map = {
                "<300,000": "_300_000",
                "300,000-500,000": "300_000_500_000",
                "500,000-1,000,000": "500_000_1_000_000",
                "1,000,000- 2,000,000": "1_000_000__2_000_000",
                ">2,000,000": "_2_000_000"
            }
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/What_s_your_estimated_annual_income'][@value='{income_map[data['annual_income']]}']")
            )
            
            # Farming Reason
            logger.info(f"Filling Farming Reason: {data['farming_reason']}")
            reason_value = data["farming_reason"].lower().replace(" ", "_")
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Why_did_you_start_farming'][@value='{reason_value}']")
            )
            
            # Farmers Association
            logger.info(f"Filling Farmers Association: {data['farmers_association']}")
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Are_you_a_member_of_ation_or_cooperative'][@value='{data['farmers_association'].lower()}']")
            )
            
            # Received Loan
            logger.info(f"Filling Received Loan: {data['received_loan']}")
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Did_you_receive_any_n_the_last_12_months'][@value='{data['received_loan'].lower()}']")
            )
            
            # Loan Amount (conditional)
            if data["received_loan"] == "Yes" and data["loan_amount"]:
                logger.info(f"Filling Loan Amount: {data['loan_amount']}")
                self.fill_text(
                    (By.NAME, "/amw8cha2r83Vs2o7cTBSgY/If_yes_how_much"),
                    data["loan_amount"]
                )
            
            # SECTION B: COMMUNITY LEVEL INSECURITY
            logger.info("Section B: Insecurity")
            
            # Has Insecurity
            logger.info(f"Filling Has Insecurity: {data['has_insecurity']}")
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/In_the_past_thee_yea_es_in_your_community'][@value='{data['has_insecurity'].lower()}']")
            )
            
            # Insecurity Types
            logger.info(f"Filling Insecurity Types: {len(data['insecurity_types'])} types")
            insecurity_type_map = {
                "Theft of farm produce": "theft_of_farm_produce",
                "Destruction of crops": "destruction_of_crops",
                "Herdsmen/farmers clashes": "herdsmen_farmers_clashes",
                "Kidnapping": "kidnapping",
                "Armed robbery": "armed_robbery",
                "Communal conflict": "communal_conflict",
                "Banditry": "banditry"
            }
            for insec_type in data["insecurity_types"]:
                self.click_checkbox(
                    (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/What_type_of_insecur_rienced_or_witnessed'][@value='{insecurity_type_map[insec_type]}']")
                )
            
            # Insecurity Frequency
            logger.info(f"Filling Insecurity Frequency: {data['insecurity_frequency']}")
            freq_value = data["insecurity_frequency"].lower().replace(" ", "_")
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/How_often_do_these_i_occur_in_your_area_'][@value='{freq_value}']")
            )
            
            # Safety Feeling
            logger.info(f"Filling Safety Feeling: {data['safety_feeling']}")
            safety_value = data["safety_feeling"].lower().replace(" ", "_")
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/How_safe_do_you_feel_going_to_the_farm'][@value='{safety_value}']")
            )
            
            # Police Distance
            logger.info(f"Filling Police Distance: {data['police_distance']}")
            police_map = {
                "< 1km": "__1km",
                "1-3km": "1_3km",
                "4-6km": "4_6km",
                "7-10km": "7_10km",
                ">10km": "_10km"
            }
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/How_far_is_the_neare_station_to_your_farm'][@value='{police_map[data['police_distance']]}']")
            )
            
            # Hospital Time
            logger.info(f"Filling Hospital Time: {data['hospital_time']}")
            hospital_map = {
                "Less than 10min": "less_than_10min",
                "10-20mins": "10_20mins",
                "21-30mins": "21_30mins",
                "31-60mins": "31_60mins",
                "more than 60mins": "more_than_60mins"
            }
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/How_long_does_it_tak_the_nearest_hospital'][@value='{hospital_map[data['hospital_time']]}']")
            )
            
            # Suffered Loss
            logger.info(f"Filling Suffered Loss: {data['suffered_loss']}")
            self.click_radio(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Have_you_personally_ss_due_to_insecurity'][@value='{data['suffered_loss'].lower()}']")
            )
            
            # Loss Value (conditional)
            if data["suffered_loss"] == "Yes" and data["loss_value"]:
                logger.info(f"Filling Loss Value: {data['loss_value']}")
                self.fill_text(
                    (By.NAME, "/amw8cha2r83Vs2o7cTBSgY/If_yes_estimate_the_value_of_your_loss"),
                    data["loss_value"]
                )
            
            # SECTION C: CROPPING DECISIONS
            logger.info("Section C: Cropping Decisions")
            
            # Crops Planted
            logger.info(f"Filling Crops: {len(data['crops'])} crops")
            crop_map = {
                "Tubers": "tubers",
                "Cereals": "cereals",
                "Legumes": "legumes",
                "Cash crops": "cash_crops",
                "Vegetables": "vegetables"
            }
            for crop in data["crops"]:
                self.click_checkbox(
                    (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/what_crops_did_you_p_last_farming_season'][@value='{crop_map[crop]}']")
                )
            
            # Insecurity Influenced
            logger.info(f"Filling Insecurity Influenced: {data['insecurity_influenced']}")
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Has_insecurity_influence_your_decision'][@value='{data['insecurity_influenced'].lower()}']")
            )
            
            # Influence Types (conditional)
            if data["insecurity_influenced"] == "Yes" and data["influence_types"]:
                logger.info(f"Filling Influence Types: {len(data['influence_types'])} types")
                influence_map = {
                    "Switched to crops that mature faster": "switched_to_crops_that_mature_faster",
                    "Reduced farm size": "reduced_farm_size",
                    "Avoided distant farmland": "avoided_distant_farmland",
                    "left part of land uncultivated": "left_part_of_land_uncultivated",
                    "Practiced mixed cropping": "practiced_mixed_cropping"
                }
                for influence in data["influence_types"]:
                    self.click_checkbox(
                        (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/If_yes_how_did_it_i_luence_your_decision'][@value='{influence_map[influence]}']")
                    )
            
            # Land Change
            logger.info(f"Filling Land Change: {data['land_change']}")
            land_value = data["land_change"].lower().replace(" ", "_")
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Compared_to_previous_cultivated_land_has'][@value='{land_value}']")
            )
            
            # Abandoned Land
            logger.info(f"Filling Abandoned Land: {data['abandoned_land']}")
            self.click_radio(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Have_you_abandoned_a_ecause_of_insecurity'][@value='{data['abandoned_land'].lower()}']")
            )
            
            # Affected Timing
            logger.info(f"Filling Affected Timing: {data['affected_timing']}")
            self.click_radio(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Has_insecurity_affec_g_or_harvesting_time'][@value='{data['affected_timing'].lower()}']")
            )
            
            # Cropping System
            logger.info(f"Filling Cropping System: {data['cropping_system']}")
            system_map = {
                "Mono-cropping": "mono_cropping",
                "Mixed cropping": "option_2",
                "Inter-cropping": "inter_cropping",
                "Crop rotation": "crop_rotation"
            }
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/What_type_of_croppin_stem_do_you_practice'][@value='{system_map[data['cropping_system']]}']")
            )
            
            # SECTION D: MARKET PARTICIPATION
            logger.info("Section D: Market Participation")
            
            # Sold Produce
            logger.info(f"Filling Sold Produce: {data['sold_produce']}")
            self.click_radio(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Did_you_sell_any_of_produce_last_season'][@value='{data['sold_produce'].lower()}']")
            )
            
            # Total Harvest
            logger.info(f"Filling Total Harvest: {data['total_harvest']}")
            self.fill_text(
                (By.NAME, "/amw8cha2r83Vs2o7cTBSgY/What_was_your_total_harvest_Kg_tonnes"),
                data["total_harvest"]
            )
            
            # Amount Sold
            logger.info(f"Filling Amount Sold: {data['amount_sold']}")
            self.fill_text(
                (By.NAME, "/amw8cha2r83Vs2o7cTBSgY/How_much_did_you_sell_Kg_tonnes"),
                data["amount_sold"]
            )
            
            # Sales Income
            logger.info(f"Filling Sales Income: {data['sales_income']}")
            self.fill_text(
                (By.NAME, "/amw8cha2r83Vs2o7cTBSgY/What_was_your_total_income_from_sales_"),
                data["sales_income"]
            )
            
            # Market Affected
            logger.info(f"Filling Market Affected: {data['market_affected']}")
            self.click_radio(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Has_insecurity_affec_to_access_the_market'][@value='{data['market_affected'].lower()}']")
            )
            
            # Market Distance
            logger.info(f"Filling Market Distance: {data['market_distance']}")
            market_dist_map = {
                "<1km": "_1km",
                "1-3km": "1_3km",
                "4-6km": "4_6km",
                "7-10km": "7_10km",
                ">10km": "_10km"
            }
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/How_far_is_the_neare_from_your_farm_Km'][@value='{market_dist_map[data['market_distance']]}']")
            )
            
            # Market Effects (conditional)
            if data["market_affected"] == "Yes" and data["market_effects"]:
                logger.info(f"Filling Market Effects: {len(data['market_effects'])} effects")
                effect_map = {
                    "increased transport cost": "increased_transport_cost",
                    "Buyers no longer come": "buyers_no_longer_come",
                    "Fear of traveling": "fear_of_traveling",
                    "Road blockages": "road_blockages",
                    "Reduced market days": "reduced_market_days"
                }
                for effect in data["market_effects"]:
                    self.click_checkbox(
                        (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/If_yes_how'][@value='{effect_map[effect]}']")
                    )
            
            # Selling Location
            logger.info(f"Filling Selling Location: {data['selling_location']}")
            location_value = data["selling_location"].lower().replace(" ", "_")
            self.click_checkbox(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Where_do_you_mostly_sell_your_produce'][@value='{location_value}']")
            )
            
            # SECTION E: CROPPING DECISION (Additional)
            logger.info("Section E: Additional Decisions")
            
            # Hectares Lost
            logger.info(f"Filling Hectares Lost: {data['hectares_lost']}")
            self.fill_text(
                (By.NAME, "/amw8cha2r83Vs2o7cTBSgY/How_many_hectares_of_u_lost_to_insecurity"),
                data["hectares_lost"]
            )
            
            # Crops Discontinued
            logger.info(f"Filling Crops Discontinued: {data['crops_discontinued']}")
            self.fill_text(
                (By.NAME, "/amw8cha2r83Vs2o7cTBSgY/How_many_crop_types_ed_due_to_insecurity"),
                data["crops_discontinued"]
            )
            
            # Switched to Livestock
            logger.info(f"Filling Switched Livestock: {data['switched_livestock']}")
            self.click_radio(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Did_you_switch_enter_ecause_of_insecurity'][@value='{data['switched_livestock'].lower()}']")
            )
            
            # Joined Vigilante
            logger.info(f"Filling Joined Vigilante: {data['joined_vigilante']}")
            self.click_radio(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Did_you_join_vigilan_group_of_insecurity'][@value='{data['joined_vigilante'].lower()}']")
            )
            
            # Hired Security
            logger.info(f"Filling Hired Security: {data['hired_security']}")
            self.click_radio(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Did_you_hire_any_pri_ecause_of_insecurity'][@value='{data['hired_security'].lower()}']")
            )
            
            # Diversified Non-Farm
            logger.info(f"Filling Diversified Non-Farm: {data['diversified_non_farm']}")
            self.click_radio(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Did_you_diversify_in_ecause_of_insecurity'][@value='{data['diversified_non_farm'].lower()}']")
            )
            
            # Early Harvest
            logger.info(f"Filling Early Harvest: {data['early_harvest']}")
            self.click_radio(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Did_you_harvest_earl_ecause_of_insecurity'][@value='{data['early_harvest'].lower()}']")
            )
            
            # Temporary Relocation
            logger.info(f"Filling Temp Relocation: {data['temp_relocation']}")
            self.click_radio(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Did_you_relocate_tem_ecause_of_insecurity'][@value='{data['temp_relocation'].lower()}']")
            )
            
            # Financial Contribution
            logger.info(f"Filling Financial Contribution: {data['financial_contribution']}")
            self.click_radio(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Did_you_contribute_f_ity_security_efforts'][@value='{data['financial_contribution'].lower()}']")
            )
            
            # Cooperative Participation
            logger.info(f"Filling Cooperative Participation: {data['cooperative_participation']}")
            self.click_radio(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Do_you_participate_i_rotection_or_support'][@value='{data['cooperative_participation'].lower()}']")
            )
            
            # Received Assistance
            logger.info(f"Filling Received Assistance: {data['received_assistance']}")
            self.click_radio(
                (By.XPATH, f"//input[@name='/amw8cha2r83Vs2o7cTBSgY/Have_you_received_an_to_manage_insecurity'][@value='{data['received_assistance'].lower()}']")
            )
            
            # Security Opinion
            logger.info(f"Filling Security Opinion")
            self.fill_text(
                (By.NAME, "/amw8cha2r83Vs2o7cTBSgY/In_your_opinion_wha_farmers_in_your_area"),
                data["security_opinion"]
            )
            
            # SUBMIT THE FORM

            logger.info("Submitting form...")
            self.random_wait(1, 2)
            
            # Find and click submit button
            submit_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' or contains(@class, 'btn-primary')]"))
            )
            self.scroll_to_element(submit_button)
            self.safe_click(submit_button)
            
            self.random_wait(2, 4)
            
            logger.info("✓ Form submission completed successfully!")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Error filling form: {e}")
            # Save screenshot for debugging
            try:
                screenshot_name = f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.driver.save_screenshot(screenshot_name)
                logger.info(f"Screenshot saved: {screenshot_name}")
            except:
                pass
            return False
            
    def close_driver(self):
        """Close browser"""
        if self.driver:
            self.driver.quit() 


# MAIN AUTOMATION LOOP

def run_automation():
    """Run the complete automation"""
    
    print("\n" + "="*60)
    print("KOBOTOOLBOX AUTOMATION")
    print("="*60)
    print(f"Form: {FORM_URL}")
    print(f"Responses: {NUM_RESPONSES}")
    print(f"Duration: {DURATION_HOURS} hours")
    print(f"Headless: {HEADLESS}")
    print("="*60 + "\n")
    
    # Confirmation
    if NUM_RESPONSES > 5:
        response = input(f"⚠️  Submit {NUM_RESPONSES} responses? Type 'yes' to continue: ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
    
    # Calculate delay between submissions
    total_seconds = DURATION_HOURS * 2600
    delay_between = total_seconds / NUM_RESPONSES if NUM_RESPONSES > 1 else 0
    
    logger.info(f"Average delay between submissions: {delay_between/200:.1f} minutes")
    
    start_time = datetime.now()
    successful = 0
    failed = 0
    
    for i in range(NUM_RESPONSES):
        logger.info(f"\n{'='*60}")
        logger.info(f"Response {i+1} of {NUM_RESPONSES}")
        logger.info(f"{'='*60}")
        
        # CREATE NEW BROWSER FOR EACH SUBMISSION
        filler = FormFiller(FORM_URL, headless=HEADLESS)
        
        try:
            # Setup browser
            filler.setup()
            
            # Generate data
            data = generate_farmer_data()
            
            # Fill form
            success = filler.fill_complete_form(data)
            
            if success:
                successful += 1
            else:
                failed += 1
                
        except Exception as e:
            logger.error(f"Error in submission {i+1}: {e}")
            failed += 1
        finally:
            # ALWAYS CLOSE BROWSER AFTER EACH SUBMISSION
            filler.close_driver()
            logger.info("Browser closed")
        
        # Wait before next submission (except for last one)
        if i < NUM_RESPONSES - 1:
            variation = random.uniform(0.2, 0.3)
            wait_time = delay_between * variation
            
            logger.info(f"\nWaiting {wait_time/60:.1f} minutes before next submission...")
            time.sleep(wait_time)
            
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 3600
    
    print("\n" + "="*60)
    print("AUTOMATION COMPLETE!")
    print("="*60)
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total time: {duration:.2f} hours")
    print(f"Average time per response: {(duration*60)/NUM_RESPONSES:.1f} minutes")
    print("="*60 + "\n")
            
if __name__ == "__main__":
    try:
        run_automation()
    except KeyboardInterrupt:
        logger.info("\n\nInterrupted by user")
    except Exception as e:
        logger.error(f"\n\nCritical error: {e}")