import mysql.connector
import sys
import json
import cv2
import pytesseract
from collections import defaultdict
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
import string
import re
import numpy as np



    # Connect to MariaDB
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    database="mysql"
)
cursor = conn.cursor()
    # Create a cursor object to execute SQL commands
    #return conn.cursor(), conn






def getCardNumber(buffer):
    filters = {}
    
    filters["number"], filters["`set`"] = buffer
        
    query = "SELECT id FROM allcards WHERE "
    conditions = []
    for key, value in filters.items():
        conditions.append(f"{key} = \'{value}\'")
    
    query += " AND ".join(conditions)
    print(query)

    cursor.execute(query)

    # Fetch the result (assuming only one ID is expected)
    return cursor.fetchone()[0]
    

    
def getNameFromId(id):
    query = f"SELECT name FROM allcards WHERE id = \'{id}\'"

    cursor.execute(query)

    # Fetch the result (assuming only one ID is expected)
    return (cursor.fetchone()[0])  
  
def getRarityFromId(id):
    query = f"SELECT rarity FROM allcards WHERE id = \'{id}\'"

    cursor.execute(query)

    # Fetch the result (assuming only one ID is expected)
    return (cursor.fetchone()[0]) 
   
def getSetFromId(id):
    query = f"SELECT `set` FROM allcards WHERE id = \'{id}\'"

    cursor.execute(query)

    # Fetch the result (assuming only one ID is expected)
    return (cursor.fetchone()[0])
    
def getPriceFromId(id):
    query = f"SELECT price FROM allcards WHERE id = \'{id}\'"

    cursor.execute(query)

    # Fetch the result (assuming only one ID is expected)
    return (cursor.fetchone()[0])
    
    
    

# set/reset DB

def deletetables():
    try:
        # Get the list of tables in the database
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        # Iterate through the tables and drop each one
        for table in tables[0:-1]:
            table_name = table[0]
            drop_table_query = f"DROP TABLE {table_name}"
            cursor.execute(drop_table_query)
        
        # Commit changes to the database
        conn.commit()
        
        print("All tables dropped successfully!")

    except mysql.connector.Error as e:
        print(f"Error: {e}")


def create(x, y):
    try:
        # Create the parent table to hold child table names
        create_parent_table_query = """
        CREATE TABLE ParentTable (
            id INT AUTO_INCREMENT PRIMARY KEY,
            table_name VARCHAR(255),
            rarity VARCHAR(50)
        )
        """
        cursor.execute(create_parent_table_query)

        # Create child tables dynamically
        for i in range(x):
            for j in range(y):
                table_name = f"slot{i}{j}"
                create_child_table_query = f"""
                CREATE TABLE {table_name} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255)
                )
                """
                cursor.execute(create_child_table_query)

                # Insert the child table name into the parent table
                insert_table_name_query = f"""
                INSERT INTO ParentTable (table_name, rarity) VALUES ('{table_name}', 'n')
                """
                cursor.execute(insert_table_name_query)
                
                
        with open(datafile, encoding='utf-8') as f:
            data = json.load(f)

        # Extract important data
        important_data = []
        tokens_data = []
        for item in data:
                
            if not (item['layout'] == "reversible_card") and not (item['oversized'] == True) and (item['frame']== "2015") and not (item["layout"] == "art_series") and not(item["digital"]) and not(item["promo"]) and not (item["set"] == "plst") and not ("\u2605" in item["collector_number"]):
                
                
                if item["nonfoil"]:
                    important_data.append([item['name'], item['rarity'][0], item['set'], item['collector_number'], item["prices"]["eur"] if item["prices"]["eur"] else item["prices"]["usd"]]) 
                else:
                    important_data.append([item['name'], item['rarity'][0], item['set'], item['collector_number'], item["prices"]["eur_foil"] if item["prices"]["eur_foil"] else item["prices"]["usd_foil"]]) 
                
        
        create_table_query = """
        CREATE TABLE allcards (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            rarity VARCHAR(50),
            `set` VARCHAR(50),
            number VARCHAR(50),
            price VARCHAR(50),
            UNIQUE(number, `set`)
        )
        """
        cursor.execute(create_table_query)
        with open("out", "w", encoding="utf-8") as sys.stdout:
            for data in important_data:
                print(data)
        # Insert data into the table
        insert_query = "INSERT IGNORE INTO allcards (name, rarity, `set`, number, price) VALUES (%s, %s, %s, %s, %s)"
        cursor.executemany(insert_query, important_data)
        

        # Commit changes to the database
        conn.commit()

        print("Tables created successfully!")

    except mysql.connector.Error as e:
        print(f"Error creating tables: {e}")



# change DB

def add(x, y, element_name):
    try:
        table_name = f"slot{x}{y}"
        # Construct the INSERT query
        insert_query = f"INSERT INTO {table_name} (name) VALUES ('{element_name}')"

        # Execute the INSERT query
        cursor.execute(insert_query)

        # Commit changes to the database
        conn.commit()

        print(f"Element '{element_name}' added to {table_name} successfully!")

    except mysql.connector.Error as e:
        print(f"Error adding element: {e}")


def delete(x, y):
    try:
        table_name = f"slot{x}{y}"
        max_id_query = f"SELECT id, name FROM {table_name} WHERE id = (SELECT MAX(id) FROM {table_name})"
        cursor.execute(max_id_query)
        max_id, element_name = cursor.fetchone()

        if max_id is not None:
            # Delete the row with the maximum ID
            delete_query = f"DELETE FROM {table_name} WHERE id = {max_id}"
            cursor.execute(delete_query)
            
            reset_auto_increment_query = f"ALTER TABLE {table_name} AUTO_INCREMENT = 1"
            cursor.execute(reset_auto_increment_query)
            # Commit changes to the database
            conn.commit()

            print(f"Deleted {element_name} from {table_name} successfully!")
            
            return element_name
        else:
            print(f"No elements found in {table_name}")

    except mysql.connector.Error as e:
        print(f"Error deleting element: {e}")


def move(fromX, fromY, toX, toY):
    add(toX, toY, delete(fromX, fromY))
    print(f"Move sucessful")



# find in DB


# deals with how slots are used. ids:
# c - commons
# u - uncommons
# r - rares
# m - mythic
# p - promo
# vc - valuable common (+30c)
# vu - valuable uncommon (+30c)
# vr - valuable rare (+50c)
# vm - valueable mythic (+1e)
# e - error

def slotRarity(rarity):
    query = f"SELECT table_name FROM ParentTable WHERE rarity = {rarity}"
    cursor.execute(query)
    result = cursor.fetchall()
    return result

def selectSlotToPlace(rarity):
    slots = slotRarity(rarity)
    slot = ""
    for i in slots:
        query = f"SELECT COUNT(*) FROM {i}"
        cursor.execute(query)

        # Fetch the result
        if (int(cursor.fetchone()[0]) < 200):
            return slot
    
    slots = slotRarity("n")

    update_query = f"""
    UPDATE ParentTable 
    SET column1 = {rarity} 
    WHERE table_name = {slots[0]};
    """
    cursor.execute(update_query)

    # Commit the transaction
    conn.commit()

    return slots[0]
    
def divideByPrice(id):
    query = f"SELECT rarity, price FROM allcards WHERE id = {id}"
    cursor.execute(query)
    rarity, price = cursor.fetchone()
    if price == None: return "e"
    price = float(price)
    match rarity:
        case "c": return "c" if price < 0.3 else "vc"
        case "u": return "u" if price < 0.3 else "vu"
        case "r": return "r" if price < 0.5 else "vr"
        case "m": return "m" if price < 1 else "vm"
        case "e": return rarity
        case "p": return rarity



 

def searchSlot(x, y, element_name):
    try:
        table_name = f"slot{x}{y}"
        select_query = f"SELECT id FROM {table_name} WHERE name = '{element_name}'"
        cursor.execute(select_query)

        # Fetch all rows from the result set
        rows = cursor.fetchall()

        if rows:
            # Extract IDs from the result set
            element_ids = [row[0] for row in rows]
            print(f"Found in {table_name}: {element_ids}")
            return element_ids
        else:
            print(f"No elements with name '{element_name}' found in {table_name}")
            return []

    except mysql.connector.Error as e:
        print(f"Error finding elements: {e}")
        return []


def searchDB(element_name):    
    # List to store the result for each table
    result = []

    # Iterate over each child table
    for x in range(sizeX):
        res = []
        for y in range(sizeY):

            # Call searchSlot function for each table
            element_ids = searchSlot(x, y, element_name)

            # Append the result to the list
            res.append(element_ids)
        result.append(res)
    print(result)
    return result


def inDB(element_name):
    found = searchDB(element_name)
    res = 0
    for line in found:
        for slot in line:
            res += len(slot)
    print(f"Found {res} cards in DB!")



# show DB

def show(x, y):
    try:
        table_name = f"slot{x}{y}"
        # Select all elements from the child table
        select_query = f"SELECT * FROM {table_name}"
        cursor.execute(select_query)

        # Fetch all rows from the result set
        rows = cursor.fetchall()

        if rows:
            print(f"Cards in {table_name}:")
            for row in rows:
                print(row)
        else:
            print(f"No cards found in {table_name}")

    except mysql.connector.Error as e:
        print(f"Error printing elements: {e}")


def showTables():
    try:        
        for x in range(sizeX):
            for y in range(sizeY):
                show(x, y)
                print()  # Add a newline for better readability

    except mysql.connector.Error as e:
        print(f"Error showing elements: {e}")


def listDB():
    try:   
        print("All cards in DB:")
        print("")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        # List to store all elements
        all_elements = []

        # Iterate over each child table
        for x in range(sizeX):
            for y in range(sizeY):
                table_name = f"slot{x}{y}"

                # Select all elements from the current table
                select_query = f"SELECT name FROM {table_name}"
                cursor.execute(select_query)

                # Fetch all rows from the result set
                rows = cursor.fetchall()

                # Append all elements from the current table to the list
                all_elements.extend(rows)
            
        listed = defaultdict(int)
        
        for card in all_elements:
            listed[card] += 1
        
        for card in listed:
            print(f"{card[0]}: {listed[card]}")
        
        return listed
    
    except mysql.connector.Error as e:
        print(f"Error fetching all elements from all tables: {e}")
        return []




datafile = "C:\\Users\\tiago\\Documents\\COde\\default-cards-20240504090539.json"


deletetables()
create(3, 3)


datafile = "C:\\Users\\tiago\\Documents\\COde\\default-cards-20240504090539.json"


# test stuff
"""
with open('out', 'w') as sys.stdout:
    with open('in', 'r') as sys.stdin: 

        while not inputl == "q":
            try:
                inb = input().split()
                inputl = inb[0]
                match inputl:
                    case "a": add(inb[1], inb[2], inb[3])
                    case "d": delete(inb[1], inb[2])
                    case "m": move(inb[1], inb[2], inb[3], inb[4])
                    case "s": show(inb[1], inb[2])
                    case "r":
                        deletetables()
                        create(sizeX, sizeY)
                    case "sa": showTables()
                    case "f": searchDB(inb[1])
                    case "i": inDB(inb[1])
                    case "l": listDB()
            except:
                print("Wrong Input")
            
            print("")
                

# clear stuff

cursor.close()
conn.close()

"""