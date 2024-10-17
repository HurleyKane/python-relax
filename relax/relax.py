import os
import utm
import subprocess

from CoseismicEvents import CoseismicEvents


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
        self.add_grid_model()
        self.add_elastic_parameter()
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

    def add_elastic_parameter(self, lambda_param = 3e4, mu_param=3e4, gamma=8.33e-4):
        """
        - gamma = (1 - nu) rho g  # 其中 nu为泊松比, rho为密度，g为重力加速度
        - mu : shear modulus 剪切模量
        - lambda_para : 第一拉梅常数
        - 即，未知量为第一拉梅常数、剪切模量和泊松比。密度和重力加速度需要根据当地情况进行了解
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

    def add_observation_planes(self, num=0):
        bash_content = f"""# number of observation planes\n{num}
"""
        self.bash_content_dict[4] = bash_content

    def add_observation_points(self, num=0):
        bash_content = f"""# number of observation points\n{num}
"""
        self.bash_content_dict[5] = bash_content

    def add_stress_observation_segments(self, num=0):
        bash_content = f"""# number of stress observation segments\n{num}
"""
        self.bash_content_dict[6] = bash_content

    def add_prestress_interfaces(self, num=0):
        bash_content = f"""# number of prestress interfaces\n{num}
"""
        self.bash_content_dict[7] = bash_content

    def add_linear_viscous_interfaces(self, num=0):
        bash_content = f"""# number of linear viscous interfaces\n{num}
"""
        self.bash_content_dict[8] = bash_content

    def add_nonlinear_viscous_interfaces(self, num=0):
        bash_content = f"""# number of non-linear viscous interfaces\n{num}
"""
        self.bash_content_dict[9] = bash_content

    def add_fault_creep_interfaces(self, num=0):
        bash_content = f"""# number of fault creep interfaces\n{num}
"""
        self.bash_content_dict[10] = bash_content

    def add_inter_seismic_strike_slip_segments(self, num=0):
        bash_content = f"""# number of inter-seismic strike-slip segments\n{num}
"""
        self.bash_content_dict[11] = bash_content

    def add_inter_seismic_tensile_segments(self, num=0):
        bash_content = f"""# number of inter-seismic tensile segments\n{num}
"""
        self.bash_content_dict[12] = bash_content

    def add_coseismic_events(self, coseismic_events:CoseismicEvents):
        if coseismic_events is None:
            coseismic_events = CoseismicEvents()
        self.bash_content_dict[13] = coseismic_events.bash_content

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

    def run_bash_script(self):
        subprocess.run(self.bash_content, shell=True, capture_output=True, text=True)

# 使用示例
if __name__ == "__main__":
    relax = Relax(no_proj_output=True)
    cos_events = CoseismicEvents()
    relax.add_coseismic_events(cos_events)
    relax.save_bash_script()