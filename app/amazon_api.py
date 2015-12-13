import bottlenose
import logging
import random
import time

from bs4 import BeautifulSoup
from dateutil import parser

from .models import Settings

logger = logging.getLogger('product_advertising_api')

class ProductAdvertisingAPI(object):
    """
    A wrapper class for the necessary Amazon Product Advertising API calls.
    See the API reference here: http://docs.aws.amazon.com/AWSECommerceService/latest/DG/CHAP_ApiReference.html
    See bottlenose here: https://github.com/lionheart/bottlenose
    """
    def __init__(self):
        amazon_credentials = Settings.query.all()[-1]

        self.amazon = bottlenose.Amazon(
            str(amazon_credentials.Access_key_ID),
            str(amazon_credentials.Secret_Access_key),
            str(amazon_credentials.Amazon_user),
            Region='US',
            Parser=lambda response_text: BeautifulSoup(response_text, 'lxml'),
        )

    @staticmethod
    def __get_item_attribute(item, attribute):
        """
        Returns the attribute value from a bs4 parsed item.
        :param item: bs4 item returned from PA API upon item lookup
        :param attribute: the attribute to search for
        :return: the value if found, else None
        :rtype: basestring
        """
        value = item.itemattributes.find_all(attribute, recursive=False)
        return value[0].string if len(value) == 1 else None

    @staticmethod
    def format_datetime(value):
        """
        Formats the given value if it is not None in the given format.
        :param value: the value to format
        :type value: basestring
        :return: formatted datetime
        :rtype: basestring
        """
        if value is not None:
            try:
                return parser.parse(value)
            except ValueError:
                logger.error('Unable to parse %s to a datetime', value)
                return None

    @staticmethod
    def handle_error(error):
        """
        Generic error handler for bottlenose requests.
        @see https://github.com/lionheart/bottlenose#error-handling
        :param error: error information
        :type error: dict
        :return: if to retry the request
        :rtype: bool
        :
        """
        ex = error['exception']

        logger.error(
            'Error was thrown upon requesting URL %(api_url)s (Cache-URL: %(cache_url)s: %(exception)r' % {
                'api_url': error['api_url'],
                'cache_url': error['cache_url'],
                'exception': ex,
            }
        )

        # try reconnect
        if isinstance(ex, HTTPError) and ex.code == 503:
            time.sleep(random.expovariate(0.1))
            return True

        return False

    def lookup_at_amazon(self, item_ids):
        """
        Outsourced this call to better mock in tests.
        :param item_ids: the item ids
        :type item_ids: list
        :return: parsed xml
        :rtype: bs4.BeautifulSoup
        """
        return self.amazon.ItemLookup(ItemId=','.join(item_ids),ResponseGroup='Large')

    def item_lookup(self, item_ids):
        """
        Lookup of the item with the given id on Amazon. Returns it values or None if something went wrong.
        :param item_ids: the item ids
        :type item_ids: list
        :return: the values of the item
        :rtype: dict
        """
        logger.info('starting lookup for ASINs %s', ', '.join(item_ids))
        item_response = self.lookup_at_amazon(item_ids)

        if getattr(item_response, 'items') is None:
            logger.error(
                'Request for item lookup (ASINs: %s) returned nothing',
                ', '.join(item_ids),
            )
            return None

        if item_response.items.request.isvalid.string == 'True':

            # the dict that will contain a key for every ASIN and as value the parsed values
            product_values = dict()
            for item_node in item_response.find_all(['item']):

                # parse the values
                item_values = {
                    'asin': item_node.asin.string,
                    'title': item_node.itemattributes.title.string,
                    'artist': item_node.itemattributes.artist.string if item_node.itemattributes.artist is not None else None,
                    'isbn': self.__get_item_attribute(item_node, 'isbn'),
                    'eisbn': self.__get_item_attribute(item_node, 'eisbn'),
                    'date_publication': self.format_datetime(self.__get_item_attribute(item_node, 'publicationdate')),
                    'date_release': self.format_datetime(self.__get_item_attribute(item_node, 'releasedate')),
                    'offer_url': "http://www.amazon.com/dp/"+item_node.asin.string,
                }

                # check if there are offers, if so add price
                if item_node.offers is not None and int(item_node.offers.totaloffers.string) > 0:
                    try:
                        item_values['price'] = float(item_node.offers.offer.offerlisting.price.amount.string) / 100
                        item_values['currency'] = item_node.offers.offer.offerlisting.price.currencycode.string
                    except:
                        item_values['price'] = -1
                lowestnewprice=None

                if item_node.find("listprice"):
                    list_price = float(item_node.find("listprice").amount.string)/100
                    if list_price<item_values.get('price'):
                        item_values['price'] = list_price
                if item_node.find("saleprice"):
                    sale_price = float(item_node.find("saleprice").amount.string)/100
                    if sale_price<item_values.get('price'):
                        item_values['price'] = sale_price

                if not item_values.get('price'):
                    item_values['price'] = -1
                product_values[item_values['asin']] = item_values

            # check if all ASINs are included, if not write error message to log
            failed_asins = []
            for asin in item_ids:
                if asin not in product_values.keys():
                    failed_asins.append(asin)

            if failed_asins:
                logger.error('Lookup for the following ASINs failed: %s', ', '.join(failed_asins))

            # if there is at least a single ASIN in the list, return the list, else None
            return None if len(product_values) == 0 else product_values

        else:
            logger.error(
                'Request for item lookup (ASINs: %s) was not valid',
                ', '.join(item_ids),
            )
            return None
