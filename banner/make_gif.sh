echo 'Dither man'
python dither_man.py
echo 'Bulding hypercube frames'
python hypercube.py
echo 'Building star field frames'
python build_star_field.py
echo 'Combining man, cube and stars'
python blend_man_and_hypercube.py
echo 'Generating light banner frames'
python frame_shaker.py
echo 'Building dark banner gif'
convert  -delay 7 -loop 0 ./horizon_man_looking_hypercube/*.png ./dark_banner.gif
echo 'Building light banner gif'
convert  -delay 7 -loop 0 ./shaken_day_frames/*.png ./light_banner.gif
echo 'Optimizing gifs'
mogrify -layers 'optimize' ./dark_banner.gif
mogrify -layers 'optimize' ./light_banner.gif
