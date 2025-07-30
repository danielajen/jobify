from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import re
from config import config
from backend.database.models import db, ApplicationError, UserProfile
from datetime import datetime
from flask import current_app

class AutoApplier:
    COMMON_QUESTIONS = {
        "authorized to work": "Yes",
        "work authorization": "Authorized",
        "visa sponsorship": "No",
        "legally eligible": "Yes",
        "require sponsorship": "No",
        "work eligibility": "Authorized"
    }

    WORKDAY_SWE_FIELDS = {
        "years of experience": "3",
        "programming languages": "Python, JavaScript, Java",
        "frameworks": "React, Node.js, Django",
        "education level": "Bachelor's Degree",
        "graduation year": "2024",
        "salary expectation": "Competitive"
    }

    def __init__(self, user_info):
        self.user_info = user_info
        self.driver = self.init_driver()
        self.wait = WebDriverWait(self.driver, 20)

    def init_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

    def apply_to_job(self, job_url, job_id, user_id):
        try:
            print(f"Applying to: {job_url}")
            self.driver.get(job_url)

            # Detect application portal type
            if "workday" in job_url:
                return self.apply_workday(job_id, user_id)
            elif "indeed.com" in job_url:
                return self.apply_indeed(job_id, user_id)
            elif "linkedin.com" in job_url:
                return self.apply_linkedin(job_id, user_id)
            elif "github.com" in job_url:
                return self.apply_github(job_id, user_id)
            else:
                return self.apply_generic(job_id, user_id)
        except Exception as e:
            print(f"Application failed: {e}")
            self.capture_application_error(job_id, user_id, str(e))
            return False
        finally:
            self.driver.quit()

    def apply_workday(self, job_id, user_id):
        try:
            print("Detected Workday application portal")
            
            # Check if we need to create an account
            if self.driver.find_elements(By.ID, 'input-4'):
                print("Workday account creation required")
                return self.create_workday_account(job_id, user_id)
            
            # Check if login is required
            if self.driver.find_elements(By.ID, 'input-1'):
                print("Workday login required")
                return self.login_to_workday(job_id, user_id)
            
            # Start application
            apply_button = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-automation-id='applyButton']")
            ))
            apply_button.click()
            
            # Fill out Workday-specific SWE fields
            self.fill_workday_fields()
            
            # Fill personal information
            self.fill_field('firstName', self.user_info['name'].split()[0])
            self.fill_field('lastName', self.user_info['name'].split()[-1])
            self.fill_field('email', self.user_info['email'])
            self.fill_field('phone', self.user_info['phone'])
            
            # Upload resume
            if self.user_info.get('resume_path'):
                resume_field = self.driver.find_element(
                    By.CSS_SELECTOR, "input[type='file'][accept='.doc,.docx,.pdf']"
                )
                resume_field.send_keys(os.path.abspath(self.user_info['resume_path']))
            
            # Answer eligibility questions
            self.answer_workday_questions()
            
            # Submit application
            submit_btn = self.wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-automation-id='bottom-navigation-next-button']")
            ))
            submit_btn.click()
            
            # Verify submission
            self.wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//h2[contains(., 'Application Submitted')]")
            ))
            return True
            
        except Exception as e:
            print(f"Workday application failed: {e}")
            self.capture_application_error(job_id, user_id, str(e))
            return False

    def create_workday_account(self, job_id, user_id):
        try:
            print("Creating Workday account...")
            # Generate a workday email if not provided
            if not self.user_info.get('workday_email'):
                base_email = self.user_info['email'].split('@')[0]
                workday_email = f"{base_email}+workday@example.com"
                self.user_info['workday_email'] = workday_email
            
            # Generate password if not provided
            if not self.user_info.get('workday_password'):
                workday_password = "AutoApply123!"
                self.user_info['workday_password'] = workday_password
            
            # Fill registration form
            self.fill_field('input-4', self.user_info['workday_email'])
            self.fill_field('input-5', self.user_info['workday_password'])
            self.fill_field('input-6', self.user_info['workday_password'])
            
            # Submit registration
            register_btn = self.driver.find_element(
                By.CSS_SELECTOR, "button[data-automation-id='createAccountButton']"
            )
            register_btn.click()
            
            # Wait for registration to complete
            time.sleep(3)
            
            # Save credentials to user profile
            self.save_workday_credentials(user_id)
            
            # Restart application process
            return self.apply_workday(job_id, user_id)
            
        except Exception as e:
            print(f"Workday account creation failed: {e}")
            error = {
                'error_type': 'WORKDAY_ACCOUNT_CREATION_FAILED',
                'field_name': 'workday_credentials',
                'message': str(e)
            }
            self.capture_application_error(job_id, user_id, error)
            return False

    def login_to_workday(self, job_id, user_id):
        try:
            print("Logging into Workday...")
            if not self.user_info.get('workday_email') or not self.user_info.get('workday_password'):
                error = {
                    'error_type': 'WORKDAY_CREDENTIALS_MISSING',
                    'field_name': 'workday_credentials',
                    'message': 'Workday credentials required'
                }
                self.capture_application_error(job_id, user_id, error)
                return False
                
            self.fill_field('input-1', self.user_info['workday_email'])
            self.fill_field('input-2', self.user_info['workday_password'])
            
            login_btn = self.driver.find_element(
                By.CSS_SELECTOR, "button[data-automation-id='signInSubmitButton']"
            )
            login_btn.click()
            
            # Wait for login to complete
            time.sleep(2)
            
            # Restart application process
            return self.apply_workday(job_id, user_id)
            
        except Exception as e:
            print(f"Workday login failed: {e}")
            error = {
                'error_type': 'WORKDAY_LOGIN_FAILED',
                'field_name': 'workday_credentials',
                'message': str(e)
            }
            self.capture_application_error(job_id, user_id, error)
            return False

    def save_workday_credentials(self, user_id):
        try:
            with current_app.app_context():
                user = UserProfile.query.filter_by(user_id=user_id).first()
                if user:
                    user.workday_email = self.user_info['workday_email']
                    user.workday_password = self.user_info['workday_password']
                    db.session.commit()
                    print("Workday credentials saved to user profile")
        except Exception as e:
            print(f"Error saving Workday credentials: {e}")

    def fill_workday_fields(self):
        try:
            print("Filling Workday-specific SWE fields")
            for field_name, value in self.WORKDAY_SWE_FIELDS.items():
                try:
                    # Try to find the field by placeholder text
                    field = self.driver.find_element(
                        By.XPATH, f"//input[contains(@placeholder, '{field_name}')]"
                    )
                    field.send_keys(value)
                except:
                    # Try to find the field by associated label
                    try:
                        label = self.driver.find_element(
                            By.XPATH, f"//label[contains(., '{field_name}')]"
                        )
                        field = label.find_element(By.XPATH, "./following::input[1]")
                        field.send_keys(value)
                    except:
                        print(f"Couldn't find field: {field_name}")
        except Exception as e:
            print(f"Error filling Workday fields: {e}")

    def answer_workday_questions(self):
        try:
            # Workday-specific question handling
            questions = self.driver.find_elements(
                By.CSS_SELECTOR, "div[data-automation-id='questionPrompt']"
            )
            
            for question in questions:
                q_text = question.text.lower()
                
                # Authorization question
                if "authorized to work" in q_text or "require sponsorship" in q_text:
                    self.select_radio_option(question, "No")
                    
                # Veteran status
                elif "veteran" in q_text:
                    self.select_radio_option(question, "I don't wish to answer")
                    
                # Disability status
                elif "disability" in q_text:
                    self.select_radio_option(question, "No")
                    
                # GPA question
                elif "gpa" in q_text:
                    self.fill_field_by_label(q_text, "3.5")
                    
                # Work availability
                elif "available to work" in q_text:
                    self.select_radio_option(question, "Yes")
        except Exception as e:
            print(f"Error answering Workday questions: {e}")

    def select_radio_option(self, container, option_text):
        try:
            # Find radio button by associated label text
            option = container.find_element(
                By.XPATH, f".//label[contains(., '{option_text}')]/preceding-sibling::input"
            )
            if option:
                option.click()
        except:
            print(f"Couldn't select option: {option_text}")

    def fill_field_by_label(self, label_text, value):
        try:
            label = self.driver.find_element(
                By.XPATH, f"//label[contains(., '{label_text}')]"
            )
            field = label.find_element(By.XPATH, "./following::input[1]")
            field.send_keys(value)
        except:
            print(f"Couldn't fill field for: {label_text}")

    def apply_indeed(self, job_id, user_id):
        try:
            apply_button = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(., "Apply now")]')
            ))
            apply_button.click()

            name_field = self.wait.until(EC.presence_of_element_located(
                (By.NAME, 'applicant.name')
            ))
            name_field.send_keys(self.user_info['name'])

            email_field = self.driver.find_element(By.NAME, 'applicant.email')
            email_field.send_keys(self.user_info['email'])

            try:
                phone_field = self.driver.find_element(By.NAME, 'applicant.phoneNumber')
                phone_field.send_keys(self.user_info['phone'])
            except:
                pass

            try:
                education_field = self.driver.find_element(By.NAME, 'education')
                education_field.send_keys(self.user_info['education'])
            except:
                pass

            self.answer_questions()

            submit_btn = self.driver.find_element(By.XPATH, '//button[contains(., "Submit Application")]')
            submit_btn.click()

            self.wait.until(EC.presence_of_element_located(
                (By.XPATH, '//div[contains(., "application submitted")]')
            ))
            return True
        except Exception as e:
            print(f"Indeed application error: {e}")
            self.capture_application_error(job_id, user_id, str(e))
            return False

    def apply_linkedin(self, job_id, user_id):
        try:
            easy_apply = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(., "Easy Apply")]')
            ))
            easy_apply.click()

            self.fill_linkedin_sections()
            self.answer_questions()

            submit_btn = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(., "Submit application")]')
            ))
            submit_btn.click()

            self.wait.until(EC.presence_of_element_located(
                (By.XPATH, '//h3[contains(., "Application submitted!")]')
            ))
            return True
        except Exception as e:
            print(f"LinkedIn application error: {e}")
            self.capture_application_error(job_id, user_id, str(e))
            return False

    def apply_github(self, job_id, user_id):
        try:
            apply_button = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//a[contains(., "Apply") or contains(., "APPLY")]')
            ))
            apply_url = apply_button.get_attribute('href')
            self.driver.get(apply_url)
            time.sleep(2)
            return self.apply_generic(job_id, user_id)
        except Exception as e:
            print(f"GitHub application error: {e}")
            self.capture_application_error(job_id, user_id, str(e))
            return False

    def apply_generic(self, job_id, user_id):
        try:
            self.fill_field('name', self.user_info['name'])
            self.fill_field('email', self.user_info['email'])
            self.fill_field('phone', self.user_info['phone'])
            self.fill_field('education', self.user_info['education'])

            self.answer_questions()

            for question, answer in self.user_info.get('answers', {}).items():
                try:
                    field = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{question}')]/following-sibling::textarea")
                    field.send_keys(answer)
                except:
                    pass

            submit_btn = self.driver.find_element(By.XPATH, '//input[@type="submit"] | //button[@type="submit"]')
            submit_btn.click()
            time.sleep(3)
            return True
        except Exception as e:
            print(f"Generic application error: {e}")
            self.capture_application_error(job_id, user_id, str(e))
            return False

    def fill_linkedin_sections(self):
        for _ in range(5):
            try:
                self.fill_field('email', self.user_info['email'])
                self.fill_field('phone', self.user_info['phone'])

                try:
                    education_field = self.driver.find_element(By.XPATH, "//label[contains(., 'Education')]/following-sibling::input")
                    education_field.send_keys(self.user_info['education'])
                except:
                    pass

                for question, answer in self.user_info.get('answers', {}).items():
                    try:
                        field = self.driver.find_element(By.XPATH, f"//label[contains(., '{question}')]/following-sibling::textarea")
                        field.send_keys(answer)
                    except:
                        pass

                next_btn = self.driver.find_element(By.XPATH, '//button[contains(., "Next")]')
                next_btn.click()
                time.sleep(1)
            except:
                break

    def fill_field(self, field_name, value):
        try:
            field = self.driver.find_element(By.NAME, field_name)
            if not field.get_attribute('value'):
                field.send_keys(value)
        except:
            try:
                # Try by placeholder
                field = self.driver.find_element(
                    By.XPATH, f"//input[contains(@placeholder, '{field_name}')]"
                )
                field.send_keys(value)
            except:
                pass

    def answer_questions(self):
        try:
            questions = self.driver.find_elements(By.XPATH, '//label | //legend | //p[contains(text(), "?")]')
            for question in questions:
                q_text = question.text.strip().lower()
                if not q_text:
                    continue
                    
                # Try exact matches first
                answer = None
                for pattern, response in self.COMMON_QUESTIONS.items():
                    if pattern in q_text:
                        answer = response
                        break
                        
                # Then try user answers
                if not answer:
                    for pattern, response in self.user_info.get('answers', {}).items():
                        if pattern.lower() in q_text:
                            answer = response
                            break
                            
                if answer:
                    try:
                        input_field = question.find_element(By.XPATH, './following::input[1] | ./following::textarea[1]')
                        input_field.send_keys(answer)
                    except:
                        try:
                            if "yes" in answer.lower():
                                yes_btn = question.find_element(
                                    By.XPATH, './/following::input[contains(@value, "Yes") or contains(@value, "yes")][1]'
                                )
                                yes_btn.click()
                            elif "no" in answer.lower():
                                no_btn = question.find_element(
                                    By.XPATH, './/following::input[contains(@value, "No") or contains(@value, "no")][1]'
                                )
                                no_btn.click()
                        except:
                            print(f"Couldn't answer: {q_text}")
        except Exception as e:
            print(f"Error answering questions: {e}")

    def capture_application_error(self, job_id, user_id, error_message):
        try:
            # Parse error type
            error_type = "UNKNOWN"
            field_name = None
            
            if "could not locate element" in error_message:
                error_type = "ELEMENT_MISSING"
            elif "file upload" in error_message:
                error_type = "UPLOAD_FAILED"
            elif "required field" in error_message:
                error_type = "FIELD_MISSING"
                # Extract field name from error message
                field_match = re.search(r"field '(.+?)'", error_message)
                if field_match:
                    field_name = field_match.group(1)
            
            # Save to database
            error = ApplicationError(
                job_id=job_id,
                user_id=user_id,
                error_type=error_type,
                field_name=field_name,
                required_value=None
            )
            db.session.add(error)
            db.session.commit()
            
        except Exception as e:
            print(f"Failed to capture error: {e}")