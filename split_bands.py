from PIL import Image
from glob import glob
import numpy as np
import matplotlib.pyplot as plt

input_path = "."
images_paths = glob(input_path + "/**/*.jpg", recursive= True)
image_name = "IMG_00366"
image_rgb = np.asarray(Image.open(f"{input_path}/RGB/{image_name}.jpg"))
image_nir = np.asarray(Image.open(f"{input_path}/NIR/{image_name}.jpg"))

fig, axes = plt.subplots(2,3, figsize = (16,10))

axes[0,0].imshow(image_rgb[:,:,0], cmap= "gray")
axes[0,0].set_title("Banda Roja")
axes[0,1].imshow(image_rgb[:,:,1], cmap= "gray")
axes[0,1].set_title("Banda Verde")
axes[0,2].imshow(image_rgb[:,:,2], cmap= "gray")
axes[0,2].set_title("Banda Azul")
axes[1,0].imshow(image_nir[:,:,0], cmap= "gray")
axes[1,0].set_title("Banda Borde Rojo")
axes[1,1].imshow(image_nir[:,:,2], cmap= "gray")
axes[1,1].set_title("Banda NIR")
axes[1,2].imshow(image_rgb)
axes[1,2].set_title("Imagen RGB")

plt.tight_layout()

## Split Bandas

plt.show()