"""Code to extract book details from Books to Scrape website """
import os
import shutil
from urllib.parse import urljoin
import csv
import requests
from bs4 import BeautifulSoup

MAIN_URL = "http://books.toscrape.com/catalogue/category/books_1/index.html"

def get_single_book_details(product_url): # EXTRACT + TRANSFORM SECTION OF ETL PROCESS
    """Function to get all detailsl of speicified product url"""

    web_page = requests.get(product_url)
    soup = BeautifulSoup(web_page.content,'html.parser')
    dictofdetails = {"product_page_url":"","book_title":"","upc":"","price_including_tax":"","price_excluding_tax":"","quantity_available":"","description":"","category":"","review_rating":"","image_url":""}
    dictofdetails["product_page_url"] = product_url
    #Column --> book_title
    book_title = soup.find_all("li",class_="active")[0].text
    dictofdetails["book_title"] = book_title
    #for row in product_rows:
    table_headers = soup.find_all("th")
    header_values = soup.find_all("td")
    dict = {}
    #Columns --> upc,price_including_tax,price_excluding_tax,quantity_available
    for i in range(len(table_headers)):
        index = table_headers[i].text.strip()
        value = header_values[i].text.strip()
        dict[index] = value

    dictofdetails["upc"] = dict["UPC"]
    dictofdetails["price_including_tax"] = dict["Price (incl. tax)"]
    dictofdetails["price_excluding_tax"] = dict["Price (excl. tax)"]
    dictofdetails['quantity_available'] = dict["Availability"]

    #Column --> description ## PENDING
    description =soup.find("article",class_="product_page").select("p")[3].get_text(strip=True)
    dictofdetails["description"] = description

    #Column --> category ## PENDING
    category = soup.find("ul",class_="breadcrumb").select("li")[2].find("a").get_text(strip=True)
    dictofdetails["category"] = category

    #Column --> review_rating
    rating = soup.find("article",class_="product_page").select("p")[2]
    review_rating = rating['class'][1]
    dictofdetails["review_rating"] = review_rating

    #Column --> image_url
    image_url =""
    images = soup.find_all("img")
    for img in images:
        if img['alt'] == book_title:
            image_url = img['src']
    image_url = image_url.replace("../..","http://books.toscrape.com/")
    dictofdetails["image_url"] = image_url

    image_folder = os.getcwd()+"/images"
    if not os.path.isdir(image_folder):
        os.mkdir("images")
    
    image_filename = os.getcwd() + "/images/" + image_url.split("/")[-3] + image_url.split("/")[-2] + ".jpg"
    r = requests.get(image_url,stream=True)
    if r.status_code == 200:
        with open(image_filename,"wb") as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw,f)

    return dictofdetails
    
def get_single_category_books_url(category_url): # EXTRACT SECTION OF ETL PROCESS
    """Function to get urls of all books from speicified category"""
    list_of_book_urls = []

    while True:
        web_page = requests.get(category_url)
        soup = BeautifulSoup(web_page.content,'html.parser')

        category = soup.find("ul",class_="breadcrumb").select("li")[2].get_text(strip=True)
        print("Category: ",category)

        # check books are distributed on multiple pages
        strong_tags = soup.find("form",class_="form-horizontal").select("strong")

        # total number of books in the category
        total_num_books = strong_tags[0].get_text(strip=True)
        if len(strong_tags) == 1:
            start_index = 0
            end_index = int(total_num_books)
        else:
            start_index = int(strong_tags[1].get_text(strip=True))
            end_index = int(strong_tags[2].get_text(strip=True))

        # retrieve each book's url on the page
        book_sections = soup.find_all("article",class_="product_pod")
        i = 0
        j = int(start_index)
        print("Total Books: ",total_num_books,start_index,end_index)
        while j <= int(end_index):
            if i >= int(total_num_books):
                break
            book_url = book_sections[i].select("a")[1]["href"]
            book_url = book_url.replace("../../..","http://books.toscrape.com/catalogue")
            list_of_book_urls.append(book_url)
            j += 1
            i += 1

        #check if next page exists or not
        next_page = soup.select_one("li.next>a")
        if next_page:
            next_url = next_page.get('href')
            category_url = urljoin(category_url, next_url)
            print(category_url)
        else:
            break
    return list_of_book_urls

def get_all_categories(main_pageurl): # EXTRACT SECTION OF ETL PROCESS
    """Function to retrieve all categories URLs"""

    web_page = requests.get(main_pageurl)
    soup = BeautifulSoup(web_page.content,'html.parser')
    all_cat_dict = {}
    side_categories = soup.find("ul",class_="nav nav-list").find("li").select("a")

    for i in range(1,len(side_categories)):
        cat_url = side_categories[i]["href"]
        cat_url = cat_url.replace("..","http://books.toscrape.com/catalogue/category")
        cat_name = side_categories[i].get_text(strip=True)
        i += 1
        all_cat_dict[cat_name] = cat_url
    return all_cat_dict

def write_data_to_csv(): # LOAD SECTION OF ETL PROCESS
    """Function to write details of each books of each categories to Separate csv file"""

    header_row = ["product_page_url","book_title","upc","price_including_tax","price_excluding_tax","quantity_available","description","category","review_rating","image_url"]

    # retrieve all categories
    all_categories = get_all_categories(MAIN_URL)
    cat_names_list = list(all_categories.keys())

    for category in range(0,len(cat_names_list)):
        cat_name = cat_names_list[category]
        list_books_url = get_single_category_books_url(all_categories[cat_name])

        # make csv file as per category name
        filename = open(cat_name+".csv","w",newline="", encoding="utf-8")
        writer = csv.writer(filename,delimiter=";")
        writer.writerow(header_row)
        i = 0

        # write each book details to corresponding csv file
        while i < len(list_books_url):
            single_book_dict = get_single_book_details(list_books_url[i])
            data_row = []
            for j in range(len(header_row)):
                data_row.append(single_book_dict[header_row[j]])
            writer.writerow(data_row)
            i += 1

write_data_to_csv()
