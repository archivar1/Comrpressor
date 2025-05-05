from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse, Http404, JsonResponse
from django.views.decorators.http import require_http_methods
from .forms import *
from django.conf import settings
from .handler import *
import io
import zipfile

ALLOWED_CONTENT_TYPE = ["image/webp", "image/png", "image/jpeg", "image/svg+xml"]


# Create your views here.
@require_http_methods(['GET', 'POST'])
def index(request):
    content_type = ", ".join(ALLOWED_CONTENT_TYPE)
    if request.method == 'POST':

        images = request.FILES.getlist('images')
        print(images)
        if not images:
            return Http404('Images is missed')
        invalid = next((img for img in images if img.content_type not in ALLOWED_CONTENT_TYPE), None)
        if invalid:
            return JsonResponse({
                'error': 'Недопустимый формат файла. Разрешены: PNG, JPEG, WebP, SVG.'
            }, status=400)
        procced_res = []
        handler = ProcessImageView()
        for img in images:
            processed_url, processed_filename, original_size, compressed_size, compressed_rate, original_path, original_name = handler.imageProccesing(
                img)
            procced_res.append(
                {'image_url': processed_url, 'image_name': processed_filename, 'original_size': original_size,
                 'compressed_size': compressed_size, 'compressed_rate': compressed_rate,
                 'original_path': original_path, 'original_name': original_name})

        request.session['processed_url'] = procced_res

        return render(request, 'mainApp/index.html', {
            'processed_images': procced_res,
            'is_compress': True,
            'content_type': content_type,
            'compression_level': 90,

        })

    return render(request, 'mainApp/index.html', {'content_type': content_type})


@require_http_methods(['GET', 'POST'])
def PNGCompressor(request):
    title = 'PNG-Compressor'
    header = 'Компрессор PNG'
    content_type = 'image/png'
    if request.method == 'POST':

        images = request.FILES.getlist('images')
        if not images:
            return Http404('Images is missed')
        invalid = next((img for img in images if img.content_type not in ALLOWED_CONTENT_TYPE), None)
        if invalid:
            return JsonResponse({
                'error': 'Недопустимый формат файла. Разрешен: PNG.'
            }, status=400)
        procced_res = []
        print(images)
        handler = ProcessImageView()
        for img in images:
            processed_url, processed_filename, original_size, compressed_size, compressed_rate, original_path, original_name = handler.imageProccesing(
                img)
            procced_res.append(
                {'image_url': processed_url, 'image_name': processed_filename, 'original_size': original_size,
                 'compressed_size': compressed_size, 'compressed_rate': compressed_rate,
                 'original_path': original_path, 'original_name': original_name})

        request.session['processed_url'] = procced_res

        return render(request, 'mainApp/Compressor.html', {
            'processed_images': procced_res,
            'is_compress': True,
            'content_type': content_type,
            'header': header,
            'title': title,
            'compression_level': 90,
        })

    return render(request, 'mainApp/Compressor.html', {'content_type': content_type,
                                                       'header': header,
                                                       'title': title
                                                       })


@require_http_methods(['POST'])
def compressImage(request):
    target_url = request.POST.get('image_url')
    try:
        compress_val = int(request.POST.get('compression_value'))
    except (TypeError, ValueError):
        compress_val = 90

    processed = request.session.get('processed_url', [])
    if not processed:
        return JsonResponse({'error': 'Нет загруженных изображений'}, status=400)

    handler = ProcessImageView()

    for img in processed:
        if img['image_url'] == target_url:
            original_name = img['original_name']
            original_path = os.path.join(settings.TEMP_IMAGE_DIR, original_name)

            with open(original_path, 'rb') as f:
                new_url, new_name, orig_size, comp_size, comp_rate, _, _ = \
                    handler.imageProccesing(f, q=compress_val)

            img.update({
                'image_url': new_url,
                'image_name': new_name,
                'original_size': orig_size,
                'compressed_size': comp_size,
                'compressed_rate': comp_rate,
                'compression_level': compress_val,
            })

            request.session['processed_url'] = processed

            return JsonResponse({
                'image_url': new_url,
                'original_size': orig_size,
                'compressed_size': comp_size,
                'compressed_rate': comp_rate,
                'compression_level': compress_val,

            })

    return JsonResponse({'error': 'Изображение не найдено в сессии'}, status=404)


@require_http_methods(['GET', 'POST'])
def downloadAllImages(request):
    images = request.session.get('processed_url')

    if not images:
        raise Http404("Images is missed")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for image in images:
            img_path = os.path.join(settings.TEMP_IMAGE_DIR, image['image_name'])
            if os.path.exists(img_path):
                zip_file.write(img_path, arcname=image['image_name'])

    zip_buffer.seek(0)
    return FileResponse(zip_buffer, as_attachment=True, filename="images.zip")


@require_http_methods(['GET', 'POST'])
def JPEGCompressor(request):
    content_type = 'image/jpeg'
    title = 'JPEG-Compressor'
    header = 'Компрессор JPEG'
    if request.method == 'POST':

        images = request.FILES.getlist('images')
        if not images:
            return Http404('Images is missed')

        invalid = next((img for img in images if img.content_type not in ALLOWED_CONTENT_TYPE), None)
        if invalid:
            return JsonResponse({
                'error': 'Недопустимый формат файла. Разрешен: JPEG.'
            }, status=400)
        procced_res = []

        handler = ProcessImageView()
        for img in images:
            processed_url, processed_filename, original_size, compressed_size, compressed_rate, original_path, original_name = handler.imageProccesing(
                img)
            procced_res.append(
                {'image_url': processed_url, 'image_name': processed_filename, 'original_size': original_size,
                 'compressed_size': compressed_size, 'compressed_rate': compressed_rate,
                 'original_path': original_path, 'original_name': original_name})

        request.session['processed_url'] = procced_res

        return render(request, 'mainApp/Compressor.html', {
            'title': title,
            'header': header,
            'processed_images': procced_res,
            'is_compress': True,
            'content_type': content_type,
            'compression_level': 90,
        })

    return render(request, 'mainApp/Compressor.html', {'title': title,
                                                       'header': header,
                                                       'content_type': content_type
                                                       })


@require_http_methods(['GET', 'POST'])
def SVGCompressor(request):
    content_type = 'image/svg+xml'
    title = 'SVG-Compressor'
    header = 'Компрессор SVG'
    if request.method == 'POST':

        images = request.FILES.getlist('images')
        if not images:
            return Http404('Images is missed')

        invalid = next((img for img in images if img.content_type not in ALLOWED_CONTENT_TYPE), None)
        if invalid:
            return JsonResponse({
                'error': 'Недопустимый формат файла. Разрешен: SVG.'
            }, status=400)
        procced_res = []

        handler = ProcessImageView()
        for img in images:
            processed_url, processed_filename, original_size, compressed_size, compressed_rate, original_path, original_name = handler.imageProccesing(
                img)
            procced_res.append(
                {'image_url': processed_url, 'image_name': processed_filename, 'original_size': original_size,
                 'compressed_size': compressed_size, 'compressed_rate': compressed_rate,
                 'original_path': original_path, 'original_name': original_name})

        request.session['processed_url'] = procced_res

        return render(request, 'mainApp/Compressor.html', {
            'title': title,
            'header': header,
            'processed_images': procced_res,
            'is_compress': True,
            'content_type': content_type,
            'compression_level': 90,
        })

    return render(request, 'mainApp/Compressor.html', {'title': title,
                                                       'header': header,
                                                       'content_type': content_type})


@require_http_methods(['GET', 'POST'])
def webPCompressor(request):
    allow_type = 'image/webp'
    title = 'WebP-Compressor'
    header = 'Компрессор WebP'
    if request.method == 'POST':

        images = request.FILES.getlist('images')
        if not images:
            return Http404('Images is missed')
        procced_res = []
        invalid = next((img for img in images if img.content_type not in ALLOWED_CONTENT_TYPE), None)
        if invalid:
            return JsonResponse({
                'error': 'Недопустимый формат файла. Разрешен: WebP.'
            }, status=400)
        handler = ProcessImageView()
        for img in images:
            processed_url, processed_filename, original_size, compressed_size, compressed_rate, original_path, original_name = handler.imageProccesing(
                img)
            procced_res.append(
                {'image_url': processed_url, 'image_name': processed_filename, 'original_size': original_size,
                 'compressed_size': compressed_size, 'compressed_rate': compressed_rate,
                 'original_path': original_path, 'original_name': original_name})

        request.session['processed_url'] = procced_res

        return render(request, 'mainApp/Compressor.html', {
            'title': title,
            'header': header,
            'processed_images': procced_res,
            'is_compress': True,
            'content_type': allow_type,
            'compression_level': 90,
        })

    return render(request, 'mainApp/Compressor.html', {'title': title,
                                                       'header': header,
                                                       'content_type': allow_type
                                                       })


@require_http_methods(['GET', 'POST'])
def Converter(request):
    content_type = "image/webp, image/png, image/jpeg"
    title = 'Converter'
    header = 'Конвертер'
    data = {'title': title, 'header': header, 'content_type': content_type, 'is_compress': False}
    return render(request, 'mainApp/Converter.html', context=data)


@require_http_methods(['GET', 'POST'])
def toJPG(request):
    content_type = "image/webp, image/png, image/jpeg"
    title = 'to-JPG-Converter'
    header = 'Конвертер в JPG'
    data = {'title': title, 'header': header, 'content_type': content_type}
    if request.method == 'POST':

        images = request.FILES.getlist('images')
        if not images:
            return Http404('Images is missed')
        invalid = next((img for img in images if img.content_type not in ALLOWED_CONTENT_TYPE), None)
        if invalid:
            return JsonResponse({
                'error': 'Недопустимый формат файла. Разрешены: PNG, JPEG, WebP, SVG.'
            }, status=400)
        procced_res = []

        for img in images:
            handler = ProcessImageView()
            to_convert = 'JPG'
            processed_url, processed_filname = handler.convertImages(img, to_convert)
            procced_res.append({'image_url': processed_url, 'image_name': processed_filname})

        request.session['processed_url'] = procced_res

        return render(request, 'mainApp/Converter.html', {
            'title': title,
            'header': header,
            'processed_images': procced_res,
            'is_compress': False,
            'content_type': content_type
        })
    return render(request, 'mainApp/Converter.html', context=data, )


@require_http_methods(['GET', 'POST'])
def toPNG(request):
    content_type = 'image/webp, image/png, image/jpeg'
    title = 'to-PNG-Converter'
    header = 'Конвертер в PNG'
    data = {'title': title, 'header': header, 'content_type': content_type}
    if request.method == 'POST':

        images = request.FILES.getlist('images')
        if not images:
            return Http404('Images is missed')

        invalid = next((img for img in images if img.content_type not in ALLOWED_CONTENT_TYPE), None)
        if invalid:
            return JsonResponse({
                'error': 'Недопустимый формат файла. Разрешены: PNG, JPEG, WebP, SVG.'
            }, status=400)
        procced_res = []

        for img in images:
            handler = ProcessImageView()
            to_convert = 'PNG'
            processed_url, processed_filname = handler.convertImages(img, to_convert)
            procced_res.append({'image_url': processed_url, 'image_name': processed_filname})

        request.session['processed_url'] = procced_res

        return render(request, 'mainApp/Converter.html', {
            'title': title,
            'header': header,
            'processed_images': procced_res,
            'is_compress': False,
            'content_type': content_type
        })
    return render(request, 'mainApp/Converter.html', context=data)


@require_http_methods(['GET', 'POST'])
def toWebP(request):
    title = 'to-WebP-Converter'
    content_type = 'image/webp, image/png, image/jpeg'
    header = 'Конвертер в WebP'
    data = {'title': title, 'header': header, 'content_type': content_type}
    if request.method == 'POST':

        images = request.FILES.getlist('images')
        if not images:
            return Http404('Images is missed')

        invalid = next((img for img in images if img.content_type not in ALLOWED_CONTENT_TYPE), None)
        if invalid:
            return JsonResponse({
                'error': 'Недопустимый формат файла. Разрешены: PNG, JPEG, WebP, SVG.'
            }, status=400)
        procced_res = []

        for img in images:
            handler = ProcessImageView()
            to_convert = 'WEBP'
            processed_url, processed_filname = handler.convertImages(img, to_convert)
            procced_res.append({'image_url': processed_url, 'image_name': processed_filname})

        request.session['processed_url'] = procced_res

        return render(request, 'mainApp/Converter.html', {
            'title': title,
            'header': header,
            'processed_images': procced_res,
            'is_compress': False,
            'content_type': content_type
        })
    return render(request, 'mainApp/Converter.html', context=data)


@require_http_methods(['GET', 'POST'])
def toSVG(request):
    title = 'to-SVG-Converter'
    content_type = 'image/webp, image/png, image/jpeg, image/svg+xml'
    header = 'Конвертер в SVG'
    data = {'title': title, 'header': header, 'content_type': content_type}
    if request.method == 'POST':

        images = request.FILES.getlist('images')
        if not images:
            return Http404('Images is missed')

        invalid = next((img for img in images if img.content_type not in ALLOWED_CONTENT_TYPE), None)
        if invalid:
            return JsonResponse({
                'error': 'Недопустимый формат файла. Разрешены: PNG, JPEG, WebP, SVG.'
            }, status=400)
        procced_res = []

        for img in images:
            handler = ProcessImageView()
            to_convert = 'SVG'
            processed_url, processed_filname = handler.convertImages(img, to_convert)
            procced_res.append({'image_url': processed_url, 'image_name': processed_filname})

        request.session['processed_url'] = procced_res

        return render(request, 'mainApp/Converter.html', {
            'title': title,
            'header': header,
            'processed_images': procced_res,
            'is_compress': False,
            'content_type': content_type
        })
    return render(request, 'mainApp/Converter.html', context=data)
