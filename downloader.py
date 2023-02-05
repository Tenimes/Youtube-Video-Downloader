import pytube
from io import BytesIO
from PIL import ImageTk, Image
from urllib.request import urlopen


class video(pytube.YouTube):
    def __init__(self, url, **kwargs):
        super().__init__(url, **kwargs)

    def length_str(self):
        self.length_by_second = self.length
        if self.length_by_second < 3600:
            self.length_final = str(self.length_by_second//60)+':'
            if (self.length_by_second % 60 < 10):
                self.length_final = self.length_final + \
                    '0'+str(self.length_by_second % 60)
            else:
                self.length_final = self.length_final + \
                    str(self.length_by_second % 60)
        else:
            self.length_final = str(self.length_by_second//3600)+':'
            if (self.length_by_second % 3600)//60 < 10:
                self.length_final = self.length_final+'0' + \
                    str((self.length_by_second % 3600)//60)+':'
            else:
                self.length_final = self.length_final + \
                    str((self.length_by_second % 3600)//60)+':'
            if (self.length_by_second % 60) < 10:
                self.length_final = self.length_final + \
                    '0'+str(self.length_by_second % 60)
            else:
                self.length_final = self.length_final + \
                    str(self.length_by_second % 60)
        return self.length_final

    def thumbnail_image(self, image_size=(240, 135)):
        self.url = urlopen(self.thumbnail_url)
        self.raw_data = self.url.read()
        self.url.close()
        self.image = Image.open(BytesIO(self.raw_data))
        self.w, self.h, = self.image.size
        self.left = 0
        self.right = self.w
        self.upper = self.h/8
        self.lower = 7*self.h/8
        self.image = self.image.crop(
            ([self.left, self.upper, self.right, self.lower]))
        self.image = self.image.resize(image_size, Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(self.image)
        return self.photo


if __name__ == '__main__':
    url = 'https://www.youtube.com/watch?v=MNeX4EGtR5Y&ab_channel=Fireship'
    video = video(url)
