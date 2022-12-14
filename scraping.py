# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemisphere_images(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


# Scrape web data
def mars_news(browser):
    # Visit url
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay and search for elements w/ specific
    # combination of tag (div) and attribute (list_text).
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        # Returns reference to first object found
        # that contains <div class='list_text'>
        slide_elem = news_soup.select_one('div.list_text')

        # Retrieve only the text of this element.
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Scrape the article summary from this same element.
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_p


# JPL Space Images Featured Image
def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None

    # Use base url to create absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url


# Create Data Table
def mars_facts():
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    df.columns = ['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    return df.to_html()


# Hemisphere Images
def hemisphere_images(browser):
    # 1. Use browser to visit the URL
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Retrieve the image urls and titles for each hemisphere.
    html = browser.html
    img_soup = soup(html, 'html.parser')

    titles = [title.get_text() for title in img_soup.find_all('h3')]
    titles.remove(titles[-1])

    for i in range(len(titles)):
        # Find and click image link
        browser.links.find_by_partial_text(titles[i]).click()

        # Find link to full image
        html = browser.html
        img_soup = soup(html, 'html.parser')
        full_image_link = img_soup.find('a', text='Sample').get('href')

        # Add image link to dictionary
        hemisphere_image_urls.append({
            'img_url': url + full_image_link,
            'title': titles[i]
        })
        # Return to previous page
        browser.back()

    # 4. Return the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls


if __name__ == "__main__":
    # if running as script, print scraped data
    print(scrape_all())
