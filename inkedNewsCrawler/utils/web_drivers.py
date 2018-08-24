from selenium import webdriver


def get_chrome_options(headless=True, disable_javascript=True, disable_images=True):
    options = webdriver.ChromeOptions()
    prefs = {}
    if headless:
        options.add_argument('--headless')
    if disable_images:
        prefs["profile.managed_default_content_settings.images"] = 2
    if disable_javascript:
        prefs["profile.managed_default_content_settings.javascript"] = 2
    options.add_experimental_option("prefs", prefs)
    return options
