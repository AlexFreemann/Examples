path="/Users/aleksandrglotov/Downloads/geckodriver"



import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep


class WebDriverPythonBasics(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox(executable_path=path)



    def test_saucelabs_homepage_header_displayed(self):
        self.browser.get("https://auto.ru/cars/evaluation/?from=top_menu")
        print(self.browser)
        sleep(0.3)
        element = self.browser.find_element_by_id("confirm-button")
        self.assertTrue(element.is_displayed())
        # element.send_keys("Hello WebDriver!")
        element.click()
        sleep(0.3)

        sleep(1)
        pricing_link2 = self.browser.find_element_by_xpath("//*[text()='{}']".format(input("Ведите производителя:")))
        self.assertTrue(pricing_link2.is_displayed())
        pricing_link2.click()
        sleep(3)
        pricing_link3 = self.browser.find_element_by_xpath("//span[text()='{}' and @class='Radio__text']".format(input("Введите модель:")))

        self.assertTrue(pricing_link3.is_displayed())
        pricing_link3.click()
        sleep(3)
        pricing_link4 = self.browser.find_element_by_xpath("//span[text()='{}' and @role='presentation']".format(input("Введите год:")))
        self.assertTrue(pricing_link4.is_displayed())
        pricing_link4.click()
        sleep(3)
        pricing_link5 = self.browser.find_element_by_xpath(
            "//span[text()='{}' and @class='Radio__text']".format(input("Введите тип кузова\n Седан \nУниверсал 5 дв. \n Хэтчбек 5 дв.:")))
        self.assertTrue(pricing_link5.is_displayed())
        pricing_link5.click()
        pricing_link6 = self.browser.find_element_by_xpath(
            "//span[text()='{}' and @class='Radio__text']".format(
                input("Поколение.:")))
        self.assertTrue(pricing_link6.is_displayed())
        pricing_link6.click()
        pricing_link7 = self.browser.find_element_by_xpath(
            "//span[text()='{}' and @class='Radio__text']".format(
                input("Тип топлива.:")))
        self.assertTrue(pricing_link7.is_displayed())
        pricing_link7.click()
        pricing_link8 = self.browser.find_element_by_xpath(
            "//span[text()='{}' and @class='Radio__text']".format(
                input("Тип топлива.:")))
        self.assertTrue(pricing_link7.is_displayed())
        pricing_link7.click()
        sleep(10)




    def tearDown(self):
        self.browser.close()

if __name__ == '__main__':
        unittest.main()


#

