#!/usr/bin/python

# Using Python Image Library (PIL)
# Download at http://www.pythonware.com/products/pil/]

from PIL import Image
import epub
import StringIO

epub.EpubFile


#test = epub.EpubFile("/home/nic/workspace/epubfile/testfiles/testpub.epub")
test = epub.EpubFile("C:/Users/Edward/Documents/Aptana Studio 3 Workspace/ios2m/samples/text.epub")

for item in test.opf.manifest:
    if str.startswith(str(item.mimetype), "image") == True:
        print item.archloc
        bitches = StringIO.StringIO()
        image_file = item.read()
        bitches.write(image_file)
        print image_file
        img = Image.open(bitches)