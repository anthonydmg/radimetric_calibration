
import numpy as np

teflon_reflectance  = {
    "wavelengths" : np.linspace(0, 900, 901).astype(np.int32),
    "reflectance": np.array([1] * 900) 
}
