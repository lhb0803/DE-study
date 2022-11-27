import numpy as np
import bentoml
from bentoml.io import NumpyNdarray

runner = bentoml.xgboost.get("xgb_bento:latest").to_runner()

svc = bentoml.Service("xgb_bento", runners=[runner])

@svc.api(input=NumpyNdarray(), output=NumpyNdarray())
def predict(input_series: np.ndarray) -> np.ndarray:
    result = runner.predict.run(input_series)
    return result