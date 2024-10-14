# InSAR Three Dimension deformation
## 0 额外依赖
```aiignore
    gdal
    opencv
```
## 1. 功能
该源代码是通过对已有的InSAR观测值(InSAR LOS向、AZI向形变观测值)进行处理,获取其东西、南北和垂直向三维形变。

## intall
### 1. 使用release的whl包进行安装
```bash
pip install InSARlib_default_windows_py311_20240601131008-0.0.3-py3-none-any.whl
```
### 2. 利用git命令安装github仓库
```bash
git clone git@github.com:HurleyKane/InSAR3DDDeformationn.git
```
## 3. 使用示例
### 3.1 [实验数据的初始化](Document/实验数据的初始化.md)

### 3.2 [GNSS和InSAR数据融合的SMVCE方法](Document/GNSS和InSAR数据融合的SMVCE方法.md)

### 3.3 [自主识别断层线的三维形变反演方法](codes/ridgecreast_simulation_experiment/thirdPaperSimulationExperiment/0.2 提取断层线和三维形变提取可视化.ipynb)

## 详细说明文档
### [断层线对象的使用]()

## 4. cites
[1] Chen M, Xu G, Zhang T, et al. A novel method for inverting coseismic 3D surface deformation using InSAR considering the weight influence of the spatial distribution of GNSS points [J]. Advances in Space Research, 2024, 73(1) : 585–596.

[2] 陈明锴, 许光煜, 王乐洋. InSAR同震地表三维形变反演：一种顾及形变梯度的联合解算方法[J]. 武汉大学学报(信息科学版), 2023, 48(8) : 1349–1358.

