import random
from craig_helper import dice
from math import ceil, floor

classes = ["warrior","cleric","rogue","ranger","wizard"]
monsters = ["goblin","orc","troll","giant"]

def attack( source, target ):
    dmg = random.randint( 1, dice[1] )
    dmg *= source.atk
    dmg = ceil(dmg)
    target.hp -= dmg
    return dmg

def special_attack( source, target ):
    if source.check_class( source._class ) == 0:
        # restore self HP my MAG * 10% HP
        if source.hp <= 0:
            return
        self.hp += ceil(source.mag * ceil(0.1*source.max_hp))
        return 0
    if source.check_class( source._class ) == 1:
        # restore hp by 2MAG * 10% of target HP -- set to 105 if theyre dead
        if target.hp <= 0:
            target.hp = ceil(target.max_hp * .1)
            return
        target.hp *= ceil(source.mag*2.0) * ceil(target.max_hp*.1)
        return 1
    if source.check_class( source._class ) == 2:
        # backstab! -- double dmg
        dmg = attack( source, target )
        target.hp -= dmg
        return 2 
    if source.check_class( source._class ) == 3:
        # flurry 8x attacks for 1/2 dmg ea
        dmg = 0
        for i in range( 0,7 ):
            t_dmg = random.randint( 1, dice[1] )
            dmg += ceil( t_dmg/2.0 )
        target.hp -= dmg
        return 3
    if source.check_class( source._class ) == 4:
        # fireball!
        dmg = random.randint( 1, dice[1] )
        dmg *= source.atk
        dmg = ceil(dmg)
        target.hp -= dmg
        return 4
    return -1

class player:
    def __init__( self, _class ):
        self._class = _class
        self.lvl = 1
        self.exp = 0
        if self.check_class( _class ) == 0:
            self.atk = 7.5
            self.mag = 2.5
            self.max_hp = self.gen_hp( 2 )
        if self.check_class( _class ) == 1:
            self.atk = 5.0
            self.mag = 5.0
            self.max_hp = self.gen_hp( 0 )
        if self.check_class( _class ) == 2:
            self.atk = 12.5
            self.mag = 2.5
            self.max_hp = self.gen_hp( 1 )
        if self.check_class( _class ) == 3:
            self.atk = 10.0
            self.mag = 2.5
            self.max_hp = self.gen_hp( 1 )
        if self.check_class( _class ) == 4:
            self.atk = 2.0
            self.mag = 10.0
            self.max_hp = self.gen_hp( 0 )
        self.hp = self.max_hp
        return
    
    def gen_hp( self, d ):
        hp = 0
        for i in range( 0,3 ):
            hp += dice[d]
        return hp*2
    
    def to_next( self ):
        return self.lvl * 1000
    
    def check_class( self, _class ):
        for i in range( len(classes) ):
            if self._class.lower() == classes[i].lower():
                return i
        return -1
    
class monster:
    def __init__( self, kind, hp, atk ):
        self.max_hp = hp
        self.kind = kind
        self.atk = atk