import OCR
import DB
import BOT
import config


bot = BOT()

def scanAndOrganize():
    slotIn = bot.checkInput()
    while not (slotIn == 0):
        bot.moveCard(slotIn[0], slotIn[1], config.scan[0], config.scan[1])
        id = OCR.getCardId()
        slot = DB.selectSlotToPlace(DB.divideByPrice(id))
        bot.moveCard(config.scan[0], config.scan[1], slot[0], slot[1])
        DB.add(slot[0], slot[1], id)
        slotIn = bot.checkInput()
        
        

def takeCard(name, set = None):
    out = selectOutput()
    targets = DB.searchIds(config.sizeX, config.sizeY, name, set)
    results = []
    for id in targets:
        ids = DB.searchDB(id, config.sizeX, config.sizeY)
        x = -1
        for line in ids:
            x += 1
            y = -1
            for list in line:
                y += 1
                results.append([x, y, place] for place in list)
                
    results = sortFinds(results)
    
    for i in range(len(results)):
        x, y, place = results[i]
        bot.thinUntil(x, y, place)
        bot.moveCard(x, y, out[0], out[1])
        try:
            if results[i+1][0] == results[i][0] and results[i+1][1] == results[i][1]:
                continue 
        except:
        bot.dump(x, y)

        




#update tables:

#DB_OCR.deletetables()
#DB_OCR.create(sizeX, sizeY)

