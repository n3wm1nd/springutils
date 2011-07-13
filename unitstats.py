import spring
import sys
import csv

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

writer = csv.writer(sys.stdout)
writer.writerow( props )
for uname,u in units.items():
  writer.writerow( 
      [ unicode( 
          getattr(u,propname,'N/A')
           ).encode("utf-8") for propname in props 
      ]

      )

