from crust import crust_data
from relax import Relax
from scipy.constants import g

# 从crust中获取拉梅参数
lat, lon = 23.772, 120.982
crust_para = crust_data[lat, lon].values
mu, lam, E, nu = crust_para.loc["upper crust"]["mu":"nu"]
rho = crust_para.loc["upper crust"]["rho"] # kg/m^3
gamma = (1 - nu) * rho * g / mu  # 1/m

relax_model = Relax()
relax_model.add_grid_model(geo_origin=(lon, lat))
relax_model.add_elastic_parameter(lam * 1e3, mu * 1e3, gamma / 1e3)

from geodesy.earthquake.FaultGeometry import FaultGeometry
faultgeo = FaultGeometry.read_from_csv("faults/chichi.flt")
relax_model.add_coseismic_event(strike_slip_segments=faultgeo)
relax_model.bash_calculate_result_path = "../results"
relax_model.save_bash_script(filename="./coseismic.sh")
print(relax_model.bash_content)