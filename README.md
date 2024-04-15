
# Project - 2 Price Monitoring System

This code reflects the monitoring system to track book prices at [Books to Scrape](http://books.toscrape.com/), an online book retailer and establishes ETL pipeline.

The will read all the details of each book from each category and load it into the csv file named as per the category name and all book images will be downloaded in the images folder.

## Libraries

- request
- BeautifulSoup
- csv
- urljoin

To install libraries use the following command:

```text
pip install requirements.txt
```

## Defined Functions

- **get_all_categories(main_pageurl)**:

    This function takes main page URL as an input and returns dictionary containing all categories of book.

- **get_single_category_books_url(category_url)**:

    This function takes category URL as input and returns list of all book-urls of the given category.

- **get_single_book_details(product_url)**:

    This function takes single book-url as an input and returns dictionary containing all the details for the given book.
    It also downloads image of the book in the images folder.

- **write_data_to_csv()**:

    This function writes the details of each book into the separate csv file named as per the category name.

## Execution

To execute the code write following command on the command prompt from the current working directory:

```text
python Megha_Panchal_1_code_110223.py
```
