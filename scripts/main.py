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
        
        




def sortFinds(inp):
    return sorted(inp, key=lambda x: (x[0], x[1], x[2]))
        
def takeCards(cards):
    
    slotOut = bot.checkOutput()
    
    spots = []
    for i in range(len(cards)):
        targets = DB.searchIds(config.sizeX, config.sizeY, cards[i][0])
        results = []

        step = 0
        for j in range(len(cards)):
            if cards[j] == cards[i] and not j == i:
                step += 1

        i += step

        for id in targets:
            ids = DB.searchDB(id, config.sizeX, config.sizeY)
            x = -1
            for line in ids:
                x += 1
                y = -1
                for list in line:
                    y += 1
                    results.append([x, y, place] for place in list)
        if step > len(results):
            step = len(results)
        spots.extend(results[:step+1])


    results = sortFinds(spots)
    
    for i in range(len(results)):
        x, y, place = results[i]
        bot.thinUntil(x, y, place)
        bot.moveCard(x, y, slotOut[0], slotOut[1])
        try:
            if results[i+1][0] == results[i][0] and results[i+1][1] == results[i][1]:
                continue 
        except:
            pass
        bot.dump(x, y)
    

def single(buf):
    if '\n' in buf:
        buf = buf.split("\n")
        cards = [(int(s.split(' ', 1)[0]), s.split(' ', 1)[1]) for s in buf]
    else:
        cards = split_strings = [(int(buf.split(' ', 1)[0]), buf.split(' ', 1)[1]) if buf[0].isdigit() else (1, buf)]

    targets = []
    for card in cards:
        targets.extend( [card[1]] * card[0] )

    targets = sorted(targets)

    takeCards(targets)



#update tables:

#DB_OCR.deletetables()
#DB_OCR.create(sizeX, sizeY)

