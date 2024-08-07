import selenium
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import os
import time
import datetime

# import requests

# setting up the driver
driver_path = "/home/user/chrome-linux64/chrome"
# Set the path to the ChromeDriver executable in the PATH environment variable
os.environ["PATH"] += ":/home/user/chrome-linux64/chrome"
driver = webdriver.Chrome()

# get the jumia page
start_time = time.time()
# print(start_time)
URL = "https://www.carrefour.ke/mafken/en/"
driver.get(url=URL)
# fetch the close_popup button
popup_is_closed = 0
wait = WebDriverWait(driver, 5)
while popup_is_closed == 0:
    # check for elapsed time in case popup doesnt appear to exit loop
    elapsed_time = time.time()
    if elapsed_time - start_time > 19:
        popup_is_closed = 1

    try:
        close_button = driver.find_element(by=By.CLASS_NAME, value="close-button")
        # close_button = driver.find_element(by=By.XPATH, value="/html/body/div[3]/div[3]/span/svg/path")
        close_button.click()
        popup_is_closed = 1
        # print("popup closed")
    except selenium.common.exceptions.NoSuchElementException:
        popup_is_closed = 0

# navigate to the all categories
p_path = "//a[contains(@rel,'menu')]/div/p"
all_categories_links = driver.find_elements(by=By.XPATH, value="//a[contains(@rel,'menu')]")

# all_categories_names = driver.find_elements(by=By.XPATH, value=p_path)
links_list = [all_categories_links[i].get_attribute("href") for i in range(len(all_categories_links) - 1)]

# wait for category names to load
wait = WebDriverWait(driver, 10)
# create a list with all links

sub_menu_xpath = "/html/body/div[1]/div[3]/div[2]/div[1]/div/div/div[1]/div/div[7]/div/a/p"


def go_to_page(page):
    driver.get(url=page)
    # get the page name
    page_name = driver.find_element(by=By.CSS_SELECTOR, value="html head title")
    print(f"\n\npage name : {page_name.get_attribute('textContent')}")
    # wait for the sub menu to load
    wait = WebDriverWait(driver, 3)

    #
    visited_pages = 0

    # look for the submenu links add to a list ,their names ,add to list
    sub_links_elements = driver.find_elements(by=By.XPATH, value="//div/div/a[contains(@data-testid,'facet-link')]")
    root_link_list = [link.get_attribute("href") for link in sub_links_elements]

    sub_link_names = driver.find_elements(by=By.XPATH, value="//div/div/a[contains(@data-testid,'facet-link')]/p")
    root_page_names_list = [name.get_attribute("textContent") for name in sub_link_names]

    for i in range(len(root_link_list)):
        page_name = root_page_names_list[i]
        print(f"sub page : {page_name}")
        driver.get(url=root_link_list[i])
        # time.sleep(3)

        # look for the page info header
        page_info_headers = driver.find_elements(by=By.XPATH, value="//div/div/p")

        # print(page_info_header)
        for head in page_info_headers:
            head = head.get_attribute("textContent")
            if "esults" in head:
                # print(head)
                no_of_results = head.split(sep=" ")[0]
                print(f"results : {no_of_results}")

        # keep scrolling until all products are loaded
        # todo locate load more button
        try:
            load_more = driver.find_element(by=By.XPATH,
                                            value="//*[@id='__next']/div[3]/div[1]/div[4]/div[2]/div[3]/button")
            # see if located
            if load_more.get_attribute("textContent") is not None:
                loading = 1
            else:
                loading = 0

        except NoSuchElementException:
            print(f"{page_name} has no load more button")
            loading = 0

        # keep clicking the load_more button
        while loading == 1:
            try:
                load_more = driver.find_element(by=By.XPATH,
                                                value="//*[@id='__next']/div[3]/div[1]/div[4]/div[2]/div[3]/button")
            except NoSuchElementException:
                loading = 0
                continue
            # see if located
            if load_more.get_attribute("textContent") is not None:
                
                initial_num_items = driver.find_elements(by=By.XPATH,
                                                         value="//div[contains(@data-testid,'product_card')]/a")
                initial_num_items = len(initial_num_items)
                print(f"load more text : {load_more.get_attribute('textContent')}")
                load_more.click()

                # todo implement a wait for more elements to load
                def has_increased(driver):
                    current_num_items = driver.find_elements(by=By.XPATH,
                                                             value="//div[contains(@data-testid,'product_card')]/a")
                    current_num_items = len(current_num_items)
                    return current_num_items > initial_num_items
                try:
                    WebDriverWait(driver,4).until(has_increased)
                except TimeoutException:
                    continue

            else:
                loading = 0
            try:
                load_more = driver.find_element(by=By.XPATH,
                                                value="//*[@id='__next']/div[3]/div[1]/div[4]/div[2]/div[3]/button")
                # see if located
                if load_more.get_attribute("textContent") is not None:
                    loading = 1
                else:
                    loading = 0
            except:
                loading = 0

        # open the file for this page

        with open(file=f"{page_name}.csv", mode="w") as file:
            file.close()
        # todo fetch the product name ,price ,discount ,image link
        name_path = "//div[contains(@data-testid,'product_card')]/a"
        image_path = "//div[contains(@data-testid,'product_card')]/a/img"
        price_path = "//div[contains(@data-testid,'product_price')]/div/div/div"
        # discount_path = "//div[contains(@data-testid,'product_price')]/div/span"

        product_names = driver.find_elements(by=By.XPATH, value=name_path)
        names_list = [name.get_attribute("title") for name in product_names]
        print(f"len names = {len(names_list)}")

        product_prices = driver.find_elements(by=By.XPATH, value=price_path)
        prices_list = [price.get_attribute("textContent") for price in product_prices]
        for price in prices_list:
            if "KES" in price:
                prices_list.remove(price)

        product_images = driver.find_elements(by=By.XPATH, value=image_path)
        images_list = [image.get_attribute("src") for image in product_images]

        # product_discounts = driver.find_elements(by=By.XPATH, value=discount_path)
        # discounts_list = [discount.get_attribute("textContent") for discount in product_discounts]

        # click the load more button
        # repeat above until all prices are fetched
        # TODO put in a while loop while load more button is present

        # todo reconfigure to match lists
        for j in range(len(names_list)):
            product_info_dict = {
                "name": names_list[j],
                "price": prices_list[j],
                "image": images_list[j],
                # "discount": discounts_list[j]
            }
            # write to file
            product_info_line = str(f"{[item for item in product_info_dict.items()]} ,")
            print(f"writing - > {product_info_line}")
            with open(file=f"{page_name}.csv", mode="a") as file:
                file.write(f"{product_info_line}\n")

        visited_pages += 1

    if visited_pages < 1:
        print("subless page")
        # print(page_info_header)
        page_info_headers = driver.find_elements(by=By.XPATH, value="//div/div/p")
        for head in page_info_headers:
            head = head.get_attribute("textContent")
            if "esults" in head:
                # print(head)
                no_of_results = head.split(sep=" ")[0]
                print(f"results : {no_of_results}")
                # open the file for this page

                with open(file=f"{page_name}.csv", mode="w") as file:
                    file.close()
                # todo fetch the product name ,price ,discount ,image link
                name_path = "//div[contains(@data-testid,'product_card')]/a"
                image_path = "//div[contains(@data-testid,'product_card')]/a/img"
                price_path = "//div[contains(@data-testid,'product_price')]/div/div/div"
                # discount_path = "//div[contains(@data-testid,'product_price')]/div/span"

                product_names = driver.find_elements(by=By.XPATH, value=name_path)
                names_list = [name.get_attribute("title") for name in product_names]
                print(f"len names = {len(names_list)}")

                product_prices = driver.find_elements(by=By.XPATH, value=price_path)
                prices_list = [price.get_attribute("textContent") for price in product_prices]
                for price in prices_list:
                    if "KES" in price:
                        prices_list.remove(price)

                product_images = driver.find_elements(by=By.XPATH, value=image_path)
                images_list = [image.get_attribute("src") for image in product_images]

                # product_discounts = driver.find_elements(by=By.XPATH, value=discount_path)
                # discounts_list = [discount.get_attribute("textContent") for discount in product_discounts]

                # click the load more button
                # repeat above until all prices are fetched
                # TODO put in a while loop while load more button is present

                # todo reconfigure to match lists
                for j in range(len(names_list)):
                    product_info_dict = {
                        "name": names_list[j],
                        "price": prices_list[j],
                        "image": images_list[j],
                        # "discount": discounts_list[j]
                    }
                    # write to file
                    product_info_line = str(f"{[item for item in product_info_dict.items()]} ,")
                    print(f"writing - > {product_info_line}")
                    with open(file=f"{page_name}.csv", mode="a") as file:
                        file.write(f"{product_info_line}\n")

                visited_pages += 1

    time.sleep(2)
    # wait = WebDriverWait(driver, 20)


# start at index 1 to skip the main page
def main():
    print(f"no of links : {len(links_list)}")
    for i in range(2, len(links_list)):
        go_to_page(links_list[i])


if __name__ == "__main__":
    main()
