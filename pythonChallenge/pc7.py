from PIL import Image
import io, urllib.request

data = urllib.request.urlopen('http://www.pythonchallenge.com/pc/def/oxygen.png').read()
img = Image.open(io.BytesIO(data))

row = [img.getpixel((x, img.height/2)) for x in range(0, img.width, 7)]
elem = [r for r, g, b, a in row if r==g==b]
print(''.join(map(chr, elem)))

list = [105, 110, 116, 101, 103, 114, 105, 116, 121]
print(''.join(map(chr, list)))
