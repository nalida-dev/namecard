from PIL import Image, ImageFont, ImageDraw


def pixel(cm):
    return round(cm*28.347)


def separate(sentence):
    if len(sentence) > 22:
        return [sentence[:22], sentence[22:]]
    else:
        return sentence

'''
number = sys.argin[1]
initial = sys.argin[2]
name = sys.argin[3]
nickname = sys.argin[4]
sentence = sys.argin[5]
color = sys.argin[6]
'''



number = '01064956991'
initial = 'L'
name = "이주헌"
nickname = '플롯'
sentence = '다른 사람들의 이야기를 여행하기 좋아하는 음악기술공학자 입니다.'
color_code = "RGB(256, 178, 131)"



def create_namecard(number, initial, name, nickname, sentence, R, G, B):
    number = number.replace('-','')
    color_code = 'RGB(' + R + ',' + G + ',' + B + ')'
    image = Image.new("RGBA", (pixel(5.2), pixel(8.6)), color="RGB(230, 230, 230)")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('/home/juheon/fonts/NanumSquareR.ttf', 7)
    font_small = ImageFont.truetype('/home/juheon/fonts/NanumSquareR.ttf', 5)
    kover = ImageFont.truetype('/home/juheon/fonts/koverwatch.ttf', 60)
    draw.rectangle([(0, pixel(7)), (pixel(5.2), pixel(8.6))], fill="RGB(62,62,62)")
    numbers = number[0:3] + initial + number[3:]
    for i in range(3):
        for j in range(4):
            fill = "RGB(62,62,62)" if i != 0 or j != 3 else color_code
            if numbers[i*4+j] == '1':
                draw.text((pixel(0.4)+j*pixel(1.2)+pixel(0.15), pixel(0.38)+i*pixel(2.2)), numbers[i*4+j], fill=fill, font=kover)
            else:
                draw.text((pixel(0.4)+j*pixel(1.2), pixel(0.38)+i*pixel(2.2)), numbers[i*4+j], fill=fill, font=kover)
    draw.text((pixel(1.47), pixel(7.37)), name + ' ' + nickname, fill="RGB(255, 255, 255)", font=font)
    draw.line((pixel(1.47), pixel(7.7), pixel(1.47+0.22*len(name) + 0.08 + 0.22*len(nickname)), pixel(7.7)), width = 0)
    for index, item in enumerate(separate(sentence)):
        if item[0] == ' ':
            item = item[1:]
        draw.text((pixel(1.47), pixel(7.82+index*0.3)), item, file="RGB(255,255,255)", font=font_small)
    draw.rectangle([(pixel(0.47), pixel(7.40)), (pixel(1.00), pixel(8.23))], fill=color_code)
    draw.rectangle([(pixel(0.40), pixel(7.33)), (pixel(1.00), pixel(8.23))], outline="RGB(255,255,255)")
    draw.rectangle([(pixel(0.47), pixel(7.40)), (pixel(1.07), pixel(8.30))], outline="RGB(255,255,255)")
    image.save( '[NALIDA-card] '+nickname+'.png')





namecard = open('/home/juheon/MARG/PROJECT/005_NALIDA_namecard/namecard_list.csv', 'r').readlines()
for line in namecard:
    temp = line.split('\n')[0].split('\ufeff')[-1].split(',')
    create_namecard(temp[0], temp[1], temp[2], temp[3], temp[4], temp[5], temp[6], temp[7])
