from typing import Optional
import time
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import socket
import logging

from .process import process


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


app = FastAPI(title="Sherlock SNAP")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.get("/")
def health_check():
    """
    Health check and app metadata
    """
    status = {"status": "ok"}

    return status


class ProcessItemRequest(BaseModel):
    path: str
    output_directory: str = "gs://spill-sight-public/ard/"
    force: bool = False
    speckleFilter: str = "Refined Lee"
    refarea: str = "sigma0"
    nodataValueAtSea: bool = False
    imgResamplingMethod: str = "BILINEAR_INTERPOLATION"
    resolution: int = 20
    polarizations: str = "all"
    shapefile: Optional[str] = None
    scaling: str = "dB"
    geocoding_type: str = "Range-Doppler"
    removeS1BorderNoise: bool = True
    removeS1BorderNoiseMethod: str = "pyroSAR"
    removeS1ThermalNoise: bool = True
    terrainFlattening: bool = True

    class Config:
        schema_extra = {
            "example": {
                "path": "gs://spill-sight/memscale/HalifaxSpill/S1A_IW_GRDH_1SDV_20180623T220957_20180623T221022_022490_026F92_702A.zip",
                "output_directory": "gs://spill-sight/ard/",
                "force": True,
                "speckleFilter": "Refined Lee",
                "refarea": "sigma0",
                "nodataValueAtSea": False,
                "imgResamplingMethod": "BILINEAR_INTERPOLATION",
                "resolution": 20,
                "polarizations": "all",
                "shapefile": None,
                "scaling": "dB",
                "geocoding_type": "Range-Doppler",
                "removeS1BorderNoise": True,
                "removeS1BorderNoiseMethod": "pyroSAR",
                "removeS1ThermalNoise": True,
                "terrainFlattening": False,
            }
        }


@app.post("/item/")
def process_item(body: ProcessItemRequest):
    """
    Pre process Sentinel 1 scene
    """
    try:
        start_time = time.time()

        result = {}
        result["input"] = body.path

        processing_result = process(
            body.path,
            body.output_directory,
            body.speckleFilter,
            body.refarea,
            body.nodataValueAtSea,
            body.imgResamplingMethod,
            body.resolution,
            body.polarizations,
            body.shapefile,
            body.scaling,
            body.geocoding_type,
            body.removeS1BorderNoise,
            body.removeS1BorderNoiseMethod,
            body.removeS1ThermalNoise,
            body.terrainFlattening,
        )

        result["processing_result"] = processing_result

        duration = time.time() - start_time
        result["duration"] = duration

        return result

    except Exception as exception:
        log.exception(exception)

        raise HTTPException(status_code=400, detail=f"{exception}")


if __name__ == "__main__":
    # Entry point for development
    # Production containers call `uvicorn` from bash shell (see Dockerfile)
    import uvicorn

    uvicorn.run(
        "sherlock_snap.main:app", host="0.0.0.0", port=8080, log_level="info", reload=True,
    )
