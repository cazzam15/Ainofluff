# Homepage hero loop

The 9-second "jargon translator" video on the homepage, made with Tesseract
(`tsrct` 0.3.1). The underscore keeps this folder off the live site.

- `hero-loop.tsrct`: editable project (fonts packaged inside)
- `hero-loop.mp4`: master render, 1080x1080, 30 fps, silent
- `previews/`: poster frame and filmstrip
- `fonts/`: Space Grotesk and Inter from google/fonts, with their OFL licences
- `.tesseract-work/build.py`: generates every layer and keyframe. Edit `PAIRS` to change the words.

## Rebuild after changing the words

```sh
T=~/.local/share/Tesseract/bin/tsrct
cp .tesseract-work/empty.tsrct hero-loop.tsrct && python3 .tesseract-work/build.py
$T project apply --project hero-loop.tsrct --actions .tesseract-work/edits.json
python3 .tesseract-work/measure.py $T 360          # measures jargon widths for the strike
cp .tesseract-work/empty.tsrct hero-loop.tsrct && python3 .tesseract-work/build.py
$T project apply --project hero-loop.tsrct --actions .tesseract-work/edits.json
$T export --project hero-loop.tsrct --output hero-loop.mp4 --resolution 1080p \
  --encoder-backend external-ffmpeg-command --ffmpeg-path /usr/bin/ffmpeg
$T preview --project hero-loop.tsrct --time 1.6 --output previews/poster.png
# Web copies used by index.html
ffmpeg -y -i hero-loop.mp4 -an -vf scale=720:720 -c:v libx264 -crf 26 -preset slow \
  -pix_fmt yuv420p -movflags +faststart ../assets/hero-loop.mp4
ffmpeg -y -i previews/poster.png -vf scale=720:720 -q:v 4 ../assets/hero-loop-poster.jpg
```
