import zipfile
import os.path
import mimetypes
import re
import xml.dom.minidom

#this is a comment

class BadEpubFile (Exception):
    pass
        
def _checkfile (filename, mode="r"):
    try:
        testfile = zipfile.ZipFile(filename, mode)
    except zipfile.BadZipfile:
        raise BadEpubFile, "file is not an Epub File"
    return testfile

def lxmlNStagtolist (element):
    plonk = re.match("(\{[^\}]*\})?(.*)", element)
    return [plonk.group(1), plonk.group(2)]

def _getcontainer (archive):
    try:
        container = archive.open(os.path.join("META-INF", "container.xml"))
    except KeyError:
        raise BadEpubFile, "Unable to open META-INF/container.xml"
    return container
    #return archive.open("mimetype")

def _getrootfile (archive, container):
    try:
        dom = xml.dom.minidom.parse(container)
        dom.normalize()
    except:
        raise BadEpubFile, "META-INF/container.xml is invalid XML"
    
    try: 
        rootfile = dom.getElementsByTagName("rootfile")[0]
    except:
        raise BadEpubFile, "META-INF/container.xml is improperly formatted (unable to find rootfile)"
    
    try:
        root = archive.open(rootfile.getAttribute("full-path"))
    except:
        raise BadEpubFile, "There is no item named '%s' in this epubfile" % rootfile.getAttribute("full-path")
    
    try:
        rootdom = xml.dom.minidom.parse(root)
        rootdom.normalize()
    except:
        raise BadEpubFile, "'%s' is invalid XML" % rootfile.getAttribute("full-path")
    
    return [rootdom, rootfile.getAttribute("full-path")]

def _filerelpath (opfpath, target):
    return os.path.relpath(target, os.path.dirname(opfpath))


class EpubItem (object):
    def __init__ (self, archive, archloc):
        self.archloc = archloc
        self.opfRelLoc = None
        self.idref = None
        self.opf = False
        self.opfid = None
        self.spine = False
        self.ncx = False
        self.linear = False
        self.refs = []
        self.mimetype = "text/plain"
        self.archive = archive
        
    def read (self):
        try:
            out = self.archive.open(self.archloc, "r")
        except:
            raise IOError, "Cannot open '%s' for reading" % self.archloc
        return out.read()
    
    def write (self, input, stor=False):
        try:
            out = self.archive.open(self.archloc, "w")
        except:
            raise IOError, "Cannot open '%s' for writing" % self.archloc
        
        if stor == False:
            comptype = zipfile.ZIP_STORED
        else:
            comptype = zipfile.ZIP_DEFLATED
            
        if os.path.exists(input):
            try:
                out.write(input, self.archloc, comptype)
            except:
                raise IOError, "Cannot write to  '%s'" % self.archloc
        else:
            try:
                out.writestr(self.archloc, input, comptype)
            except:
                raise IOError, "Cannot write to  '%s'" % self.archloc


class metadata ():
    def __init__ (self):
        self.data = {"title":[],
                   "creator":[],
                   "subject":[],
                   "description":[],
                   "publisher":[],
                   "contributor":[],
                   "date":[],
                   "type":[],
                   "format":[],
                   "identifier":[],
                   "source":[],
                   "language":[],
                   "relation":[],
                   "coverage":[],
                   "rights":[],
                   "meta":[]
                   }
    
    def read (self, opfdom):
        #Name spaces are frickin annoying I have discovered, please see below for retardation
        
        meta = opfdom.getElementsByTagName("metadata")[0]
        #self.metaNs = meta.nsmap        
        for node in opfdom.getElementsByTagName("metadata").childNodes:
            meta = {}
            tagname = node.tagName
            
            self.dc
            
            if tagname.tolower() == "title":
                self.Title = node.firstChild.data
            if tagname.tolower() == "creator":
                self.Title = node.firstChild.data
            if tagname.tolower() == "subject":
                self.Title = node.firstChild.data
            if tagname.tolower() == "description":
                self.Title = node.firstChild.data
            if tagname.tolower() == "publisher":
                self.Title = node.firstChild.data
            if tagname.tolower() == "contributor":
                self.Title = node.firstChild.data
            if tagname.tolower() == "date":
                self.Title = node.firstChild.data
            if tagname.tolower() == "type":
                self.Title = node.firstChild.data
            if tagname.tolower() == "format":
                self.Title = node.firstChild.data
            if tagname.tolower() == "identifier":
                self.Title = node.firstChild.data
            if tagname.tolower() == "source":
                self.Title = node.firstChild.data
            if tagname.tolower() == "language":
                self.Title = node.firstChild.data
            if tagname.tolower() == "relation":
                self.Title = node.firstChild.data
            if tagname.tolower() == "coverage":
                self.Title = node.firstChild.data
            if tagname.tolower() == "rights":
                self.Title = node.firstChild.data
            meta["tag"] = tagname
        
    
class OPF ():
    def __init__ (self, opfpath, opfdom, filelist):
        self.clearopf()
        self.opfdom = opfdom
        self.opfpath = opfpath
        self.filelist = filelist
        self.NCXfile = None
        
    def clearopf (self):
        self.manifest = []
        self.spine = []
        self.meta = []
        self.refs = []
        
    def read (self):
        self._readmeta()
        self._readmanifest()
        self._readspine()
        self._readrefs()
    
    def getref (self):
        dosomething = 1
    
    def _readmanifest (self):
        protomani = self.opfdom.getElementsByTagName("manifest")[0]
        for node in protomani.getElementsByTagName("item"):
            relpath = _filerelpath(self.opfpath, os.path.join(os.path.dirname(self.opfpath), node.getAttribute('href')))
            abspath = os.path.join(os.path.dirname(self.opfpath), relpath)
            for item in self.filelist:
                if item.archloc == abspath:
                    if node.getAttribute("id"):
                        item.opfid = node.getAttribute("id")
                    if node.getAttribute("media-type"):
                        item.mimetype = node.getAttribute("media-type")
                    item.opf = True
                    item.opfRelLoc = relpath
                    self.manifest.append(item)
                    
    def _readmeta (self):
        dotsomething =1 
                    
    def _readspine (self):
        spine = self.opfdom.getElementsByTagName("spine")[0]
        if spine.getAttribute("toc"):
            for item in self.manifest:
                if spine.getAttribute("toc") == item.opfid:
                    self.NCXfile = item.archloc
        
        for node in spine.getElementsByTagName("itemref"):
            for item in self.manifest:
                if item.opfid == node.getAttribute("idref"):
                    if not node.getAttribute("linear") == "no":
                        item.linear = True
                    item.spine = True
                    self.spine.append(item)
                    
    def _readrefs (self):
        refs = self.opfdom.getElementsByTagName("guide")[0]
        for node in refs.getElementsByTagName("reference"):
            for item in self.filelist:
                if item.archloc == node.getAttribute("href"):
                    item.refs.append([node.getAttribute("type"), node.getAttribute("title")])
                    self.refs.append([node.getAttribute("type"), node.getAttribute("title"), item])
class NCX:
    def __init__ (self, ncxfile):
        self.ncx = ncxfile
        
        
        
                

class EpubInfo (object):
    def __init__ (self, filename=None):
        dosomethinghere = 1

class EpubFile:
    def __init__ (self, filename=None, mode="r"):
        if filename:
            self.epubarch = _checkfile(filename, mode)
            container =_getcontainer(self.epubarch)
            [self.rootfile, rootpath] = _getrootfile(self.epubarch,container)
            self.filelist = self._readContents()
            #for item in self.filelist:
            #    print item.archloc, item.mimetype
            self.opf = OPF(rootpath, self.rootfile, self.filelist)
            self.opf._readmeta()
            self.opf._readmanifest()
            self.opf._readspine()
            self.opf._readrefs()
            
    def _readContents (self):
        out = []
        for oriItem in self.epubarch.infolist():
            item = EpubItem(self.epubarch, oriItem.filename)
            item.mimetype = mimetypes.guess_type(oriItem.filename)[0]
            out.append(item)
        return out
    
    def _readOPF (self):
        dosomthing = 1 
    