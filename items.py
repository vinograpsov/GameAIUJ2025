import combat

def LoadItems(file):
    itemObjects = [];
    items = open(file, "r")
    if items == None:
        print("DebugError: cannot find file " + file)

    curItem = None;
    #itemObjects.append(curItem);
    
    itemHeader = ['', '', '']
    for line in items:
        lineData = line.split();
        if len(lineData) == 0:
            continue
        #if (lineData[0] == )
        if (lineData[0] == 'name:'):
            for rest in lineData:
                if rest != lineData[0]:
                    itemHeader[0] += rest + ' '
            #itemHeader[0] = lineData[1]
        elif (lineData[0] == 'desc:'):
            for rest in lineData:
                if rest != lineData[0]:
                    itemHeader[1] += rest + ' '
        elif (lineData[0] == 'image:'):
            itemHeader[2] = lineData[1]
            #finds all headers so initiates item
            curItem = Item(itemHeader[0], itemHeader[1], itemHeader[2])
            itemHeader = ['', '', ''] #clear header
            itemObjects.append(curItem)
        else:
           stat = lineData[0]
           #curItem.stats.get(lineData[0])
           form = [0]
           for i in range(len(lineData)):
               if i == 0:
                   pass
                   #stat = lineData[i]
               elif i == 1:
                   if lineData[i] == '+':
                       form[0] = 0
                   elif lineData[i] == '*':
                       form[0] = 1
               else:
                   form.append(float(lineData[i]))
           
           #print(curItem.stats.get(stat))
           try:
               curItem.stats.get(stat).append(form)
           except:
               pass
           #curItem.stats.get(stat).append(form)

    return itemObjects

#template
#def __init__(self, acc, recoil, vel, size, dmg, range, delay, recharge, multishot, ammo):

class Item():
    def __init__(self, name, desc, image):
        self.gameObject = None;
        self.name = name
        self.desc = desc
        self.image = image
        self.stats = { #stats are having form of [type(int), val], and also: [type, val, val2] than we know it is a range
            'hp': [], 'size': [], 'speed': [], 'brk': [], 'steer': [], 'acc': [], 'rec' : [], 'vel': [], 'bsize': [], 'dmg': [], 'range': [], 'delay': [], 'recharge': [], 'mult': [], 'ammo': []
            } #type 0 in stats means + type 1 means *

    def ApplyEffects(self, stat, effects):

        for effect in effects:
            if len(effect) > 2:
                if effect[0] == 0:
                    stat.rangeAddons.append([effect[1], effect[2]])
                elif effect[0] == 1:
                    stat.rangeMultipliers.append([effect[1], effect[2]])
            else:
                if effect[0] == 0:
                    stat.addons.append(effect[1])
                elif effect[0] == 1:
                    stat.multipliers.append(effect[1])
        
        stat.PreupdateModifiers()
        stat.UpdateModifiers()

    def ApplyItem(self, ship, guns):

        #part for ship
        self.ApplyEffects(ship.maxhp, self.stats['hp'])
        self.ApplyEffects(ship.size, self.stats['size'])
        self.ApplyEffects(ship.speed, self.stats['speed'])
        self.ApplyEffects(ship.brk, self.stats['brk'])
        self.ApplyEffects(ship.steer, self.stats['steer'])

        #and now for weapons:
        for gun in guns:
            self.ApplyEffects(gun.acc, self.stats['acc'])
            self.ApplyEffects(gun.recoil, self.stats['rec'])
            self.ApplyEffects(gun.vel, self.stats['vel'])
            self.ApplyEffects(gun.size, self.stats['bsize'])
            self.ApplyEffects(gun.dmg, self.stats['dmg'])
            self.ApplyEffects(gun.range, self.stats['range'])
            self.ApplyEffects(gun.delay, self.stats['delay'])
            self.ApplyEffects(gun.recharge, self.stats['recharge'])
            self.ApplyEffects(gun.multishot, self.stats['mult'])
            self.ApplyEffects(gun.ammo, self.stats['ammo'])

        #yes this function is a great piece of code, really smart...