import spring
import sys

mod = spring.Mod(sys.argv[1])

units = mod.getunits()

props = (
'unitname',
'name',
'buildcostmetal',
'buildcostenergy',
'buildtime',
'maxdamage',
'maxvelocity',
'turnrate', 
)

print ",".join(props)
for uname,u in units.items():
  print ",".join( 
      ( unicode( 
          getattr(u,propname,'N/A')
           ) for propname in props )

      ).encode('utf-8')

