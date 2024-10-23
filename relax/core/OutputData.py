from __future__ import annotations

import sys
from typing import Any
from collections.abc import (
    Mapping,
)
from xarray.core.types import DataVars

"""自建库"""
import os.path
from geodesy import GeoDataset

class OutputData(GeoDataset):
    necessary_coords = ["clon", "clat"]
    __slots__ = ()
    def __init__(
            self,
            data_vars: DataVars | None = None,
            coords: Mapping[Any, Any] | None = None,
            attrs: Mapping[Any, Any] | None = None,
    ) -> None:
        super().__init__(data_vars, coords, attrs)

    @staticmethod
    def read_from_folder(dir_name:str):
        if os.path.isdir(dir_name):
            filenames = [os.path.join(dir_name, file) for file in os.listdir(dir_name) if file.endswith(".grd")]
            properties = [[file.split("/")[-1].split(".")[-2]] for file in os.listdir(dir_name) if file.endswith(".grd")]
            dataset  = GeoDataset.read_tiffs(filenames=filenames, properties_name=properties).dataset
            return OutputData(dataset)
        else:
            raise FileNotFoundError("The directory does not exist.")

if __name__ == "__main__":
    import os
    os.chdir("/mnt/data/project/python-relax")
    path = "results/coseismic"
    dataset = OutputData.read_from_folder(path)
