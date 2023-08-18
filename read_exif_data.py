import exifread
import json

file = open("./NIR/IMG_00569.jpg", 'rb')
exif_data = exifread.process_file(file, details= False)
print(exif_data.keys())
file.close()

#with open("exif_data.json", "w") as f:
#    json.dump(exif_data, f)