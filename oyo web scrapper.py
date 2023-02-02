# Web Scraping Program

# Libraries to import, scrape and display the required data
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import argparse as ap
import connect as cnc

# Argument Parser
parser = ap.ArgumentParser()
parser.add_argument('--pagemax', help='Enter number of pages to parse', type=int)
parser.add_argument('--dbname', help='Enter name of database to store info')
args = parser.parse_args()

# Site to be scraped and Request headers
oyo_url = 'https://www.oyorooms.com/hotels-in-chennai/?page='
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
}
Scraped_info_list = []
page_num_max = args.pagemax
cnc.connect_db(args.dbname)

for i in range(1, page_num_max + 1):
    # Get content and parse using HTML parser
    url = oyo_url + str(i)
    print('GET request for : ', url)
    req = requests.get(url, headers=headers)
    content = req.content
    soup = bs(content, 'html.parser')

    # Begin scraping data
    all_hotels = soup.find_all('div', {'class': 'oyo-cell--12-col oyo-cell--8-col-tablet oyo-cell--4-col-phone'})

    for hotel in all_hotels:
        hotel_dict = {}
        hotel_dict['Hotel_name'] = hotel.find('h3', {'class': 'listingHotelDescription__hotelName d-textEllipsis'}).text
        hotel_dict['Hotel_address'] = hotel.find('span', {'itemprop': 'streetAddress'}).text
        hotel_dict['Hotel_price'] = hotel.find('meta', {'itemprop': 'priceRange'}).get('content').split()[0]

        # New hotels have no ratings - 'None' type object return
        try:
            Rating_value = hotel.find('meta', {'itemprop': 'ratingValue'}).get('content')
            Hotel_ratings = hotel.find('span', {'class': 'hotelRating__ratingSummary'}).text
        except AttributeError:
            Rating_value = 'Unrated'
            Hotel_ratings = '(New - No Ratings)'
        hotel_dict['Rating'] = Rating_value + ' ' + Hotel_ratings

        amenities = hotel.find('div', {'class': 'amenityWrapper'})
        amenities_list = []
        for amenity in amenities.find_all('div', {'class': 'amenityWrapper__amenity'}):
            amenities_list.append(amenity.find('span', {'class': 'd-body-sm'}).text.strip())
        hotel_dict['Amenities'] = ', '.join(amenities_list[:-1])

        # Pandas Library requires the input data to be in List form
        Scraped_info_list.append(hotel_dict)

        # Inserting into the Database
        cnc.insert_into_table(args.dbname, tuple(hotel_dict.values()))

dataFrame = pd.DataFrame(Scraped_info_list)
print('Creating csv file ...')
dataFrame.to_csv("Oyo.csv")
cnc.get_hotel_info(args.dbname)
