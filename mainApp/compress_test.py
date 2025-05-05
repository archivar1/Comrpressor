import pyvips
image = 'D:/progi/Compressor/Compressor/media/temp_images/procced_test (1).jpeg'
img =pyvips.Image.new_from_file(image,access='sequential')
img.write_to_file('temp.jp2', Q=30)
compress_image = pyvips.Image.new_from_file('temp.jp2', access='sequential')
compress_image.write_to_file('output.jpg', Q=85)