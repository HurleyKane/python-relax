# python-relax - Python bindings for relax

## 可选依赖
本项目通过python对relax进行调用，生成crust的脚本，运行crust的脚本，并返回结果。
注：运行crust脚本，需要配置relax软件的基本环境，如只需要生成relax的bash脚本，则不需要配置 relax 的环境。
## python环境配置
```angular2html
pip install -r requirements.txt
```
## 使用说明
使用实例见relax中的examples中的taiwan地震的fault文件夹chichi.flt
```python
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

# 需要配置relax环境
relax_model.run_bash_script(filename="./coseismic.sh")
```
