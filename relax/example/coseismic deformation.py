from __future__ import annotations
from relax.core import Relax
def coseismic_event()-> Relax:
    relax_model = Relax(no_proj_output=True)
    relax_model.add_grid_model()
    relax_model.add_elastic_parameter(3e4, 3e4, 8.33e-4)
    relax_model.add_coseismic_event(strike_slip_segments="1 1 -10 0 0 10 10 0 90 0")
    return relax_model

if __name__ == "__main__":
    relax_model = coseismic_event()
    relax_model.save_bash_script("execulator/coseismic.sh")