#!/usr/bin/python

import epub

epub.EpubFile


#test = epub.EpubFile("/home/nic/workspace/epubfile/testfiles/testpub.epub")
test = epub.EpubFile("/home/nic/Desktop/Ebooks/Random_House/1226/9781446494790.epub")

for item in test.opf.manifest:
    print item.archloc, item.mimetype

#print test