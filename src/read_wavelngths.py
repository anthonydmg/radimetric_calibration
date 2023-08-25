import rasterio

def read_wavelengths(dir_name,file_name):
    header_file = f'{dir_name}/{file_name}.bil.hdr'
    data_file = f'{dir_name}/{file_name}.bil'
    with open(header_file, 'r') as hdr_file:
        lines = hdr_file.readlines()
    
    wavelengths = []
    for line in lines:
        if line.startswith('wavelength'):
            values = line.split('{')[1].strip('}\n').split(',')
            wavelengths = [float(value) for value in values]
            break
    with rasterio.open(data_file) as dataset:
        spectra = dataset.read()  

    return wavelengths,spectra

wavelengths, spectra = read_wavelengths("TelaGris","Current Scan")
print("wavelengths:", wavelengths)
print("spectra:", spectra)