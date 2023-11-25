echo 'Dither man'
python dither_man.py
echo 'Bulding hypercube frames'
python hypercube3.py
echo 'Building star field frames'
python build_star_field.py
echo 'Combining man, cube and stars'
python blend_man_and_hypercube.py
echo 'Converting to animated gif'
convert  -delay 7 -loop 0 ./horizon_man_looking_hypercube/*.png ./horizon_man_looking_hypercube/banner.gif
echo 'Creating inverted version of gif'
convert ./horizon_man_looking_hypercube/banner.gif -channel RGB -negate ./horizon_man_looking_hypercube/inverted_banner.gif
echo 'Optimizing gifs'
mogrify -layers 'optimize' ./horizon_man_looking_hypercube/banner.gif
mogrify -layers 'optimize' ./horizon_man_looking_hypercube/inverted_banner.gif
