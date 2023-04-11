from PIL import Image, ImageDraw, ImageFont
import random
width, height = 2000, 2000

#(tile fill, font color)
colors = [
    [(245, 215, 191), (255, 110, 64)],
    [(239, 233, 207), (252, 68, 69)],
    [(248, 233, 161), (255, 65, 108)],
    [(191, 215, 181), (255, 87, 51)],
    [(181, 216, 235), (255, 75, 100)]
]


# create a new image with the given size
img = Image.new('RGB', (width, height), color='white')

# create a font for the tile numbers
font = ImageFont.truetype('comic.ttf', size= (width+height)//(2*35))

# create a draw object to draw on the image
draw = ImageDraw.Draw(img)
posDict = {}
# draw the tiles and tile numbers
while True:
    clr = - 99
    switch = False
    if input("Press enter to generate new picture or type end to exit\n") == "end":
        break
    for i in range(100):
        if i % 10 == 0 and i > 0: switch = not switch
        if switch:
            x = width*0.9 - (i % 10) * width//10
        else: 
            x = (i % 10) * width//10
        y = (9 - (i // 10)) * height//10

        tmp = clr
        while abs(tmp - clr) < 2:
            clr = random.randint(0,len(colors)-1)
        posDict[i+1] = (int(x + width // 20), int(y + height // 20)) 
        draw.rectangle((x, y, x+width//10, y+height//10), fill=colors[clr][0], outline='black')
        draw.text((x + font.size//5, y + font.size//5), str(i+1), font=font, fill=colors[clr][1])

    # save the image to a file
    img.save('snakes_and_ladders.png')
    print(posDict)
