from PIL import Image


class ImageProcessor:

    @staticmethod
    def color_cmp(orig, comp):
        tolerance = 5  # You can adjust color tolerance value
        inside = []
        for i in range(len(orig)):
            if (orig[i] - tolerance) <= comp[i] <= (orig[i] + tolerance):
                inside.append(True)
            else:
                inside.append(False)
        if inside.count(False):
            return 0
        else:
            return 1

    @staticmethod
    def magicSauce(rgbImg, to_copare_with_pixel, backgroundcolor):
        for y in range(rgbImg.size[1]):
            for x in range(rgbImg.size[0]):
                pix_color = rgbImg.getpixel((x, y))
                if ImageProcessor.color_cmp(pix_color, to_copare_with_pixel):
                    rgbImg.putpixel((x, y), backgroundcolor)
                else:
                    rgbImg.putpixel((x, y), (
                        abs(pix_color[0]), abs(pix_color[1]),
                        abs(pix_color[2])))
        return rgbImg

    @staticmethod
    def automask(path, height, width):
        img = Image.open(path)

        rdb_frames = []

        backgroundcolor = (255, 255, 255)

        is_animated = False

        if hasattr(img, 'is_animated') and img.is_animated:
            is_animated = True
        if is_animated:
            for frame in range(0, img.n_frames):
                img.seek(frame)
                rgbImg = img.convert('RGB')
                rgbImg = rgbImg.resize((height, width), Image.ADAPTIVE)
                to_copare_with_pixel = rgbImg.getpixel((0, 0))
                rgbImg = ImageProcessor.magicSauce(rgbImg, to_copare_with_pixel, backgroundcolor)
                rdb_frames.append(rgbImg)
        else:
            # img = img.convert('RGB')
            img = img.resize((height, width), Image.ADAPTIVE)

            to_copare_with_pixel = img.getpixel((0, 0))

            img = ImageProcessor.magicSauce(img, to_copare_with_pixel, backgroundcolor)
            rdb_frames.append(img)

        return rdb_frames
