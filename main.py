from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException, ElementNotInteractableException
import time
import pickle
import csv
import os

# Initialize WebDriver
options = Options()
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

url = "https://pro.napaprolink.com"
csv_file = "data/product_details.csv"

try:
    # Open the URL
    driver.get(url)
    time.sleep(5)

    # Log in to the site
    try:
        username_field = driver.find_element(By.ID, "j_usernamehomepage")
        username_field.send_keys("LarrysProlink")

        password_field = driver.find_element(By.ID, "j_passwordhomepage")
        password_field.send_keys("^Waialae96816$")

        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'SUBMIT')]")
        login_button.click()
        time.sleep(3)

    except NoSuchElementException as e:
        print(f"Error during login: {e}")
        driver.quit()

    # Save session cookies
    try:
        with open("data/cookies.pkl", "wb") as cookies_file:
            pickle.dump(driver.get_cookies(), cookies_file)
    except Exception as e:
        print(f"Error saving cookies: {e}")

    # Select year
    try:
        print(f"Selecting year: 2016")
        year_dropdown = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "plkvhomevehicleYear-selector"))
        )
        year_dropdown.click()
        time.sleep(2)

        year_option = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//li[@data-attr='2017']"))
        )
        year_option.click()
        time.sleep(2)

    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error selecting year: {e}")

    # Select make
    try:
        print(f"Selecting make: Toyota")
        try:
            cookie_accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            cookie_accept_button.click()
            time.sleep(2)
        except (TimeoutException, NoSuchElementException):
            print("Cookie consent button not found or already accepted.")

        make_dropdown = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "plkvhomevehicleMake-selector"))
        )
        make_dropdown.click()
        time.sleep(2)

        make_option = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//li[div[text()='Toyota']]"))
        )
        make_option.click()
        time.sleep(2)

    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error selecting make: {e}")

    # Define the models you're interested in for Toyota 2016
    # Model to be revisited :  ,  '86', '4Runner', 'Avalon', 'Avanza **',
              
    models = ['Camry', 'Corolla', 'Hiace **', 'Highlander', 'Hilux **', 'Land Cruiser', 'Mirai', 'Prius', 'Prius Prime', 'Prius V', 'Prius c' 'Rav4', 
              'Sequoia', 'Sienna', 'Tacoma', 'Tundra', 'Yaris']
    
    all_product_data = [] 

    for model in models:
        try:
            print(f"Selecting model: {model}")

            # Click the model dropdown and select the model
            model_dropdown = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, "plkvhomevehicleModel-selector"))
            )
            model_dropdown.click()

            model_option = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//li[div[text()='{model}']]"))
            )
            model_option.click()
            time.sleep(2)

            # Fetch and select available engines for the selected model
            try:
                print("Attempting to fetch engines...")
                # engine_dropdown = WebDriverWait(driver, 20).until(
                #     EC.element_to_be_clickable((By.ID, "plkvhomevehicleEngine-selector"))
                # )
                # engine_dropdown.click()

                engine_options = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.XPATH, f"//div[@id='plkvhomevehicleEngine-selector']//li"))
                )
                engines = [option.text for option in engine_options if option.text]
                print(f"Available engines: {engines}")
                
               
                if len(engine_options)==1:
                    time.sleep(2)
                    pass
                else:                    
                    try:
                        print(f"Selecting engine .....")
                        engine_options[-1].click()
                        time.sleep(2)
                    except (TimeoutException, NoSuchElementException, ElementNotInteractableException) as e:
                        print(f"Error selecting engine : {str(e)}")
                        continue

                # Check Quick Pick Search checkboxes
                try:
                    quick_pick_checkboxes = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "plkw-facet-checkmark"))
                    )
                    for checkbox in quick_pick_checkboxes:
                        if not checkbox.is_selected():
                            checkbox.click()
                except (TimeoutException, NoSuchElementException) as e:
                    print(f"Error with Quick Pick Search checkboxes: {e}")

                # Submit the search form or click the search button
                try:
                    search_button = driver.find_element(By.CLASS_NAME, "search-filters")
                    search_button.click()
                except NoSuchElementException as e:
                    print(f"Error clicking search button: {e}")

                # Process products
                try:
                    multisearch_buttons = driver.find_elements(By.CLASS_NAME, "plk-quickpick-multisearchplpbutton")
                    time.sleep(2)
                    print(f"✅ Categories are : {multisearch_buttons} ")
                    print(f"Categories number:{len(multisearch_buttons)}")
                    

                    for button_index in range(14, len(multisearch_buttons)):           
                        multisearch_buttons = driver.find_elements(By.CLASS_NAME, "plk-quickpick-multisearchplpbutton")
                        button = multisearch_buttons[button_index]               

                        button_text = button.text.strip()
                        if not button_text:
                            button_text = button.get_attribute("textContent").strip()
                        try:
                            print(f"Clicking button {button_index}: {button_text}")
                            
                            # Scroll into view and click
                            driver.execute_script("arguments[0].scrollIntoView(true);", button)
                            time.sleep(1)  # Allow scroll time
                            
                            # Attempt to click with retries
                            retries = 3
                            for attempt in range(retries):
                                try:
                                    button.click()
                                    print(f"Clicked button {button_index} on attempt {attempt + 1}")
                                    break
                                except ElementNotInteractableException:
                                    print(f"Attempt {attempt + 1} failed, retrying...")
                                    time.sleep(2)
                        except Exception as e:
                            print(f"Error clicking button: {e}")

                        # After clicking the button, process the first page of results
                        try:
                            product_list = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "geo-search-results-collections"))
                            )
                            print("Processing product list...")

                        except TimeoutException:
                            print("No product list found, moving to next button.")
                            continue

                        # Loop for pagination
                        while True:
                            try:
                                # Extract product items on the current page
                                product_items = product_list.find_elements(By.XPATH, "//geo-product-list-item")
                                product_ids = [item.get_attribute('id') for item in product_items]
                                print("Collected Product IDs:", product_ids)

                                # Process each product on the current page
                                for product_id in product_ids:
                                    try:
                                        item = WebDriverWait(driver, 10).until(
                                            EC.presence_of_element_located((By.XPATH, f"//geo-product-list-item[@id='{product_id}']"))
                                        )
                                        product_link = item.find_element(By.CLASS_NAME, 'plp-product-title-text')
                                        product_title = product_link.text

                                        product_texts = driver.find_elements(By.CLASS_NAME, "plp-product-sub-texts")

                                        try:
                                            part_number = product_texts[0].text
                                        except Exception:
                                            part_number = "N/A"

                                        try:
                                            brand = product_texts[1].text
                                        except Exception:
                                            brand = "N/A"

                                        product_link.click()
                                        time.sleep(3)

                                        try:
                                            cost_pricing = driver.find_element(By.CLASS_NAME, "geo-price-pod-cost-amount").text
                                        except NoSuchElementException:
                                            cost_pricing = "N/A"

                                        try:
                                            list_pricing = driver.find_element(By.CLASS_NAME, "geo-price-pod-list-amount").text
                                        except NoSuchElementException:
                                            list_pricing = "N/A"

                                        # Extract specifications
                                        specifications_elements = driver.find_elements(By.CLASS_NAME, "geo-product-spec-block")
                                        specifications = {}
                                        for element in specifications_elements:
                                            try:
                                                spec_name = element.find_element(By.XPATH, ".//div[@class='geo-product-spec-label']").text
                                                spec_value = element.find_element(By.XPATH, ".//div[@class='geo-product-spec-text']").text
                                                specifications[spec_name] = spec_value
                                            except NoSuchElementException:
                                                specifications[spec_name] = "N/A"

                                        # Extract features and benefits
                                        features_and_benefits_elements = driver.find_elements(By.CLASS_NAME, "geo-feature-sub-desc-li")
                                        features_and_benefits = []
                                        for feature in features_and_benefits_elements:
                                            feature_text = feature.text.strip()
                                            if feature_text:
                                                features_and_benefits.append(feature_text)
                                        if not features_and_benefits:
                                            features_and_benefits = ["N/A"]

                                        # Add the collected data to the CSV file
                                        with open(csv_file, 'a', newline='', encoding='utf-8') as csvfile:
                                            fieldnames = ["Year", "Make", "Model", "Category", "Product Title", "Part Number", "Brand", "Cost_Price(Each)", "List_Price(Each)", "Specifications", "Features and Benefits"]
                                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                            writer.writerow({
                                                "Year": 2017,
                                                "Make": "Toyota",
                                                "Model": model,
                                                "Category": button_text,
                                                "Product Title": product_title,
                                                "Part Number": part_number,
                                                "Brand": brand,
                                                "Cost_Price(Each)": cost_pricing,
                                                "List_Price(Each)": list_pricing,
                                                "Specifications": specifications,
                                                "Features and Benefits": features_and_benefits
                                            })

                                        # Go back to the search results page for the next product
                                        driver.back()
                                        time.sleep(5)

                                    except StaleElementReferenceException as e:
                                        print(f"Retrying due to stale element reference: {e}")
                                        continue

                                # Check for the pagination link and click if it exists
                                try:
                                    pagination_link = WebDriverWait(driver, 5).until(
                                        EC.element_to_be_clickable((By.CLASS_NAME, "geo-plp-pagination-link"))
                                    )
                                    pagination_link.click()  # Click to go to the next page
                                    time.sleep(3)
                                    print("Navigating to next page of results...")

                                except (TimeoutException, NoSuchElementException):
                                    print("No more pages to paginate.")
                                    break  # Exit the loop if no more pagination is available

                            except Exception as e:
                                print(f"Error processing pagination: {e}")
                                break

                    # Go back to the vehicle selection page for the next engine
                    driver.back()
                    time.sleep(5)

                except (TimeoutException, NoSuchElementException) as e:
                    print(f"Error processing products: {e}")
                    continue

            except (TimeoutException, NoSuchElementException) as e:
                print(f"Error fetching engines for model {model}: {str(e)}")
                continue

        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error selecting model {model}: {e}")
            continue

except Exception as e:
    print(f"An unexpected error occurred: {e}")

finally:
    time.sleep(10)
    driver.quit()
