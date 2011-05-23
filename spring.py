import lupa

import os
import sys

import UserDict


class Mod(object):
  def __init__(self, moddir):
    self.dir = moddir
    self._lua = lupa.LuaRuntime()
    self._lua.execute("""
      function lowerkeys(t)
        local tn = {}
        for i,v in pairs(t) do
          local typ = type(i)
          if type(v)=="table" then
            v = lowerkeys(v)
          end
          if typ=="string" then
            tn[i:lower()] = v
          else
            tn[i] = v
          end
        end
        return tn
      end
      """)


  def getunit(self,unitname):
    unitdir = os.path.join(self.dir,"units")
    with open( os.path.join(unitdir,unitname+".lua"),"r") as unitfile:
      unitdata = self._lua.execute(unitfile.read().decode("latin1"))
      unit = Unit(unitname,mod=self)
      unit.__dict__.update(unitdata[unitname])
      return unit

  def getunits(self):
    unitdir = os.path.join(self.dir,"units")
    units = {}
    unitfiles = os.listdir(unitdir)
    unitfiles = filter( lambda u: u.endswith(".lua"), unitfiles)
    unitnames = [u.replace(".lua","") for u in unitfiles]
    for name in unitnames:
      units[name]=self.getunit(name)
    return units

  def getweapon(self,weaponname):
    weapondir = os.path.join(self.dir,"weapons")
    with open( os.path.join(weapondir,weaponname+".lua"),"r") as weaponfile:
      weapondata = self._lua.execute(weaponfile.read().decode("latin1"))
      weapon = Weapon(weapondata[weaponname])
      return weapon
  def getweapons(self):
    weapondir = os.path.join(self.dir,"weapons")
    weapons = {}
    weaponfiles = os.listdir(weapondir)
    weaponfiles = filter( lambda u: u.endswith(".lua"), weaponfiles)
    weaponnames = [u.replace(".lua","") for u in weaponfiles]
    for name in weaponnames:
      weapons[name]=self.getweapon(name)
    self.weapons=weapons
    return weapons

  def movedefs(self):
    movedatafilename=os.path.join(self.dir,"gamedata/movedefs.lua")
    moveclasses = {}
    with open( movedatafilename,"r") as movedatafile:
      movedatalist = self._lua.execute(movedatafile.read())
      for n, movedata in movedatalist.items():
        moveclasses[movedata.name] = movedata
    return moveclasses 

class Unit(object):
  def __init__(self,unitname,mod=None):
    self.unitname=unitname
    if mod:
      self.mod=mod
  def __repr__(self):
    return "Unit("+str(self.unitname)+")"

  def __getattribute__(self,name):
    try:
      if name in ['corpse']:
        featurename = self.__dict__[name].lower()
        return Feature(self.featuredefs[featurename])
      if name in ['weapons']:
        weapons = {}
        for wn,w in self.__dict__[name].items():
          w["def"] = Weapon(self.weapondefs[w["def"].lower()])
          weapons[wn] = w
    except KeyError:
      raise AttributeError()
    
    return object.__getattribute__(self,name)

class Ptr(object):
  data={}
  def __init__(self,initialdata={}):
    self.__dict__["data"] = initialdata

  def __getattr__(self,name):
    try:
      return self.data[name]
    except KeyError:
      raise AttributeError()

  def __setattr__(self,name,value):
    self.data[name]=value
    
  def __delattr__(self,name):
    del self.data[name]

class Feature(Ptr):
  pass
class Weapon(Ptr):
  pass



