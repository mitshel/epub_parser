#!/usr/bin/python

import epub_new
import os


test = epub_new.epubFile(os.path.join(os.path.dirname(__file__), "test_files/sample_file.epub"))
#test = epub_new.epubFile(os.path.join(os.path.dirname(__file__), "test_files/sample_file.epub"))

#get opf location test
#print test.info._getOPFLocation()

#contents test
#for item in test.info.contents:
#    print item.info()

#contents test2
#print test.info.contents.opfIdDir
#print test.info.opf.contents.opfIdDir

#manifest test
#for item in test.info.opf.manifest:
#    print item.info()

#spine test
for item in test.info.opf.spine:
	print item.opfRelLoc

#random test 1
#item = test.info.opf.manifest[1]
#print item.info()
