import datetime
import os.path
from scour import scour
from django.conf import settings
from .models import *
from  PIL import Image
from django.core.files.storage import FileSystemStorage
from django.core.management.base import BaseCommand


def get_extension(file_name):
    return os.path.splitext(file_name)[1].lower()


class ProcessImageView():
    def imageProccesing(self, img, q=90):

        img_storage = FileSystemStorage(location=settings.TEMP_IMAGE_DIR, base_url=f"{settings.MEDIA_URL}temp_images/")
        file_name = os.path.basename(img.name)
        file_path = os.path.join(settings.TEMP_IMAGE_DIR, file_name)
        print(file_path)
        if not os.path.exists(file_path):
            saved_name = img_storage.save(file_name, img)
            file_path = img_storage.path(saved_name)
            file_name = saved_name
            procced_filename = f"procced_{file_name}"
            procced_filepath = os.path.join(settings.TEMP_IMAGE_DIR, procced_filename)
        elif os.path.exists(f"procced_{file_name}"):
            os.remove(f"procced_{file_name}")
        procced_filename = f"procced_{file_name}"
        procced_filepath =  os.path.join(settings.TEMP_IMAGE_DIR, procced_filename)
        ext = get_extension(file_name)
        original_size = os.path.getsize(file_path) // 2 ** 10

        # print(procced_filepath, procced_filename)
        if ext in ['.png', '.jpg', '.jpeg', '.webp']:

            with Image.open(file_path) as img:
                match ext:
                    case '.png':
                        img = self.compressPNG(img, q)
                        img.save(procced_filepath, optimize=True)
                    case '.jpg' | '.jpeg':
                        img = self.compressJPG(img)
                        img.save(procced_filepath, optimize=True, quality=q)
                    case '.webp':
                        img = self.compressWebP(img)
                        img.save(procced_filepath, optimize=True, quality=q)



        elif ext in ['.svg', '.svgz']:
            with open(file_path, 'r', encoding='UTF-8') as f, open(procced_filepath, 'wb') as out:
                self.compressSVG(f, out, q)

        else:
            img_storage.delete(file_name)
            raise ValueError(f'wrong format')
        compressed_size = os.path.getsize(procced_filepath) // 2 ** 10
        compression_rate = 100 * (1 - compressed_size / original_size) if original_size else 0


        procced_url = img_storage.url(procced_filename)
        res = [procced_url, procced_filename, original_size, compressed_size, round(compression_rate, 1), file_path, file_name]
        return res

    def convertImages(self, img, to_convert):
        img_storage = FileSystemStorage(location=settings.TEMP_IMAGE_DIR, base_url=f"{settings.MEDIA_URL}temp_images/")
        file_name = img_storage.save(img.name, img)
        file_path = img_storage.path(file_name)
        ext = get_extension(file_name)
        procced_filename = f"procced_{file_name[0]}.{to_convert.lower()}"
        procced_filepath = os.path.join(settings.TEMP_IMAGE_DIR, procced_filename)
        if os.path.exists(procced_filepath):
            os.remove(procced_filepath)
        if ext in ['.png', '.jpg', '.jpeg', '.webp']:
            with Image.open(file_path) as img:
                if to_convert == 'PNG':
                    img = self.convertToPNG(img)
                    img.save(procced_filepath, format='PNG', optimize=True)
                elif to_convert == 'JPG':
                    img = self.convertToJPG(img)
                    img.save(procced_filepath, format='JPEG', optimize=True)

                elif to_convert == 'WEBP':
                    img.save(procced_filepath, format='WEBP')

        else:
            raise ValueError(f'Wrong format')


        procced_url = img_storage.url(procced_filename)
        return procced_url, procced_filename

    def compressPNG(self, img, q):
        max_colors = min(round(((q - 10) / 90) * 253) + 2, 255)
        img = img.convert('P', palette=Image.ADAPTIVE, colors=max_colors)
        img = img.quantize(colors=max_colors, method=Image.FASTOCTREE)
        return img

    def compressJPG(self, img):
        return img

    def compressWebP(self, img):
        return img
    def compressSVG(self, input_file, out_file, q):

        options = scour.sanitizeOptions()
        options.remove_metadata = True  # удалить метаданные
        options.enable_viewboxing = True  # сохранить атрибут viewBox
        options.strip_comments = True  # удалить комментарии
        options.indent_type = None  # удалить отступы
        options.newlines = False  # удалить переводы строк
        options.shorten_ids = True  # сократить идентификаторы
        max_dp, min_dp = 6, 0
        dp = int(round(max_dp - (q / 100.0) * (max_dp - min_dp)))
        options.numerical_precision = dp
        if q <= 50:
            options.group_collapse = 1
        elif q < 75:
            options.remove_descriptive_elements = 1
        elif q < 80:
            options.strip_ids = 1
        scour.start(options, input_file, out_file)

    def convertToJPG(selfs, img):
        if img.mode in ('RGBA', 'LA'):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        else:
            img = img.convert('RGB')
        return img

    def convertToPNG(selfs, img):
        return img

    def convertToSVG(selfs, img):
        img = img.convert('L')

        return img

    def convertToWebP(selfs, img):

        return img


class Command(BaseCommand):
    help = 'Clean up temporary files'

    def handle(self, *args, **options):
        now = datetime.datetime.now()
        temp_dir = settings.TEMP_IMAGE_DIR
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            if os.path.isfile(file_path):
                file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                if (now - file_mtime).total_seconds() > 3000:
                    try:

                        os.remove(file_path)
                        self.stdout.write(f"Deleted: {file_path}")
                    except Exception as e:
                        self.stderr.write(f"Error {file_path}:{e}")
