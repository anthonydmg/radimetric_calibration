import exifread
import json

file = open("./RGB/IMG_00366.jpg", 'rb')
exif_data = exifread.process_file(file, details= False)
print(exif_data)
file.close()

#with open("exif_data.json", "w") as f: 
#    json.dump(exif_data, f)