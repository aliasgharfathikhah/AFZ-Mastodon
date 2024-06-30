import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import wikipedia
import wikipediaapi
from langdetect import detect
import environ

env = environ.Env()
environ.Env.read_env('.env')

def get_wikipedia_summary(search_text, lang='en'):
    try:
        custom_headers = {
            'User-Agent': f"{lang} Wikipedia API Client (https://example.com/contact)"
        }
        wiki_wiki = wikipediaapi.Wikipedia(language=lang, headers=custom_headers)
        page = wiki_wiki.page(search_text)

        if page.exists():
            url = page.fullurl
            url_length = len(url)
            summary_length = 465 - url_length
            summary = page.summary[:summary_length]
            lines = summary.split('. ')
            lines += '\n'
            if lines:
                lines.append(url)
                return lines

        wikipedia.set_lang(lang)
        search_results = wikipedia.search(search_text)
        if not search_results:
            print("No page found for the search term.")
            return None

        for result in search_results:
            try:
                page = wikipedia.page(result)
                summary = page.summary[:300]
                lines = summary.split('. ')
                if lines:
                    return lines
            except wikipedia.exceptions.DisambiguationError as e:
                print(f"Disambiguation error: {e.options}")
            except wikipedia.exceptions.PageError:
                print(f"Page error: No page matched for {result}")
        
        print("No suitable summary found.")
        return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def run_bot(driver):
    driver.implicitly_wait(10)
    driver.get('https://mastodon.world/notifications')
    driver.implicitly_wait(10)
    driver.find_element(By.CLASS_NAME, 'active').click()
    try:
        while True:
            user_name = ''
            driver.implicitly_wait(10)
            messages = driver.find_elements(By.CSS_SELECTOR, 'div.status')
            for message in messages:
                    driver.implicitly_wait(10)
                    star_button = message.find_element(By.CSS_SELECTOR, 'button.star-icon')
                    replay_button = message.find_element(By.CSS_SELECTOR, 'button.icon-button--with-counter')
        
                    if "active" not in star_button.get_attribute('class'):
                        text_element = message.find_element(By.CSS_SELECTOR, 'div.status__content__text')
                        user_element = message.find_element(By.CLASS_NAME, 'display-name__account')
                        user_name = user_element.text
                        print(f"Message: {text_element.text} - {user_element.text}")
                        text = text_element.text.replace('@afz', '').replace('\n', ' ').replace('@afz\n', '').replace('dictator', '').replace('Is', '').strip()
                        print(text)
                        language = detect(text)
                        lines = get_wikipedia_summary(text, language)
                        print(lines)
                        if lines:
                            driver.implicitly_wait(10)
                            star_button.click()
                            driver.implicitly_wait(10)
                            replay_button.click()
                            driver.find_element(By.CLASS_NAME, 'autosuggest-textarea__textarea').send_keys(f'\n {". ".join(lines)}')
                            driver.implicitly_wait(10)
                            driver.find_element(By.CLASS_NAME, 'compose-form__publish-button-wrapper').click()
                        else:
                            driver.implicitly_wait(10)
                            star_button.click()
                            driver.implicitly_wait(10)
                            replay_button.click()
                            driver.find_element(By.CLASS_NAME, 'autosuggest-textarea__textarea').send_keys("╰（‵□′）╯ No data found, please ask more precisely! Or, if the data is available on Wikipedia, raise the issue with our support. @FATHI@mstdn.social Thanks")
                            driver.implicitly_wait(10)
                            driver.find_element(By.CLASS_NAME, 'compose-form__publish-button-wrapper').click()
                        print("------------------------------------------")
    except selenium.common.exceptions.WebDriverException:
        print("Session timed out. Restarting...")
        driver.quit()
        driver = webdriver.Remote(
            command_executor=env.str('SERVER_URL') + 'webdriver',
            options=chrome_options,
        )
        driver.get(url)
        
        for cookie in cookies:
            driver.add_cookie(cookie)
        
        run_bot(driver)

chrome_options = webdriver.ChromeOptions()
chrome_options.set_capability('browserless:token', env.str('TOKEN'))
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')

driver = webdriver.Remote(
    command_executor=env.str('SERVER_URL') + 'webdriver',
    options=chrome_options,
)

print(">> Start")
url = env.str('URL')
driver.get(url)
driver.implicitly_wait(10)
driver.find_element(By.CLASS_NAME, 'button-tertiary').click()

driver.implicitly_wait(10)
driver.find_element(By.ID, 'user_email').send_keys(env.str('USER_EMAIL'))
driver.implicitly_wait(10)
driver.find_element(By.ID, 'user_password').send_keys(env.str('USER_PASSWORD'))

driver.find_element(By.CLASS_NAME, 'btn').click()

cookies = driver.get_cookies()

run_bot(driver)