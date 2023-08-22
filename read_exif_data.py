import exifread
import json

file = open("./NIR/IMG_00569.jpg", 'rb')
exif_data = exifread.process_file(file, details= True)
print(exif_data)
file.close()

#with open("exif_data.json", "w") as f:
#    json.dump(exif_data, f)