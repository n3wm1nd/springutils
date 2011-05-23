import unittest
import lupa

import os
import sys


bla = (None,)*1000 #workaround for lupa bug

def newlua():
  lua = lupa.LuaRuntime()
  lua.execute("""
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
  return lua




units = {}
weapons = {}
moveclasses = {}
buildable=set()

def loadunits(springpath):
  lua = newlua()
  # read unit files
  unitdir = os.path.join(springpath,"units")
  for filename in os.listdir(unitdir):
    with open( os.path.join(unitdir,filename),"r") as unitfile:
      if os.path.splitext(filename)[1] == ".lua":
        try:
          units.update( lua.execute(unitfile.read()) )
        except lupa.LuaError:
          print "syntax error reading file: "+filename
      else:
        pass
        print "not scanning "+filename 

weapons = {}
def loadweapons(springpath):
  lua = newlua()
  # read unit files
  weaponsdir = os.path.join(springpath,"weapons")
  for filename in os.listdir(weaponsdir):
    with open( os.path.join(weaponsdir,filename),"r") as weaponfile:
      if os.path.splitext(filename)[1] == ".lua":
        try:
          weapons.update( lua.execute(weaponfile.read()) )
        except lupa.LuaError:
          print "syntax error reading file: "+filename
      else:
        print "not scanning "+filename 

def loadmovedata(springpath):
  lua = newlua()
  movedatafilename=os.path.join(springpath,"gamedata/movedefs.lua")
  with open( movedatafilename,"r") as movedatafile:
    movedatalist = lua.execute(movedatafile.read())
    for n, movedata in movedatalist.items():
      moveclasses[movedata.name] = movedata

def updatebuildable(springpath,startingset):
  lua = newlua()
  
  tocheck = set(startingset)
  morph={}
  with open(os.path.join(springpath,"luarules/configs/morph_defs.lua"),"r") as md:
    morphdefs = lua.execute(md.read())
    for u,t in morphdefs.items():
      morph[u]=set()
      if "into" in t:
        morph[u].add( t.into.lower() ) #should be fixed in source
      else:
        for _,t in t.items():
          morph[u].add( t.into.lower() )  #same here
  while len(tocheck):
    check = tocheck.pop()
    #print "adding "+check
    buildable.add(check)
    if units[check].buildoptions:
      tocheck |= set(units[check].buildoptions.values())-buildable
    if check in morphdefs:
      tocheck |= morph[check]
 
  #print buildable


class TestUnit(unittest.TestCase):
  def __init__(self,unit,methodname='runTest'):
    self.unit = unit
    unittest.TestCase.__init__(self,methodname)

  def __repr__(self):
    return "TestUnit("+self.unit.unitname+")"

  def __str__(self):
    return self.__repr__()
  
  def test_mandatory(self):
    self.assertIn("category", self.unit)
    self.assertIn("objectname", self.unit)
    self.assertIn("side", self.unit)
    self.assertIn("unitname", self.unit)
    self.assertIn("buildtime", self.unit)
    self.assertIn("description", self.unit)
    self.assertIn("maxdamage", self.unit)
    self.assertIn("name", self.unit)
    self.assertIn("buildcostenergy", self.unit)
    self.assertIn("buildcostmetal", self.unit)
    self.assertIn("footprintx", self.unit)
    #self.assertIn("maxwaterdepth", self.unit)
    #self.assertIn("maxslope", self.unit)
    cats = self.unit.category.split(" ")
    #if not "VTOL" in cats and not "CTRL_V" in cats:
    #  self.assertIn("corpse", self.unit)
    #self.assertIn("movementclass", self.unit)

  def test_weapon(self):
    if self.unit.weapons == None: return
    #curweapon=1
    for weaponnum,unitweapon in self.unit.weapons.items():
      #self.assertEqual(curweapon,weaponnum,"weapon%d defined while weapon%d isn't" %(weaponnum,curweapon) )
      self.assertIn("def",list( unitweapon.keys() ))
      weaponname=unitweapon["def"].lower()
      self.assertIn(weaponname, self.unit.weapondefs)
      weapon=self.unit.weapondefs[weaponname]
      #curweapon+=1
      
      
  def test_categories(self):
    for cat in self.unit.category.split(" "):
      pass
      self.assertEqual(cat,cat.upper())


  def test_moveclass(self):
    #self.assertIn("movementclass",list(self.unit.keys()))
    if "movementclass" in self.unit:
      self.assertIn(self.unit.movementclass.upper(),moveclasses.keys())
      #self.assertIn(self.unit.movementclass,moveclasses.keys())

  def test_buildable(self):
    self.assertIn(self.unit.unitname, buildable, "not buildable")

  def test_corpsemetal(self):
    if self.unit.corpse:
      corpsename=self.unit.corpse.lower()
      try:
        corpse = self.unit.featuredefs[corpsename]
      except KeyError:
        return #checked elsewhere
      if corpse:
        self.assertIn("metal",corpse)
        self.assertTrue(corpse.metal <= self.unit.buildcostmetal)

  def test_corpse(self):
    if self.unit.corpse:
      corpsename=self.unit.corpse.lower()
      self.assertIn("featuredefs",self.unit,"no feature def in unit")
      self.assertIn(corpsename,self.unit.featuredefs,"corpse feature not defined")
      corpse = self.unit.featuredefs[corpsename]
      while corpse:
        self.assertIn("description",corpse,"%s: no description" % corpsename)
        self.assertIn("damage",corpse,"%s: no damage" % corpsename)
        self.assertIn("object",corpse,"%s: no object" % corpsename)
        self.assertIn("category",corpse,"%s: no category" % corpsename)
        self.assertTrue(corpse.category in ("corpses","arm_corpses","core_corpses","tll_corpses","dragonteeth","heaps","rocks"),"%s: wrong corpse category '%s'" % (corpsename, corpse.category) )

        try:
          corpsename = corpse.featuredead.lower()
        except AttributeError:
          corpsename = None
        # set the featurecorpse, go and test that
        corpse = self.unit.featuredefs[corpsename]


  
  def test_explosion(self):
    if "explodeas" in self.unit:
      self.assertIn(self.unit["explodeas"].lower(),weapons.keys())
    if "selfdestructas" in self.unit:
      self.assertIn(self.unit["selfdestructas"].lower(),weapons.keys())

  def test_buildoptions(self):
    if "buildoptions" in self.unit:
      for unitname in self.unit["buildoptions"].values():
        self.assertIn(unitname,units,"unit %s does not exist" % unitname)




class UnitTests(unittest.TestSuite):
  def __init__(self,unit,tests=()):
    unittest.TestSuite.__init__(self)
    if len(tests) == 0:
      tests = filter(lambda n: n.startswith('test_'), TestUnit.__dict__.keys())
    for tn in tests:
      t=TestUnit(unit,tn)
      self.addTest(t)
    

#weapon tests

# does [NOWEAPON] exist


class AllUnits(unittest.TestSuite):
  def __init__(self,tests=()):
    unittest.TestSuite.__init__(self)
    for unitname,unit in units.items():
      t = UnitTests(unit,tests)
      self.addTest(t)
        #print "add "+testname+" for "+unitname

class ModelsTests(unittest.TestCase):
  def setUp(self):
    modeldir = os.path.join(sys.argv[1],"objects3d")
    self.models = set( (m.lower().replace('.3do','') for m in os.listdir(modeldir)) )

  def test_unused(self):
    used = set()
    for _,u in units.items():
      used.add(u.objectname.lower())

      if "featuredefs" in u:
        for _,f in u.featuredefs.items():
          used.add(f.object.lower())
      if "weapondefs" in u:
        for _,w in u.weapondefs.items():
          if "model" in w:
            used.add(w.model.lower())

    for _,w in weapons.items():
      if "model" in w:
        used.add(w.model.lower())
    self.assertEqual(used,self.models )


if __name__ == '__main__':
  springdir=sys.argv[1]
  loadunits(springdir)
  print "units loaded"
  loadweapons(springdir)
  print "weapons loaded"
  loadmovedata(springdir)
  print "movedata loaded"
  updatebuildable( springdir, ('armcom','corcom','tllcom') )
  print "buildable"
  tests = sys.argv[2:] 

  suite = AllUnits(tests)
  
  #suite = unittest.TestSuite()
  #suite.addTest( ModelsTests('test_unused') )

  unittest.TextTestRunner(verbosity=1).run(suite)
  print "done"
