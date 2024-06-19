from typing import List

import xml.etree.ElementTree as et


async def generate_xml(product_data: List[dict]):
    root = et.Element('kaspi_catalog', date='string', xmlns='kaspiShopping', )
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.set('xsi:schemaLocation', 'kaspiShopping http://kaspi.kz/kaspishopping.xsd')
    company = et.SubElement(root, 'company')

    merchantid = et.SubElement(company, 'merchantid')
    merchantid.text = str(111)

    offers = et.SubElement(company, 'offers')

    for product in product_data:
        offer = et.SubElement(offers, 'offer', sku=str(product.get('id')))
        model = et.SubElement(offer, 'model')
        model.text = product.get('name')
        availabilities = et.SubElement(offer, 'availabilities')

        if product.get('quantity') > 0:
            available = 'yes'
        else:
            available = 'no'

        availability = et.SubElement(availabilities, 'availability', available=available, storeID=str(product.get('shop_id')))
        cityprices = et.SubElement(offer, 'cityprices')
        cityprice = et.SubElement(cityprices, 'cityprice', cityID=f'')
        cityprice.text = str(product.get('price'))

    xml_data = et.tostring(root, encoding='utf-8').decode()
    return xml_data
