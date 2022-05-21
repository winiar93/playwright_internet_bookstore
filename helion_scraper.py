from playwright.sync_api import sync_playwright
import time
import re
import pandas as pd
import datetime

with sync_playwright() as p:

    data_record = []
    browser = p.chromium.launch(headless=True, slow_mo=50)
    page = browser.new_page()
    page.goto("https://helion.pl/")
    
    print(page.title())

    page.type("input#inputSearch", "python")
    time.sleep(0.3)
    page.click("#szukanie > fieldset > a > button")
    for no_page in range(58):
        
        numerate_page = f"https://helion.pl/search?szukaj=python&nrs={no_page}&serwisyall=0&wsprzed=1&wprzed=0&wprzyg=0&wyczerp=0&sortby=wd&qa=&nr=&ceny=&formaty=&wydawca=&jezyk=&promocja="
        page.goto(numerate_page)
        bks = page.query_selector_all("#right-big-col > div.book-list-container.multi-line.padding-top.padding-top-search > div > ul > li")
        time.sleep(2)

        for single_book in bks:
            book_tags = single_book.query_selector("p.tags").inner_text()
            book_title = single_book.query_selector("h3 a:first-of-type").inner_text()
            book_author = single_book.query_selector("p[class*='author']").inner_text()
            #example path to book actual price -  "p > #text","a > ins","a","p a #text", 
            book_actual_price = "null"
            for fn in ["p[class*='price price-add']","p[class*='price price-time']", "a > ins"]:
                try:
                    book_actual_price = single_book.query_selector(f"{fn}").inner_text().replace("\n", " ")
                    break
                except Exception as e:
                    print(e)
                    pass
                
            try:
                book_first_price = single_book.query_selector("del").inner_text()

            except Exception as e:
                print(e)
                book_first_price = "null"
                
            book_format_list_raw = single_book.query_selector_all("ul > li") #[class*='book-type']
            book_format_list = [x.get_attribute("class") for x in book_format_list_raw]
            words = ['type-book', 'type-ebook', 'type-online']
            finds = []
            for i in book_format_list:
                try:
                    single_finds = re.findall(r"(?=(\b" + '\\b|\\b'.join(words) + r"\b))", i)
                    finds.append(single_finds[0].split("-")[-1])
                except Exception as e:
                    print(e)
                    pass

            book_format = ' '.join(set(finds))

            book_url = single_book.query_selector("a").get_attribute("href")
            
            data_row = {"book_title": str(book_title),
                "book_author": str(book_author),
                "book_tags": str(book_tags), 
                "book_format": str(book_format), 
                "book_actual_price": str(book_actual_price),
                "book_first_price": str(book_first_price),
                "book_url_link": book_url}
            print(data_row)
            data_record.append(data_row)
        print(no_page)
    df = pd.DataFrame(data_record)
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y_%m_%d_%H_%M_%S")
    
    df.to_csv(f"helion_ksiazki_{timestamp}.csv", sep="\t")
    page.close()