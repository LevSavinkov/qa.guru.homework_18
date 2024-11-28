from requests import post
import allure
from selene import browser, by, have

from tests.utils.log_util import logging_response, attach_response

BASE_API_URL = "https://demowebshop.tricentis.com/"
USER_EMAIL = "test.qa.guru.c16@gmail.com"


def test_add_to_cart_unauthorized():
    with allure.step("Добавляем товар в корзину методом POST /addproducttocart/catalog"):
        response = post(url=f"{BASE_API_URL}/addproducttocart/catalog/31/1/1")
    
    logging_response(response)
    attach_response(response)
    
    assert response.status_code == 200
    assert response.json().get("success") is True
    
    with allure.step("Получаем cookie"):
        cookie = response.cookies.get("Nop.customer")
    
    with allure.step("Открываем сайт demowebshop.tricentis.com"):
        browser.open("https://demowebshop.tricentis.com/")
    
    with allure.step("Подставляем cookie в браузер"):
        browser.driver.add_cookie({"name": "Nop.customer", "value": cookie})
        browser.driver.refresh()
    
    with allure.step("Проверяем на фронте что товар был добавлен в корзину"):
        browser.element("#topcartlink").element("a").element(by.class_name("cart-qty")).should(have.text("(1)"))
        browser.element("#topcartlink").click()
        browser.element(by.xpath("//a[@class='product-name']")).should(have.text("14.1-inch Laptop"))


def test_add_to_cart_authorized():
    with allure.step("Авторизуемся"):
        response = post(
            url=f"{BASE_API_URL}/login",
            data={"Email": USER_EMAIL, "Password": "Qwerty!12", "RememberMe": False},
            allow_redirects=False
        )
    
    assert response.status_code == 302
    
    with allure.step("Получаем авторизационный токен"):
        token = response.cookies.get("NOPCOMMERCE.AUTH")
    
    with allure.step("Добавляем товар в корзину методом POST /addproducttocart/catalog"):
        post(url=f"{BASE_API_URL}/addproducttocart/catalog/31/1/1", cookies={"NOPCOMMERCE.AUTH": token})
        
    with allure.step("Открываем сайт demowebshop.tricentis.com"):
        browser.open("https://demowebshop.tricentis.com/")
    
    with allure.step("Подставляем cookie в браузер"):
        browser.driver.add_cookie({"name": "NOPCOMMERCE.AUTH", "value": token})
        browser.driver.refresh()
    
    with allure.step("Проверяем на фронте что пользователь авторизован"):
        browser.element(by.xpath("//div[@class='header-links']//a[@class='account']")).should(have.text(USER_EMAIL))
    
    with allure.step("Проверяем на фронте что товар был добавлен в корзину"):
        browser.element("#topcartlink").element("a").element(by.class_name("cart-qty")).should(have.text("(1)"))
        browser.element("#topcartlink").click()
        browser.element(by.xpath("//a[@class='product-name']")).should(have.text("14.1-inch Laptop"))
    
    with allure.step("Очищаем корзину"):
        browser.element(by.xpath("//input[@name='removefromcart']")).click()
        browser.element(by.xpath("//input[@name='updatecart']")).click()
        browser.element(by.xpath("//div[@class='order-summary-content']")).should(
            have.text("Your Shopping Cart is empty!"))
