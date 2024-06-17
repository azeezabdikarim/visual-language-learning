import exifread

def get_img_metadata(img_path):
    with open(img_path, 'rb') as f:
        tags = exifread.process_file(f)
    desired_keys = ['Image DateTime', ' GPS GPSLatitudeRef', 'GPS GPSLatitude', 'GPS GPSLongitudeRef', 'GPS GPSLongitude', 
                    'GPS GPSAltitudeRef', 'GPS GPSAltitude', 'GPS GPSTimeStamp', 'GPS GPSSpeedRef', 'GPS GPSSpeed', 'GPS GPSDate']
    
    metadata = {key: str(tags.get(key, None)) for key in desired_keys}
    return metadata