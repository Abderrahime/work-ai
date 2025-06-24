import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException



def initialize_browser(headless=False, logger=None):
    """Initialize browser with options"""
    if logger:
        logger.info("Initializing browser")
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Firefox(options=options)
    driver.get("https://www.free-work.com/fr/tech-it")
    return driver


def check_and_click_login(driver, logger):
    """Check if already logged in and click login if needed"""
    try:
        login_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//a[contains(@class, 'btn--light') and contains(., 'Connexion')]"
            ))
        )
        logged_in_elements = driver.find_elements(By.CSS_SELECTOR, ".user-profile-indicator")
        if not logged_in_elements:
            login_button.click()
            logger.info("Login button clicked")
        else:
            logger.info("Already logged in")
        return True
    except Exception as e:
        logger.error(f"Login check failed: {e}")
        return False


def perform_login(driver, email, password, logger):
    """Perform login with credentials and check for error messages"""
    try:
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_field.send_keys(email)
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(password)
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit' and contains(., 'Se connecter')]")
        submit_button.click()
        time.sleep(5)

        # Check for login error message
        try:
            error_element = driver.find_element(By.XPATH, "//*[contains(text(), 'incorrect') or contains(text(), 'Identifiants') or contains(text(), 'erreur') or contains(text(), 'invalide')]")
            if error_element.is_displayed():
                logger.error("Login failed: Incorrect credentials or error message detected on page.")
                return False
        except Exception:
            pass  # No error message found

        # Check if user profile indicator is present (logged in)
        logged_in_elements = driver.find_elements(By.CSS_SELECTOR, "#user-menu")
        if logged_in_elements:
            logger.success("Login successful")
            return True
        else:
            logger.error("Login failed: User menu not found after login.")
            return False
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return False


def perform_search(driver, search_term, logger):
    """Perform search with given term"""
    try:
        search_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "query")))
        search_field.clear()
        search_field.send_keys(search_term)
        search_field.send_keys(Keys.RETURN)
        time.sleep(3)
        logger.info(f"Search performed for: {search_term}")
        return True
    except Exception as e:
        logger.error(f"Search failed for {search_term}: {e}")
        return False


def _apply_filter(driver, logger, filter_id, option_type, option_values):
    """
    A generic function to apply a filter.
    
    :param driver: The Selenium WebDriver.
    :param logger: The logger instance.
    :param filter_id: The ID of the main filter button (e.g., 'contracts', 'remote').
    :param option_type: The type of input ('checkbox' or 'radio').
    :param option_values: A list of values to select.
    """
    try:
        # 1. Click on the main filter button to open the pop-up
        filter_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, filter_id))
        )
        filter_button.click()
        logger.info(f"Opened '{filter_id}' filter pop-up.")
        time.sleep(1)  # Wait for animation

        # 2. Find the filter pop-up that is now visible
        filter_popup = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'tippy-box') and @data-state='visible']"))
        )

        # 3. Click "Réinitialiser" INSIDE the pop-up (if it exists)
        try:
            reset_button = filter_popup.find_element(By.XPATH, ".//button[@type='reset' and contains(., 'Réinitialiser')]")
            reset_button.click()
            logger.info(f"Reset '{filter_id}' filters.")
            time.sleep(0.5)  # Wait for reset to apply

            # After reset, the pop-up closes, so we need to click the filter button again
            filter_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, filter_id))
            )
            filter_button.click()
            logger.info(f"Reopened '{filter_id}' filter pop-up after reset.")
            time.sleep(1)  # Wait for animation

            # Re-find the pop-up to avoid stale element reference after reset
            filter_popup = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'tippy-box') and @data-state='visible']"))
            )
            logger.info("Refreshed filter pop-up context after reset.")

        except Exception:
            logger.warning(f"No 'Réinitialiser' button found for '{filter_id}'.")
        
        # 4. Select the desired options INSIDE the pop-up
        for value in option_values:
            try:
                # Debug: List all available radio buttons for publication date filter
                if filter_id == "freshness":
                    all_radio_buttons = filter_popup.find_elements(By.XPATH, ".//input[@type='radio']")
                    logger.info(f"Available radio button values in '{filter_id}' filter:")
                    for radio in all_radio_buttons:
                        radio_value = radio.get_attribute('value')
                        radio_id = radio.get_attribute('id')
                        logger.info(f"  - value: '{radio_value}', id: '{radio_id}'")
                
                # Find the input element (checkbox or radio) by its name and value
                input_element = filter_popup.find_element(
                    By.XPATH, f".//input[@type='{option_type}' and @value='{value}']"
                )
                if not input_element.is_selected():
                    # Use JS click for reliability
                    driver.execute_script("arguments[0].click();", input_element)
                    logger.info(f"Selected '{value}' in '{filter_id}' filter.")
            except Exception as e:
                logger.warning(f"Option '{value}' for '{filter_id}' not found or clickable: {e}")
        
        # 5. Click the "Appliquer" button INSIDE the pop-up
        apply_button = filter_popup.find_element(By.XPATH, ".//button[contains(., 'Appliquer')]")
        apply_button.click()
        logger.info(f"Applied '{filter_id}' filter.")
        time.sleep(2)
        return True
    except Exception as e:
        logger.error(f"Filter operation failed for '{filter_id}': {e}")
        # Save the page source for debugging
        with open(f"{filter_id}_filter_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logger.info(f"Saved current page to {filter_id}_filter_debug.html for inspection.")
        return False


def filter_contract_types(driver, contract_types, logger):
    """Filter by contract types using the generic filter function."""
    logger.info(f"Filtering by contract types: {contract_types}")
    if not contract_types:
        return True
    return _apply_filter(driver, logger, "contracts", "checkbox", contract_types)


def filter_remote_work(driver, remote_types, logger):
    """Filter by remote work types using the generic filter function."""
    logger.info(f"Filtering by remote types: {remote_types}")
    if not remote_types:
        return True
    return _apply_filter(driver, logger, "remote", "checkbox", remote_types)


def filter_publication_date(driver, timeframe, logger):
    """Filter by publication date using the generic filter function."""
    logger.info(f"Filtering by publication date: {timeframe}")
    if not timeframe:
        return True
    # The timeframe is a single value, so we pass it in a list
    return _apply_filter(driver, logger, "freshness", "radio", [timeframe])


def check_if_already_applied(driver):
    """Check if already applied to this job"""
    try:
        return len(driver.find_elements(By.XPATH, "//h3[contains(text(), 'Vous avez postulé')]")) > 0
    except:
        return False


def submit_application(driver, message, logger):
    """Submit application with custom message"""
    try:
        textarea = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "job-application-message")))
        textarea.clear()
        textarea.send_keys(message)
        submit = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Je postule')]")))
        driver.execute_script("arguments[0].click();", submit)
        time.sleep(2)
        
        try:
            confirm = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Confirmer candidature')]")))
            confirm.click()
            time.sleep(2)
        except:
            pass
        
        logger.success("Application submitted successfully")
        return True
    except Exception as e:
        logger.error(f"Application failed: {e}")
        return False


def check_job_content(driver, excluded_keywords, logger, search_term, search_config):
    """Check job content and apply if suitable"""
    main = driver.current_window_handle
    windows = driver.window_handles
    
    try:
        for window in windows[1:]:  # Skip main window
            driver.switch_to.window(window)
            
            try:
                # Check if already applied
                if check_if_already_applied(driver):
                    logger.info("Already applied to this job - skipping")
                    driver.close()
                    continue
                
                # Get job content
                content = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "prose-content"))
                )
                
                # Check for excluded keywords
                content_text = content.text.lower()
                if any(keyword in content_text for keyword in excluded_keywords):
                    logger.info(f"Job contains excluded keyword - skipping")
                    driver.close()
                    continue
                
                # Get job title and company for logging
                try:
                    job_title = driver.find_element(By.XPATH, "//h1").text
                    company = driver.find_element(By.XPATH, "//span[contains(@class, 'company')]").text
                except:
                    job_title = "Unknown"
                    company = "Unknown"
                
                # Submit application
                success = submit_application(driver, search_config['application_message'], logger)
                
                # Log application attempt
                logger.application_log(job_title, company, "success" if success else "failed", search_term)
                
                # Return application data for statistics
                return {
                    'job_title': job_title,
                    'company': company,
                    'status': "success" if success else "failed",
                    'timestamp': datetime.now().isoformat(),
                    'search_term': search_term,
                    'contract_type': search_config.get('contract_types', []),
                    'remote_type': search_config.get('remote_types', [])
                }
                
                driver.close()
            except Exception as e:
                logger.error(f"Error processing job: {e}")
                driver.close()
                
        driver.switch_to.window(main)
        return None
    except Exception as e:
        logger.error(f"Error checking job content: {e}")
        return None


def open_search_results_with_pagination(driver, max_applications, excluded_keywords, logger, search_term, search_config):
    """Open search results with pagination and apply to jobs"""
    applications_count = 0
    applications_data = []
    
    try:
        while True and applications_count < max_applications:
            links = driver.find_elements(By.XPATH, "//h2[contains(@class, 'font-semibold')]//a[contains(@href, '/fr/tech-it/')]")
            
            for link in links[:16]:  # Process up to 16 jobs per page
                if applications_count >= max_applications:
                    break
                    
                url = link.get_attribute("href")
                driver.execute_script(f"window.open('{url}', '_blank');")
                time.sleep(1)
            
            # Process applications and collect data
            application_data = check_job_content(driver, excluded_keywords, logger, search_term, search_config)
            if application_data:
                applications_data.append(application_data)
                applications_count += 1
            
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Suivant')]")))
                next_button.click()
                time.sleep(3)
            except TimeoutException:
                logger.info("No more pages to process")
                break
                
        return applications_data
    except Exception as e:
        logger.error(f"Pagination failed: {e}")
        return applications_data


def run_search_session(driver, search_term, search_config, logger, config_manager):
    """Run a complete search session for one search term"""
    logger.info(f"Starting search session for: {search_term}")
    
    # Perform search
    if not perform_search(driver, search_term, logger):
        return False, []
    
    # Apply filters
    if not filter_contract_types(driver, search_config['contract_types'], logger):
        return False, []
    
    if not filter_remote_work(driver, search_config['remote_types'], logger):
        return False, []
    
    # Ensure publication_timeframes is always a list
    ptf = search_config['publication_timeframes']
    if isinstance(ptf, str):
        ptf = [ptf]
    if not filter_publication_date(driver, ptf[0], logger):
        return False, []
    
    # Process results and collect statistics
    session_applications = open_search_results_with_pagination(
        driver, 
        search_config['max_applications_per_session'],
        search_config['excluded_keywords'],
        logger,
        search_term,
        search_config
    )
    
    return True, session_applications


def main(email=None, password=None, search_config=None, config_manager=None, logger=None):
    """Main function with enhanced parameters"""
    # Initialize components if not provided
    if config_manager is None:
        from config import SecureConfig
        config_manager = SecureConfig()
    
    if logger is None:
        from logger import SecureLogger
        logger = SecureLogger(email)
    
    if email is None or password is None:
        email, password = config_manager.load_credentials()
        if not email or not password:
            logger.error("No credentials found. Please run the interface first.")
            return
    
    if search_config is None:
        search_config = config_manager.load_search_config()
    
    # Initialize statistics
    all_applications = []
    session_stats = {
        'total_applications': 0,
        'successful_applications': 0,
        'failed_applications': 0,
        'sessions': [],
        'last_session': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Log session start
    logger.session_start(search_config)
    
    try:
        driver = initialize_browser()
        
        # Login
        if not check_and_click_login(driver, logger):
            logger.error("Could not find or click the login button. Stopping application.")
            driver.quit()
            return
        
        if not perform_login(driver, email, password, logger):
            logger.error("Login failed. Please check your credentials. Stopping application.")
            driver.quit()
            return
        
        # Process each search term
        for search_term in search_config['search_terms']:
            logger.info(f"Processing search term: {search_term}")
            
            # Navigate back to main page for each search
            driver.get("https://www.free-work.com/fr/tech-it")
            time.sleep(2)
            
            # Run search session
            success, session_applications = run_search_session(driver, search_term, search_config, logger, config_manager)
            
            if success:
                all_applications.extend(session_applications)
                logger.success(f"Completed search session for: {search_term}")
            else:
                logger.error(f"Failed search session for: {search_term}")
            
            # Add random delay between search terms
            time.sleep(random.uniform(3, 7))
        
        # Calculate final statistics
        session_stats['total_applications'] = len(all_applications)
        session_stats['successful_applications'] = len([app for app in all_applications if app['status'] == 'success'])
        session_stats['failed_applications'] = len([app for app in all_applications if app['status'] == 'failed'])
        
        # Create session record
        session_record = {
            'session_id': f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'date': datetime.now().isoformat(),
            'applications': all_applications,
            'total': session_stats['total_applications'],
            'successful': session_stats['successful_applications'],
            'failed': session_stats['failed_applications'],
            'success_rate': (session_stats['successful_applications'] / session_stats['total_applications'] * 100) if session_stats['total_applications'] > 0 else 0.0
        }
        
        session_stats['sessions'] = [session_record]
        
        # Save statistics
        config_manager.save_statistics(email, session_stats)
        
        # Log session end
        logger.session_end(session_stats)
        
        logger.success("All search sessions completed successfully!")
        
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass


if __name__ == "__main__":
    # Run the interface instead of direct execution
    from interface import FreeWorkInterface
    app = FreeWorkInterface()
    app.run()
