from PIL import Image, ImageFont, ImageDraw


def pixel(cm):
    return round(cm*28.347)


def separate(sentence):
    words = sentence.split()
    if len(sentence) <= 22:
        return [sentence]
    else:
        for i in range(len(words)-1,0,-1):
            left = ' '.join(words[:i])
            right = ' '.join(words[i:])
            if len(left) <= 22 and len(right) <= 22:
                return [left, right]
        return [sentence[:22], sentence[22:]]

def create_namecard(number, initial, name, nickname, sentence, R, G, B, output_filename, p=4):
    number = number.replace('-','')
    color_code = 'RGB(' + (str)(R) + ',' + (str)(G) + ',' + (str)(B) + ')'
    image = Image.new("RGBA", (pixel(5.2*p), pixel(8.6*p)), color="RGB(230, 230, 230)")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('NanumSquareRoundR.ttf', 7*p)
    font_small = ImageFont.truetype('NanumSquareRoundR.ttf', 5*p)
    kover = ImageFont.truetype('koverwatch.ttf', 60*p)
    draw.rectangle([(0, pixel(7*p)), (pixel(5.2*p), pixel(8.6*p))], fill="RGB(62,62,62)")
    numbers = number[0:3] + initial + number[3:]
    for i in range(3):
        for j in range(4):
            fill = "RGB(62,62,62)" if i != 0 or j != 3 else color_code
            if numbers[i*4+j] == '1':
                draw.text((pixel(0.4*p)+j*pixel(1.2*p)+pixel(0.15*p), pixel(0.38*p)+i*pixel(2.2*p)), numbers[i*4+j], fill=fill, font=kover)
            else:
                draw.text((pixel(0.4*p)+j*pixel(1.2*p), pixel(0.38*p)+i*pixel(2.2*p)), numbers[i*4+j], fill=fill, font=kover)
    draw.text((pixel(1.47*p), pixel(7.37*p)), name + ' ' + nickname, fill="RGB(255, 255, 255)", font=font)
    draw.line((pixel(1.47*p), pixel(7.7*p), pixel(1.47*p+0.22*p*len(name) + 0.08*p + 0.22*p*len(nickname)), pixel(7.7*p)), width = 0)
    for index, item in enumerate(separate(sentence)):
        if item[0] == ' ':
            item = item[1:]
        draw.text((pixel(1.47*p), pixel(7.82*p+index*0.25*p)), item, fill="RGB(255,255,255)", font=font_small)
    draw.rectangle([(pixel(0.47*p), pixel(7.40*p)), (pixel(1.00*p), pixel(8.23*p))], fill=color_code)
    draw.rectangle([(pixel(0.40*p), pixel(7.33*p)), (pixel(1.00*p), pixel(8.23*p))], outline="RGB(255,255,255)")
    draw.rectangle([(pixel(0.47*p), pixel(7.40*p)), (pixel(1.07*p), pixel(8.30*p))], outline="RGB(255,255,255)")

    if not output_filename.endswith('.png'):
        output_filename += '.png'
    image.save(output_filename)
