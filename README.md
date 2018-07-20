# supportTools
several supporting tools for Quantum-espresso and EPW calculation

## phononSplit.py
This script antomatically generate folders to run ph.x in several split job.

--scfFile: filename of scf calculation of pw.x
--qmesh: mesh for 3 direction, total 3 number required
--polar:need to calculate Born effective charge and dielectric constant
--njobs:number of split jobs
--nqs:number of irreduciable qpoints

these input parameters also can be read from file. The example of the input file is phononSplitInput.txt
You need to add "@" when you want to read parameters from file. For example,

'''
python phononSplit.py @phononSplitInput.txt
'''

The number of irreducible qpoint is required, thus, I recommend to run test calclation just for Gamma point, 
and check this value from output file of ph.x, **dyn.0.
