from PIL import Image
import os


path=input("ВВедите путь к папке ")
file_mask=""



print(path)
# #
# os.path.getsize
def get_ways(general_way):
    ways = []
    for d in ld(general_way):

        for i in ld(f'{general_way}\\{d}'):
            if isd(f'{general_way}\\{d}\\{i}'):
                for file in ld(f'{general_way}\\{d}\\{i}'):
                    if file_mask in file:
                        ways.append(f'{general_way}\\{d}\\{i}\\{file}')

            else:
                for file in ld(f'{general_way}\\{d}'):
                    if file_mask in file:
                        ways.append(f'{general_way}\\{d}\\{file}')

    print(ways)
    ways = sorted(set(ways))
    print(ways)
    return ways


images=get_ways(path)


for image in images:
    if os.path.getsize(image)/(1*10**6)>=9:

        original_image=Image.open(image)
        w,h=original_image.size
        print(w*0.9,h*0.9)
        resized_image=original_image.resize((int(w*0.9),int(h*0.9)))
        resized_image.save(image)
    else:
        print("фото {} меньше 8 МБ".format(image))

