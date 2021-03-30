from typing import Optional
from pathlib import Path
import pyroSAR.snap.util
import logging

from .storage import move_file, move_directory, exists, download_and_zip_directory


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def process(
    path: str,
    output_directory: str,
    speckleFilter: str = "Refined Lee",
    refarea: str = "sigma0",
    nodataValueAtSea: bool = False,
    imgResamplingMethod: str = "BILINEAR_INTERPOLATION",
    resolution: int = 20,
    polarizations: str = "all",
    shapefile: Optional[str] = None,
    scaling: str = "dB",
    geocoding_type: str = "Range-Doppler",
    removeS1BorderNoise: bool = True,
    removeS1BorderNoiseMethod: str = "pyroSAR",
    removeS1ThermalNoise: bool = True,
    terrainFlattening: bool = True,
):
    id = Path(path).stem
    file_name = Path(path).name
    prefix = path.split(id)[0].split("/", 3)[3][:-1]

    if exists(id, prefix=prefix):
        log.info(f"{prefix} {id} exists")
        return {"status": "exists"}
    else:
        log.info(f"{prefix} {id} does not exist")

    log.info(f"Path: {path}")
    if path.endswith(".zip"):
        log.info("Processing zip archive")
        move_file(path, file_name)
    else:
        log.info("Downloading to zip arhive")
        bucket_name = path.split("/")[2]
        prefix = "/".join(path.split("/")[3:])
        file_name = download_and_zip_directory(bucket_name, prefix, id)

    output_path = Path("./ard", id)
    pyroSAR.snap.util.geocode(
        str(file_name),
        str(output_path),
        speckleFilter=speckleFilter,
        refarea=refarea,
        nodataValueAtSea=nodataValueAtSea,
        imgResamplingMethod=imgResamplingMethod,
        tr=resolution,
        polarizations=polarizations,
        shapefile=shapefile,
        scaling=scaling,
        geocoding_type=geocoding_type,
        removeS1BorderNoise=removeS1BorderNoise,
        removeS1BorderNoiseMethod=removeS1BorderNoiseMethod,
        removeS1ThermalNoise=removeS1ThermalNoise,
        terrainFlattening=terrainFlattening,
    )

    if type(output_directory) == tuple:
        output_directory = output_directory[0]
    sink_directory = f"{str(output_directory)}{str(id)}/"

    files = move_directory(str(output_path), sink_directory,)

    return files
