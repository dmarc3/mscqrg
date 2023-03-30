import os
from lxml import etree

DIR = os.path.dirname(__file__)
XML_PATH = os.path.join(DIR, "DataType_v20224.xml")

def get_cards():
    """Parses the DataTypes XML and provides list of all bulk data cards.

    Returns:
        list: List of bulk data cards
    """
    # Create XML doc
    doc = etree.parse(XML_PATH)
    groups = doc.find("groups")
    input = groups.find("group").find("group").findall("group")

    # Save all bulk data cards
    cards = []
    for card_type in input:
        for card in card_type.findall("group"):
            cards.append(card.get("name"))
        for card in card_type.findall("dataset"):
            cards.append(card.get("name"))
    return cards
