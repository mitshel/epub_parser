#!/usr/bin/python

# Using Python Image Library (PIL)
# Download at http://www.pythonware.com/products/pil/]

from PIL import Image
import epub
import math
from StringIO import StringIO

epub.EpubFile


test = epub.EpubFile("/home/nic/Desktop/Ebooks/Random_House/1309/9781446488140.epub")
#test = epub.EpubFile("C:/Users/Edward/Documents/Aptana Studio 3 Workspace/ios2m/samples/text.epub")
images = 0
images_corrected = 0
for item in test.opf.manifest:
    if str.startswith(str(item.mimetype), "image") == True:
        images = images+1
        img = Image.open(StringIO(item.read()))
        width, height = img.size
        if width*height > 2000000:
            images_corrected = images_corrected+1
            print width, height, width*height
            area = 1900000
            resize = math.sqrt(area)/math.sqrt(width*height)
            print math.floor(width*resize), math.floor(height*resize), (width*resize)*(height*resize)
            #print resize 
            
print "items in manifest: "+str(len(test.opf.manifest))
print "images in manifest: "+str(images)
print "images corrected: "+str(images_corrected)