import numpy as np
from io import StringIO

from geodesy import FaultGeometry
from geodesy.earthquake import FaultGeometry as fg

class CoseismicEvents:
    strike_slip_segments_columns = ["no", "slip", "xs", "ys", "zs", "length", "width", "strike", "dip", "rake"]
    def __init__(self, strike_slip_segments:str):
        """
        - fault_geometries = ("1 1 -10 0 0 10 10 0 90 0",) or segments.txt
        """
        self.number_of_events = 1
        self.fault_geometry : FaultGeometry = fg.read_from_csv(strike_slip_segments, delimiter=" ")
        self.bash_content = self.get_bash_content()

    def get_bash_content(self):
        bash_content = self._add_coseismic_strike_slip_segments()
        bash_content += self._add_coseismic_tensile_segments()
        bash_content += self._add_coseismic_dilatation_point_sources()
        bash_content += self._add_surface_traction()
        return bash_content

    def _add_coseismic_strike_slip_segments(self):
        bash_content = f"""# number of coseismic events
{self.number_of_events}
"""
        def add_segment(fault_geometry:FaultGeometry):
            output = StringIO()
            if fault_geometry.ndim == 1:
                num = 1
                np.savetxt(output, fault_geometry.values.reshape(1, -1), fmt="%.2f")
            else:
                num = fault_geometry.shape[0]
                np.savetxt(output, fault_geometry.values, fmt="%.2f")
            part = f"""# number of coseismic strike-slip segments
{num}
# n     slip       xs       ys       zs  length   width strike   dip   rake
{output.getvalue()}"""
            return part

        bash_content += add_segment(self.fault_geometry)
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
    ce = CoseismicEvents("1 1 -10 0 0 10 10 0 90 0")
    ce.get_bash_content()