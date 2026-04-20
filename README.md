# KoboToolbox Form Automation


## Prerequisites

### 1. Install Python 3.7+
Make sure you have Python 3.7 or higher installed:
```bash
python3 --version
```

### 2. Install Chrome Browser
Download and install Google Chrome from: https://www.google.com/chrome/

### 3. Install ChromeDriver
 Automatic (recommended):
```bash
pip install webdriver-manager
```

## Installation

1. Install required Python packages:
```bash
pip install -r requirements.txt
```

## Setup Instructions

### Step 1: Inspect Your Form

Before running the automation, you need to identify the correct field selectors:

```bash
python3 form_inspector.py
```

This will:
- Open the form in a browser
- Print all field information (names, IDs, types)
- Save the HTML to `form_html.txt`
- Keep the browser open for 60 seconds for manual inspection



### Step 2: Update Field Selectors

Open `ready_to_use_automation.py` and update the `fill_form()` method with the actual field selectors from your inspection.

**Example mappings:**

```python
# Example for text input
self.fill_text_input(By.NAME, "field_name_here", demo_data["age"])

# Example for radio button
self.click_element(By.XPATH, f"//input[@name='gender'][@value='Male']")

# Example for checkbox
self.click_element(By.XPATH, f"//input[@name='crops'][@value='Tubers']")

# Example for dropdown
self.click_element(By.XPATH, "//select[@name='education']/option[@value='Secondary']")
```

### Step 3: Configure and Run

Edit the configuration in `ready_to_use_automation.py`:

```python
NUM_RESPONSES = 20     # Number of responses to submit
DURATION_HOURS = 2     # Duration to spread responses over
HEADLESS = False       # True = no browser window, False = visible
```

Run the automation:
```bash
python3 kobotoolbox_automation.py
```

## Data Generation Logic


### Demographics
- **LGA**: Alternates 
- **Gender**: Random Male/Female
- **Age**: Random 23-65 years
- **Marital Status**: Random (Single, Married, Divorced, Widowed)
- **Household Size**: Random 1-10 people
- **Education**: Random (No formal, Primary, Secondary, Tertiary)

### Farming Information
- **Farming Years**: Random distribution
- **Land Size**: Varied farm sizes
- **Income**: Random income brackets
- **Crops**: Random combinations (Tubers, Cereals, Legumes, Cash crops, Vegetables)

### Insecurity Data
- **Insecurity Types**: 1-3 random types
- **Frequency**: Varied (Very often, Often, Sometimes, Rarely)
- **Safety Feelings**: Random responses
- **Loss Values**: Random 50,000-500,000 Naira

### Market Data
- **Harvest/Sales**: Realistic quantities
- **Income**: Random 50,000-1,500,000 Naira
- **Market Distance**: Random distances
- **Selling Location**: Varied (Farm gate, Local market, etc.)

## Timing Strategy

The script distributes submissions evenly over the specified duration:

- **20 responses over 2 hours** = ~6 minutes between submissions
- Adds ±20% random variation to avoid patterns
- Includes human-like delays between field fills

## Troubleshooting

### ChromeDriver Issues
```bash
# If you get ChromeDriver errors, try:
pip install webdriver-manager --upgrade
```

### Element Not Found Errors
- Run `form_inspector.py` again
- Check if form structure has changed
- Verify selectors in the automation script

### Form Submission Fails
- Check if form has rate limiting
- Verify network connection
- Ensure form URL is correct
- Try with `HEADLESS = False` to see what's happening

### Timeout Errors
- Increase wait times in the script
- Check internet connection
- Verify form is accessible

## Customization

### Adjust Data Patterns

Edit the `generate_*_data()` methods to modify:
- Response distributions
- Value ranges
- Selection probabilities

Example:
```python
# Make more farmers have secondary education
"education": random.choices(
    ["No formal education", "Primary", "Secondary", "Tertiary"],
    weights=[10, 20, 50, 20]  # 50% secondary
)[0]
```

### Change Submission Speed

```python
# Faster (10 responses in 30 minutes)
NUM_RESPONSES = 10
DURATION_HOURS = 0.5

# Slower (20 responses in 4 hours)
NUM_RESPONSES = 20
DURATION_HOURS = 4
```

### Add More Variation

Modify `random_delay()` calls:
```python
self.random_delay(2, 5)  
```



## Form Field Mapping Guide

Since each KoboToolbox form is unique, here's how to map your fields:

### Text Inputs (age, household size, etc.)
```python
self.fill_text_input(By.NAME, "question_name", value)
```

### Radio Buttons (gender, yes/no questions)
```python
self.click_element(By.XPATH, f"//input[@name='question_name'][@value='option_value']")
```

### Checkboxes (multi-select like crop types)
```python
for crop in crops_list:
    self.click_element(By.XPATH, f"//input[@name='crops'][@value='{crop}']")
```

### Dropdowns
```python
self.click_element(By.XPATH, "//select[@name='question_name']")
self.click_element(By.XPATH, f"//select[@name='question_name']/option[text()='option_text']")
```

### Text Areas (open-ended questions)
```python
self.fill_text_input(By.NAME, "opinion", data["security_suggestion"])
```

## Next Button Navigation

Many Kobo forms are multi-page. Add navigation:

```python
# After each section
self.click_element(By.XPATH, "//button[contains(text(), 'Next')]")
self.random_delay(1, 2)
```

## Support

For issues or questions:
1. Check the console output for error messages
2. Try running with `HEADLESS = False` to see what's happening
3. Verify field selectors match the form structure

## Safety & Ethics

- This script is for your personal form testing only
- Do not use on forms you don't own
- Respect rate limits and server resources
- Ensure data generated is appropriate for your use case


