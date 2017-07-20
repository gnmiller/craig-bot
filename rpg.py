import random
from craig_helper import dice
from math import ceil, floor

classes = ["Warrior","Cleric","Rogue","Ranger","Wizard"]

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
    
    def gen_hp( d ):
        hp = 0
        for i in range( 0,3 ):
            hp += dice[d]
        return hp
    
    def to_next():
        return self.lvl * 1000
    
    def check_class( _class ):
        for i in range( len(classes) ):
            if self._class.lower() == classes[i].lower():
                return i
        return -1
    
    def attk():
        dmg = random.randint( 1, dice[1] )
        dmg *= self.atk
        dmg = ceil(dmg)
        return dmg
    
    def special( target ):
        if self.check_class( self._class ) == 0:
            # restore self HP my MAG * 10% HP
            if self.hp <= 0:
                return
            self.hp += ceil(self.mag * ceil(0.1*self.max_hp))
            return 0
        if self.check_class( self._class ) == 1:
            # restore hp by 2MAG * 10% of target HP -- set to 105 if theyre dead
            if target.hp < 0:
                target.hp = ceil(target.max_hp * .1)
                return
            target.hp *= ceil(self.mag*2.0) * ceil(target.max_hp*.1)
            return 1
        if self.check_class( self._class ) == 2:
            # backstab!
            dmg = self.attk()
            dmg += self.attk()
            target.hp -= dmg
            return 2 
        if self.check_class( self._class ) == 3:
            # flurry
            dmg = 0
            for i in range( 0,8 ):
                t_dmg = self.attk()
                dmg += floor( t_dmg/2.0 )
            target.hp -= dmg
            return 3
        if self.check_class( self._class ) == 4:
            # fireball!
            dmg = random.randint( 1, dice[1] )
            dmg *= self.atk
            dmg = ceil(dmg)
            return 4
        return -1