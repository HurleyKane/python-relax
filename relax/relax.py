import os
from io import StringIO

import utm
import subprocess
import pandas as pd
import numpy as np
from sympy import content

from CoseismicEvents import CoseismicEvents

def get_df_stringio_str(data:pd.DataFrame or StringIO or str):
    if isinstance(data, pd.DataFrame):
        content = StringIO()
        np.savetxt(content, data, fmt="%.3f", delimiter=" ")
        content = content.getvalue()
    elif isinstance(data, StringIO):
        content = data.getvalue()
    elif isinstance(data, str):
        content = data
    else:
        raise TypeError
    num = len(content.split("\n"))
    return num, content

class Relax:
    def __init__(
            self,
            no_proj_output:bool=False,
            no_stress_output:bool=False,
            no_vtk_output:bool=False,
            no_grd_output:bool=False,
    ):
        """
        output_proj:是否输出坐标
        """
        # 1.首先是base model and fault geometry
        self.bash_content_dict = {}
        self.no_proj_output = no_proj_output
        output_str = self.parameters[0][no_proj_output]
        output_str += self.parameters[1][no_stress_output]
        output_str += self.parameters[2][no_vtk_output]
        output_str += self.parameters[3][no_grd_output]
        self.output_str = output_str
        self._bash_content = None
        self._init_parameters()  # 初始化参数

    parameters = {
        0 : {True:"""--no-proj-output """, False:""""""},
        1 : {True:"""--no-stress-output """, False:""""""},
        2 : {True:"""--no-vtk-output """, False:""""""},
        3 : {True:"""--no-grd-output """, False:""""""}
    }

    def _init_parameters(self):
        self.time_integration()
        self.add_observation_planes()
        self.add_observation_points()
        self.add_stress_observation_segments()
        self.add_prestress_interfaces()
        self.add_linear_viscous_interfaces()
        self.add_nonlinear_viscous_interfaces()
        self.add_fault_creep_interfaces()
        self.add_inter_seismic_strike_slip_segments()
        self.add_inter_seismic_tensile_segments()

    @property
    def bash_content(self):
        self._bash_content = """"""
        for key in sorted(relax.bash_content_dict.keys()):
            self._bash_content += relax.bash_content_dict[key]
        return self._bash_content

    def add_grid_model(
            self,
            grid_dimension:tuple[int, int, int] = (256, 256, 256),
            dx:tuple[float] = (0.5, 0.5, 0.5),
            smoothing:tuple[float] = (0.2, 2),
            origin_position:tuple[float] = (0,0),
            rotation = 0,
            geo_origin:[float, float] = (0, 0), # 非洲西部大西洋的几内亚湾
            observation_depths:tuple[float] = (0, 5),
    ):
        """
        - grid_dimension : 南北、东西、深度, 默认都为km
        - smoothing: beta, nyquist
        - origin_position: x0, y0, rotation
        - geographic origin: lon, lat
        - length_unit : 1e3 默认为km
        """
        if not self.no_proj_output:
            if geo_origin is not None:
                lon, lat = geo_origin
                zone = utm.from_latlon(lat, lon)[2]
                length_unit = 1e3  # 长度单位默认为km
                geo_content = f"""\n# geographic origin (longitude, latitude, UTM zone, unit)
{geo_origin[0]} {geo_origin[1]} {zone} {length_unit}"""
            else:
                print("please geo_origin:(lon, lat)")
                raise ValueError
        else:
            geo_content = """"""

        bash_content = f"""# SX1,SX2,SX3 (grid size)  
{grid_dimension[0]} {grid_dimension[1]} {grid_dimension[2]}  
# dx1,dx2,dx3 (km), beta (0-0.5), nq (2)  
{dx[0]} {dx[1]} {dx[2]} {smoothing[0]} {smoothing[1]}  
# origin position & rotation  
{origin_position[0]} {origin_position[1]} {rotation}  {geo_content}
# observation depths (for displacement and for stress)
{observation_depths[0]} {observation_depths[1]}  
# output directory (all output written here)  
$WDIR
"""
        self.bash_content_dict[1] = bash_content

    def add_elastic_parameter(self, lambda_param, mu_param, gamma):
        """
        - gamma = (1 - nu) rho g  # 其中 nu为泊松比, rho为密度，g为重力加速度
        - mu : shear modulus 剪切模量
        - lambda_para : 第一拉梅常数
        - 即，未知量为第一拉梅常数、剪切模量和泊松比。密度和重力加速度需要根据当地情况进行了解
        for example : lambda_param = 3e4, mu_param=3e4, gamma=8.33e-4
        """
        bash_content = f"""# lambda (MPa), mu (MPa), gamma (1/km)  
{lambda_param} {mu_param} {gamma}  
"""
        self.bash_content_dict[2] = bash_content

    def time_integration(self, integration_time:float=0, time_step=-1, scaling=1):
        bash_content = f"""# time interval, (positive time step) or (negative skip, scaling)
{integration_time} {time_step} {scaling}
"""
        self.bash_content_dict[3] = bash_content

    def add_observation_planes(self, data:pd.DataFrame or StringIO or str=None):
        """
        用于导出应力分量的观测面: n x1 x2 x3 length width strike dip
        输出：000.op001-s11.grd 000代表time step, op001 is plane 1.
        """
        if data is None:
            num = 0
            bash_content = f"""# number of observation planes\n{num}\n"""
        else:
            num, data = get_df_stringio_str(data)
            bash_content = f"""# number of observation planes\n{num}
# n x1 x2 x3 length width strike dip
{data}
"""
        self.bash_content_dict[4] = bash_content

    def add_observation_points(self, data:pd.DataFrame or StringIO or str=None):
        """
        对于时间相关的问题，可以设置观测点，将地域内的某些点的变形时间序列保存到单个文件中
        """
        if data is None:
            num=0
            bash_content = f"""# number of observation points\n{num}
"""
        else:
            num, content = get_df_stringio_str(data=data)
            bash_content = f"""# number of observation points\n{num}
# no name x1 x2 x3
{content}
"""

        self.bash_content_dict[5] = bash_content

    def add_stress_observation_segments(self, segments:pd.DataFrame or StringIO or str=None):
        """
        计算的是stress change: cfaults-sigma-0001.txt,也就是fault + friction
        多个fault的情况：每个文件将包含应力张量的所有分量，牵引矢量的剪切和法向分量，牵引矢量的走向和倾向分量，牵引矢量的断层法向分量和库仑应力变
        """
        if segments is None:
            num = 0
            bash_content = f"""# number of stress observation points\n{num}
        """
        else:
            num, content = get_df_stringio_str(data=segments)
            bash_content = f"""# number of stress observation segments\n{num}
# # n x1 x2 x3 length width strike dip rake friction
{content}
"""
        self.bash_content_dict[6] = bash_content

    def add_prestress_interfaces(self, num=0):
        bash_content = f"""# number of prestress interfaces\n{num}
"""
        self.bash_content_dict[7] = bash_content

    def add_linear_viscous_interfaces(self, data:pd.DataFrame or StringIO or str=None):
        """data:no depth gammadot0 cohesion"""
        if data is None:
            num = 0
            bash_content = f"""# number of linear viscous interfaces\n{num}\n"""
        else:
            num, content = get_df_stringio_str(data=data)
            bash_content = f"""# number of linear viscous interfaces\n{num}
# no depth gammadot0 cohesion
{content}
"""
        self.bash_content_dict[8] = bash_content

    def add_nonlinear_viscous_interfaces(self, data:pd.DataFrame or StringIO or str=None):
        """data:no depth gammadot0 cohesion"""
        if data is None:
            num = 0
            bash_content = f"""# number of nonlinear viscous interfaces\n{num}\n"""
        else:
            num, content = get_df_stringio_str(data=data)
            bash_content = f"""# number of nonlinear viscous interfaces\n{num}
# no depth gammadot0 cohesion
{content}
"""
        self.bash_content_dict[9] = bash_content

    def add_fault_creep_interfaces(self, fault_creep_interfaces:pd.DataFrame or str or StringIO=None,
                                   afterslip_planes:pd.DataFrame or str or StringIO=None,
                                   ):
        """
        - fault_creep_interfaces:  # no depth gamma0 (a-b)sig friction cohesion
        - afterslip_planes: # no x1 x2 x3 length width strike dip rake
        """
        if fault_creep_interfaces is None:
            num = 0
            bash_content = f"""# number of fault creep interfaces\n{num}
"""
        else:
            num, content1 = get_df_stringio_str(data=fault_creep_interfaces)
            bash_content = f"""# number of fault creep interfaces\n{num}\n"""
            bash_content += f"""# no depth gamma0 (a-b)sig friction cohesion\n{content1}\n"""
            if afterslip_planes is None:
                bash_content += """# number of afterslip planes\n 0\n"""
            else:
                num, content = get_df_stringio_str(data=afterslip_planes)
                bash_content += f"""# number of afterslip planes\n{num}
# no x1 x2 x3 length width strike dip rake
{content}\n"""

        self.bash_content_dict[10] = bash_content

    def add_inter_seismic_strike_slip_segments(self, num=0):
        bash_content = f"""# number of inter-seismic strike-slip segments\n{num}
"""
        self.bash_content_dict[11] = bash_content

    def add_inter_seismic_tensile_segments(self, num=0):
        bash_content = f"""# number of inter-seismic tensile segments\n{num}
"""
        self.bash_content_dict[12] = bash_content

    def add_coseismic_event(self, strike_slip_segments:str):
        coseismic_events = CoseismicEvents(strike_slip_segments=strike_slip_segments)
        self.bash_content_dict[13] = coseismic_events.bash_content
        return coseismic_events

    def save_bash_script(self, filename:str="relax.sh"):
        self.bash_content_dict[0] = f"""!/bin/bash {filename.split(".")[-2]}
WDIR=$(basename "$0" .sh)

if [ ! -e $WDIR ]; then
	echo adding directory $WDIR
	mkdir $WDIR
fi

OMP_NUM_THREADS={os.cpu_count()} relax {self.output_str} <<EOF | tee $WDIR/in.param
"""
        with open(filename, 'w') as f:
            f.write(self.bash_content)

    def run_bash_script(self, filename:str="relax.sh"):
        self.bash_content_dict[0] = f"""!/bin/bash {filename.split(".")[-2]}
        WDIR=$(basename "$0" .sh)

        if [ ! -e $WDIR ]; then
        	echo adding directory $WDIR
        	mkdir $WDIR
        fi

        OMP_NUM_THREADS={os.cpu_count()} relax {self.output_str} <<EOF | tee $WDIR/in.param
        """
        subprocess.run(self.bash_content, shell=True, capture_output=True, text=True)

# 使用示例
if __name__ == "__main__":
    relax = Relax()
    relax.add_grid_model()
    relax.add_elastic_parameter(lambda_param=3e4, mu_param=3e4, gamma=8.33e-4)
    relax.add_observation_planes(data="1 168.5 -438.7 0 1600 160 112.992 90")
    # 三个观测面
    relax.add_observation_points(data="001 GPS1 1 2 0\n002 GPS2 2 1 3")
    relax.add_stress_observation_segments(segments="1 -10 0 0 20 10 0 90 0.6")
    # 不同interfaces
    relax.add_fault_creep_interfaces(fault_creep_interfaces="1 0 0.3 1e3 0.6 0", afterslip_planes="1 -10 0 11 10 10 0 90 0")
    relax.add_coseismic_event(
        strike_slip_segments="0 1 2 3 4 5 6 7 8 9 0\n 1 2 3 4 5 6 7 8 9 0")
    relax.save_bash_script("../results/relax.sh")