import OCR
import DB
import BOT
import config


bot = BOT()

def scanAndOrganize():
    slotIn = bot.checkInput()
    while not (slotIn == 0):
        bot.move(slotIn[0], slotIn[1], config.scan[0], config.scan[1])
        id = OCR.getCardId()
        slot = DB.selectSlotToPlace(DB.divideByPrice(id))
        bot.move(config.scan[0], config.scan[1], slot[0], slot[1])
        DB.add(slot[0], slot[1], id)
        slotIn = bot.checkInput()
        
def takeCard(name, set = 0):
    if 




#update tables:

#DB_OCR.deletetables()
#DB_OCR.create(sizeX, sizeY)

