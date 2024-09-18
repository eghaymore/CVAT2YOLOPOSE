# For use with 'CVAT for Images' .xml annotations
import xml.etree.ElementTree as ET
import re

ANNFPATH = 'annotations.xml'
IMGX = 1280.0
IMGY = 720.0


try:
    tree = ET.parse(ANNFPATH)
    root = tree.getroot()
except:
    print(f'{ANNFPATH} not found')
print(f'Succesfully loaded annoations for {ANNFPATH}')

images = [child for child in root if (child.tag == 'image')]
print(f'Found images: ')
for img in images:
    img_fname = re.sub(r'\.png', '.txt',img.attrib['name'], flags=re.IGNORECASE)
#    print(f'new filename: {img_fname}')
    # Only handling keypoints in this script
    skeletons = [child for child in img if (child.tag == 'skeleton')] 
    print(f"{len(skeletons)} skeleton(s) detected!")
    if (len(skeletons) == 0):
        continue
    print(f"{img.attrib['name']} with skeleton: {skeletons[0].attrib}")
    for skeleton in skeletons:
        points = list()
        for point in skeleton:
            if (point.tag != 'points'):
                print("Only expecting points childs of skeletons")
                continue
            point = point.attrib
            # point: These are dicts with this format: 
            # {'label': 'HubPoint', 'source': 'manual', 'outside': '0', 'occluded': '0', 'points': '714.78,450.13'}
            
            # Parse points values
            pixel_coords = point['points'].split(',')
            occluded = point['occluded']
            label = point['label']
            
            # Map occlusions to YOLO format
            if (occluded == "0"):
                occluded ="2"
            
            # Normalize keypoint coordinate values
            px = round((float(pixel_coords[0])/IMGX), 6)
            py = round((float(pixel_coords[1])/IMGY), 6)
            if (px > 1.0):# Handle keypoint outside of frame
                px = 1.0
            elif (px < 0.0):
                px = 0.0
            if (py > 1.0):
                py = 1.0
            elif (py < 0.0):
                py = 0.0
            #print(f"Keypoint Coordinates for {label}: {px} , {py} , occluded: {occluded}")
            
            # Convert keypoint coordinates and occluded value to a string to write to file
            point_string = str(px) + " " + str(py) + " " + occluded
            points.append((label, point_string))
        
        # Sort keypoints by alphabetical order of label
        # BladePoint1, BladePoint2, BladePoint3, HubPoint, TailPoint
        points = sorted(points, key=lambda x: x[0])
        if (len(points) != 15):
                print("Found a skeleton without 15 keypoints, ignoring it")
                continue
        #for p in points:
        #    print(f"Keypoint Coordinates for {p[0]}: {p[1]}")
        with open(img_fname + ".txt", 'r+') as labels:
            #labels.seek(0)
            #line = labels.readline()  # Read the first line to determine its length
            #end_of_line_position = labels.tell()  # Position after the end of the first line
            #labels.seek(end_of_line_position)
            lines = labels.readlines()  # Read all lines into a list
            output = (" " + points[0][1] + " " + points[1][1] + " " + points[2][1] + " " + points[3][1] + " " + points[4][1]) + " " + points[5][1] + " " + points[6][1] + " " + points[7][1] + " " + points[8][1] + " " + points[9][1] + " " + points[10][1] + " " + points[11][1] + " " + points[12][1] + " " + points[13][1] + " " + points[14][1]
            try:
                lines[-1] = lines[-1].rstrip('\n') + output + '\n'
            except:
                print(f'{img_fname} has no turbine annotations. it may be a background image or a mistake')
                continue
            labels.seek(0)
            labels.write(lines[0])

