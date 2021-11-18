# [1] https://doi.org/10.1063/1.4994149

from math import log
import pickle
from ase.build import bulk
from ase.io import write
from ase import Atoms
from ase.optimize import LBFGS
from ase.calculators.espresso import Espresso


initial_output_file = 'bulk_init.xyz'
final_output_file = 'bulk_final.xyz'
cu_bulk = bulk('Cu', crystalstructure='fcc', a=4.0, cubic=True)
write(initial_output_file, cu_bulk)

pseudopotentials = {'Cu': 'Cu.pbe-dn-kjpaw_psl.1.0.0.UPF'}
input_settings = {
    'control': {
        'calculation': 'vc-relax',
        'forc_conv_thr': 0.001
    },
    'system': {
        'occupations': 'smearing',  # required for metals
        'degauss': 0.1,
        'ecutwfc': 36,  # energy cutoffs from [1]
        'ecutrho': 400
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

calc = Espresso(pseudopotentials=pseudopotentials,
                tstress=True, tprnfor=True, kpts=(1, 1, 1),
                pseudo_dir='../pseudos/',
                input_data=input_settings)
cu_bulk.calc = calc
opt = LBFGS(cu_bulk, restart='qn.pckl', logfile='ase_bulk_relax.log', trajectory='qn.traj')
opt.run(fmax=0.001)

write(final_output_file, cu_bulk)
