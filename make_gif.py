import imageio
from PIL import Image
import os

file_names = sorted((fn for fn in os.listdir('images') if fn.endswith('.png')))

images = [('images/' + fn) for fn in file_names]

frames = [imageio.imread(im) for im in images]

name = 'CO_pop_gif.GIF'
imageio.mimsave(name, frames, 'GIF', **{'duration':.1})
