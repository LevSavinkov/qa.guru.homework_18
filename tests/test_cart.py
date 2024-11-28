from requests import post
import allure
from selene import browser, by, have

from tests.utils.log_util import logging_response, attach_response


def test_add_to_cart():
    with allure.step("Добавляем товар в корзину методом POST /addproducttocart/catalog"):
        response = post(url="https://demowebshop.tricentis.com/addproducttocart/catalog/31/1/1")
    
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
