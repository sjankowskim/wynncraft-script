import os
from bs4 import BeautifulSoup

class Item:
    def __init__(self, name, rarity, lvlReq, statName, stat, statUnit, guaranteed, tradeable, link):
        self.name = name
        self.rarity = rarity
        self.lvlReq = lvlReq
        self.statName = statName
        self.stat = stat
        self.statUnit = statUnit
        self.tradeable = tradeable
        self.guaranteed = guaranteed
        self.link = link
    
    def toString(self):
        return "(" + self.name + " : " + self.rarity + ") Level Req: " + str(self.lvlReq) + ", " + self.statName + ": " + str(self.stat) + str(self.statUnit) + "\n\tTradeable? " + str(self.tradeable) + ", Guaranteed? " + str(self.guaranteed)
    
categories = ["Helmet", "Chestplate", "Leggings", "Boots", "Dagger", "Wand", "Bow", "Spear", "Relik", "Ring", "Bracelet", "Necklace"]
statToSortBy = "XP Bonus"

for category in categories:
    print("<===== " + category + " =====>")
    # Makes a curl call to the wynndata page and saves the output to a temporary text file
    os.system("curl \"https://www.wynndata.tk/items/\" -X POST --data-raw \"search=&name=&category=type-" + category + "&tier=any&profession=any&min=1&max=130&order1=level&order2=xpBonus&order3=null&order4=null\" --output temp.txt")
    items = []

    soup = BeautifulSoup(open('temp.txt', 'r', errors='ignore').read(), 'html.parser')
    for div in soup.findAll(class_=['itembox macrocategory-items']):
        # Check if an item is still obtainable
        if div.find(class_='dropTypeIcon').find('img').attrs['src'] in {'/assets/images/dropType/discontinued.png', '/assets/images/dropType/unobtainable.png'}:
            continue
        
        # Finds the name of the item entry
        name = div.find('p').text
        
        # Finds the rarity of the item
        rarity = div.find(class_='header').find('p')['class'][1]
        
        # If the category is a weapon, we need to skip over the first checkmark entry
        # because that entry indicates the class the weapon is locked to instead of the
        # minimum combat level
        if category in {"Dagger", "Wand", "Bow", "Spear", "Relik"}:
            lvlReq = int(''.join(c for c in div.findAll(class_='emoji emoji-checkmark')[1].text if c.isdigit()))
        else:
            lvlReq = int(''.join(c for c in div.find(class_='emoji emoji-checkmark').text if c.isdigit()))
        
        # Grabs the stat name we are looking for
        statName = statToSortBy
        
        # Finds that stat of the item entry
        stat = 0
        statUnit = ''
        guaranteed = True
        offset = 0
        for statEntry in div.find('tbody').findAll('tr'):
            # Checks if the item has min/max columns or just a value column
            if div.find('thead').findAll('th')[1].text != "Value":
                offset = 1
                guaranteed = False
            
            # Breaks down each stat into it's min/name/max or name/value values
            values = statEntry.findAll('td') 
            
            # If the name value of the stat is the stat we are looking for,
            # grab the stat as an integer and stop looping
            if values[0 + offset].text == statToSortBy:
                stat = int(''.join(c for c in values[1 + offset].text if c.isdigit() or c == '-'))
                statUnit = str(''.join(c for c in values[1 + offset].text if not c.isdigit() and not c == '-'))
                break
        
        # Determines if the item is tradeable or not
        tradeable = True
        if not div.find(class_='restrictions') is None:
            tradeable = False
            
        # Grabs the link to the item's page
        link = "https://www.wynndata.tk" + div.find(class_='more-details').find('a')['href']
        
        # Use the data we found to add an Item to the list    
        items.append(Item(name, rarity, lvlReq, statToSortBy, stat, statUnit, guaranteed, tradeable, link))

    items.reverse()
    currItemMax = items[0]
    i = 1
    while i < len(items):
        if items[i].stat >= currItemMax.stat:
            if items[i].stat > currItemMax.stat and items[i].lvlReq == currItemMax.lvlReq:
                items.remove(currItemMax)
                currItemMax = items[i - 1]
            else:
                currItemMax = items[i]
                i += 1
        else:
            items.remove(items[i])

    for item in items:
        print(item.toString())

        
