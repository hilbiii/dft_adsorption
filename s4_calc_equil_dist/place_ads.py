from ase.io.espresso import read_espresso_out
from ase import Atoms
from ase.io import read, write
from ase.calculators.espresso import Espresso
from ase.build import add_adsorbate
from matplotlib import pyplot as plt
import numpy as np
import copy
from time import time


start = time()
logfile = 'ase.log'


# read in the results from the slab + vacuum relaxation
slab_file = '/home/harris.se/dft_adsorption/s2_relax2_slab_7p5/espresso.pwo'

with open(slab_file, 'r') as f:
    traj = list(read_espresso_out(f, index=slice(None)))
    clean_slab = traj[-1]
    write('opt_slab.xyz', clean_slab)

initial_energy = clean_slab.get_potential_energy()
print(f"Initial Energy: {initial_energy}")


# clean_slab = read('/home/harris.se/dft_adsorption/s2_relax_slab_7p5/slab_init.xyz')

# import optimized co2
co2_file = '/home/harris.se/dft_adsorption/s3_co2_7p5/espresso.pwo'
with open(co2_file, 'r') as f:
    traj = list(read_espresso_out(f, index=slice(None)))
    co2 = traj[-1]
    write('opt_co2.xyz', co2)

# place the co2
co2_index = [atom.index for atom in co2 if atom.symbol == 'C']
heights = np.linspace(0.5, 5, 20)


pseudopotentials = {'Cu': 'Cu.pbe-dn-kjpaw_psl.1.0.0.UPF',
                    'C': 'C.pbe-n-kjpaw_psl.1.0.0.UPF',
                    'O': 'O.pbe-n-kjpaw_psl.1.0.0.UPF'}
input_settings = {
    'control': {
        'calculation': 'scf',
        'forc_conv_thr': 0.001
    },
    'system': {
        'occupations': 'smearing',  # required for metals
        'degauss': 0.1,
        'ecutwfc': 50,  # energy cutoffs from [1]
        'ecutrho': 500
    },
    'ions': {
        'ion_dynamics': 'bfgs'
    },
    'cell': {
        'cell_dynamics': 'bfgs',
        'press': 0.0,
        'press_conv_thr': 0.5,
    }
}

min_energy = 0
min_index = -1
for i, height in enumerate(heights):
    slab = copy.deepcopy(clean_slab)
    calc = Espresso(pseudopotentials=pseudopotentials,
                    tstress=True, tprnfor=True, kpts=(4, 4, 1),
                    pseudo_dir='/home/harris.se/espresso/pseudos/',
                    input_data=input_settings,
                    directory=f'run{i}')
    slab.calc = calc
    add_adsorbate(slab, co2, height=height, mol_index=co2_index[0])
    write(f'system{i}.xyz', slab)
    
    system_energy = slab.get_potential_energy()
    print(f'h={height}', f'U={system_energy}')
    if system_energy < min_energy:
        min_energy = system_energy
        min_index = i

print(f'Minimum Energy: {min_energy}')
print(f'Minimum height: {heights[min_index]}')


end = time()
duration = end - start

with open(logfile, 'a') as f:
    f.write(f'Completed in {duration} seconds')

