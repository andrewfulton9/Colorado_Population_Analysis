from images2gif import writeGif
from PIL import Image
import os

files_names = sorted((fn for fn in os.listdir('images') if fn.endswith('.jpeg')))

images = [Image.open(fn) for fn in file_names]

fn = 'CO_pop_gif.GIF'
writeGIF(fn, images, duration = 1)
