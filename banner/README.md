# How the banner was generated

1. Take `horizon_smaller.jpg` and put it through a semantic segmentation, SAM
   here, to get rid of the sky and just keep the man and the grass field.
2. Make the image wider using [seam carving](https://seamcarving.vercel.app/)
3. Open the resulting image without the sky and retouch the masked image on
   GIMP to clean up bad parts and fill up some holes.
4. Run `dither_man.py`. This dithers the man image for artistic flair and also
   adds some padding so that then we can insert the hypercube animation
comfortably.
5. Generate the frames for the rotating hypercube. For this run
   `hypercube3.py`, yes, it took me 3 algorithms to get it just like I wanted.
This will go into the `hypercube_frames` folder.
6. Finally merge the hypercube frames into the man on the field by running
   `blend_man_and_hypercube.py`
7. Finally merge the frames using imagemagick. You have same example commands
   in `make_gif.sh`
