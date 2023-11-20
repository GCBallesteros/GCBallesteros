convert -colors 32 -fuzz 50% -resize 50% -delay 7 -loop 0 *.png output.gif
convert -crop 300x300+110+100 -repage 300x300+0+0 output.gif output-2.gif
