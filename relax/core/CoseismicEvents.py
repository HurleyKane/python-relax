import numpy as np
from io import StringIO

from geodesy.earthquake import FaultGeometry
from geodesy.earthquake import FaultGeometry as fg

class CoseismicEvents:
    strike_slip_segments_columns = ["no", "slip", "xs", "ys", "zs", "length", "width", "strike", "dip", "rake"]
    def __init__(self):
        """
        - fault_geometries = ("1 1 -10 0 0 10 10 0 90 0",) or segments.txt
        """
        self.number_of_events = 1
        self.bash_content = self.get_bash_content()

    def get_bash_content(self):
        bash_content = self._add_coseismic_tensile_segments()
        bash_content += self._add_coseismic_dilatation_point_sources()
        bash_content += self._add_surface_traction()
        return bash_content

    def _add_coseismic_tensile_segments(self, num=0):
        bash_content = f"""# number of coseismic tensile segments\n{num}
"""
        return bash_content

    def _add_coseismic_dilatation_point_sources(self, num=0):
        bash_content = f"""# number of coseismic dilatation point sources\n{num}
"""
        return bash_content

    def _add_surface_traction(self, num=0):
        bash_content = f"""# number of surface traction sources\n{num}
EOF
"""
        return bash_content

if __name__ == "__main__":
    ce = CoseismicEvents()
    ce.get_bash_content()