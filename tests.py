import unittest
import spring

import os
import sys




def updatebuildable(mod,startingset):
  lua = mod._lua
  units = mod.getunits()
  
  buildable = set()
  tocheck = set(startingset)
  morph={}
  with open(os.path.join(mod.dir,"luarules/configs/morph_defs.lua"),"r") as md:
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
    try:
      tocheck |= set(units[check].buildoptions.values())-buildable
    except AttributeError:
      pass
    if check in morphdefs:
      tocheck |= morph[check]
 
  #print buildable
  return buildable


class TestUnit(unittest.TestCase):
  def __init__(self,unit,methodname='runTest'):
    self.unit = unit
    unittest.TestCase.__init__(self,methodname)

  def __repr__(self):
    return "TestUnit("+self.unit.unitname+")"

  def __str__(self):
    return self.__repr__()

  @classmethod
  def setUpClass(cls):
    cls.mod =  spring.Mod(sys.argv[1])
    cls.units =cls.mod.getunits()
    cls.weapons = cls.mod.getweapons()
    cls.buildable = updatebuildable(cls.mod,set(('armcom','corcom','tllcom')))
    cls.movedefs = cls.mod.movedefs()
 
  def test_mandatory(self):
    self.assertIn("category", self.unit.__dict__)
    self.assertIn("objectname", self.unit.__dict__)
    self.assertIn("side", self.unit.__dict__)
    self.assertIn("unitname", self.unit.__dict__)
    self.assertIn("buildtime", self.unit.__dict__)
    self.assertIn("description", self.unit.__dict__)
    self.assertIn("maxdamage", self.unit.__dict__)
    self.assertIn("name", self.unit.__dict__)
    self.assertIn("buildcostenergy", self.unit.__dict__)
    self.assertIn("buildcostmetal", self.unit.__dict__)
    self.assertIn("footprintx", self.unit.__dict__)
    #self.assertIn("maxwaterdepth", self.unit.__dict__)
    #self.assertIn("maxslope", self.unit.__dict__)
    cats = self.unit.category.split(" ")
    #if not "VTOL" in cats and not "CTRL_V" in cats:
    #  self.assertIn("corpse", self.unit.__dict__)
    #self.assertIn("movementclass", self.unit.__dict__)

  def test_weapon(self):
    #curweapon=1
    try:
      weapons = self.unit.weapons
    except AttributeError:
      return #no weapons defined
    for weaponnum,unitweapon in weapons.items():
      #self.assertEqual(curweapon,weaponnum,"weapon%d defined while weapon%d isn't" %(weaponnum,curweapon) )
      self.assertIn("def",list( unitweapon.keys() ))
      #curweapon+=1
      
      
  def test_categories(self):
    for cat in self.unit.category.split(" "):
      pass
      self.assertEqual(cat,cat.upper())


  def test_moveclass(self):
    #self.assertIn("movementclass",list(self.unit.keys()))
    try:
      movementclass = self.unit.movementclass 
    except AttributeError:
      return
    self.assertIn(movementclass.upper(),self.movedefs.keys())
      #self.assertIn(self.unit.movementclass,moveclasses.keys())

  def test_buildable(self):
    self.assertIn(self.unit.unitname, self.buildable, "not buildable")

  def test_corpsemetal(self):
    try:
      corpse = self.unit.corpse
    except AttributeError:
      return #checked elsewhere
    if corpse:
      self.assertTrue(corpse.metal <= self.unit.buildcostmetal)

  def test_corpse(self):
    try:
      corpse=self.unit.corpse
    except AttributeError:
      return

    corpsename = self.unit.__dict__["corpse"].lower()

    self.assertIn("featuredefs",self.unit.__dict__,"no feature def in unit")
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
    try:
      self.assertIn(self.unit.explodeas.lower(),self.weapons)
    except AttributeError:
      pass
    try:
      self.assertIn(self.unit.selfdestructas.lower(),self.weapons)
    except AttributeError:
      pass

  def test_buildoptions(self):
    try:
      buildoptions = self.unit.buildoptions
    except AttributeError:
      return

    for unitname in buildoptions.values():
      self.assertIn(unitname,self.units,"unit %s does not exist" % unitname)




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
  def __init__(self,mod,tests=()):
    unittest.TestSuite.__init__(self)
    for unitname,unit in mod.getunits().items():
      t = UnitTests(unit,tests)
      self.addTest(t)
        #print "add "+testname+" for "+unitname

class ModelsTests(unittest.TestCase):
  def __init__(self,mod):
    self.mod = mod
  def setUp(self):
    modeldir = os.path.join(sys.argv[1],"objects3d")
    self.models = set( (m.lower().replace('.3do','') for m in os.listdir(modeldir)) )

  def test_unused(self):
    used = set()
    for _,u in self.units.items():
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
  mod = spring.Mod(sys.argv[1])

  tests = sys.argv[2:] 

  suite = AllUnits(mod,tests)
  
  #suite = unittest.TestSuite()
  #suite.addTest( ModelsTests('test_unused') )

  unittest.TextTestRunner(verbosity=1).run(suite)
  print "done"
