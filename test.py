#!/usr/bin/python

import epub
import os


#test = epub.epubFile(os.path.join(os.path.dirname(__file__), "test_files/sample_file.epub"))
#test = epub.epubFile(os.path.join(os.path.dirname(__file__), "test_files/sample_file.epub"))
test = epub.epubFile(os.path.join(os.path.dirname(__file__), "test_files/arduino.epub"))

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
#for item in test.info.opf.spine:
#	print item.opfRelLoc

#random test 1
#item = test.info.opf.manifest[1]
#print item.info()

metadata = test.info.meta

#meta data test
#print(test.info.meta.data)

#meta data test2
#metadata.addDataTemplate("test", "test", None, None,  metadata.UNIQUE | metadata.UNIQUE)

#meta data test3
#print metadata._testFlag(metadata.REQUIRED | metadata.TEXTVALUE | metadata.ATTRVALUE, metadata.REQUIRED)

#meta data test4
print(metadata.getMetaData("cover").opfRelLoc)
print(metadata.getMetaData("title"))
print(metadata.getMetaData("author"))
print(metadata.getMetaData("identifer"))
print(metadata.getMetaData("language"))
print(metadata.getMetaData("description"))
print(metadata.getMetaData("date"))
print(metadata.getMetaData("datepub"))
print(metadata.getMetaData("datemod"))


#id finder test
#test.info.findIDreferences("navPoint-6")
#test.info.findIDreferences()