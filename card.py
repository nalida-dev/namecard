from PIL import Image, ImageFont, ImageDraw

image = Image.new("RGBA", (445, 735), color="RGB(242, 242, 242)")
#image = Image.open("template.png")
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('NanumSquareRoundR.ttf', 20)
kover = ImageFont.truetype('koverwatch.ttf', 162)
draw.rectangle([(0, 600), (445, 735)], fill="RGB(62,62,62)")
sentence = "010C40434439"
for i in range(3):
    for j in range(4):
        fill = "RGB(62,62,62)" if i != 0 or j != 3 else "RGB(245,178,131)"
        draw.text((30+j*105, 45+i*180), sentence[i*4+j], fill=fill, font=kover)
draw.text((100, 630), "김민성 주정", fill="RGB(242, 242, 242)", font=font)
image.save("result.png")
