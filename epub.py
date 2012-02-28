import zipfile
import os.path
import mimetypes
import re
from lxml import etree

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
        dom = etree.parse(container)
    except:
        raise BadEpubFile, "META-INF/container.xml is invalid XML"
    
    try: 
        rootfile = dom.xpath("//*[local-name() = 'rootfile']")[0]
    except:
        raise BadEpubFile, "META-INF/container.xml is improperly formatted (unable to find rootfile)"
    
    try:
        root = archive.open(rootfile.get("full-path"))
    except:
        raise BadEpubFile, "There is no item named '%s' in this epubfile" % rootfile.get("full-path")
    
    try:
        rootdom = etree.parse(root)
    except:
        raise BadEpubFile, "'%s' is invalid XML" % rootfile.get("full-path")
    
    return [rootdom, rootfile.get("full-path")]

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
        self.Title = None
        self.Creator = None
        self.Subject = None
        self.Description = None
        self.Publisher = None
        self.Contributor = None
        self.Date = None
        self.Type = None
        self.Format = None
        self.Identifier = None
        self.Source = None
        self.Language = None
        self.Relation = None
        self.Coverage = None
        self.Rights = None
        self.about = None
        self.cover = None
        self.other = []
    
    def read (self, opfdom):
        #Name spaces are frickin annoying I have discovered, please see below for retardation
        meta = opfdom.xpath("//*[local-name() = 'metadata']/*")[0]
        self.metaNs = meta.nsmap        
        for node in opfdom.xpath("//*[local-name() = 'metadata']/*"):
            meta = {}
            [nsurl, tagname] = lxmlNStagtolist(node.tag)
            dcns = "{http://purl.org/dc/elements/1.1/}"
            opf = ""
            if nsurl == dcns:
                if tagname == "title":
                    self.Title = node.value
                if tagname == "Creator":
                    self.Title = node.value
                if tagname == "title":
                    self.Title = node.value
                if tagname == "title":
                    self.Title = node.value
                if tagname == "title":
                    self.Title = node.value
                if tagname == "title":
                    self.Title = node.value
                if tagname == "title":
                    self.Title = node.value
            meta["nsurl"] = nsurl
            meta["tag"] = tagname
            for ns in self.metaNs:
                if "{"+self.metaNs[ns]+"}" == nsurl:
                    if ns == None:
                        ns = ""
                    else:
                        ns = ns+":"
                    meta["nstag"] = ns+tagname
                    
            if node.attrib:
                meta["attr"] = {}
                for attr in node.attrib:
                    [nsurl, attrname] = lxmlNStagtolist(attr)
                    attrId = False
                    for ns in self.metaNs:
                        if "{"+self.metaNs[ns]+"}" == nsurl:
                            if ns == None:
                                ns = ""
                            else:
                                ns = ns+":"
                            attrId = ns+attrname
                    if attrId:
                        meta["attr"][attrId] = {attr:node.attrib[attr]} 

            if node.text:
                meta["value"] = node.text
        
        if len(meta) > 0:
            for ele in meta:
                if ele["nstag"] == "dc:title":
                    self.Title = ele["value"]
                if ele["nstag"] == "dc:creator":
                    self.Title = ele["value"]
                if ele["nstag"] == "dc:identifier":
                    self.Title = ele["value"]
        
    
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
        for node in self.opfdom.xpath("//*[local-name() = 'manifest']//*[local-name() ='item']"):
            relpath = _filerelpath(self.opfpath, os.path.join(os.path.dirname(self.opfpath), node.get('href')))
            abspath = os.path.join(os.path.dirname(self.opfpath), relpath)
            for item in self.filelist:
                if item.archloc == abspath:
                    if node.get("id"):
                        item.opfid = node.get("id")
                    if node.get("media-type"):
                        item.mimetype = node.get("media-type")
                    item.opf = True
                    item.opfRelLoc = relpath
                    self.manifest.append(item)
                    
    def _readmeta (self):
        dotsomething =1 
                    
    def _readspine (self):
        spine = self.opfdom.xpath("//*[local-name() = 'spine']")[0]
        if spine.get("toc"):
            for item in self.manifest:
                if spine.get("toc") == item.opfid:
                    self.NCXfile = item.archloc
        
        for node in self.opfdom.xpath("//*[local-name() ='spine']//*[local-name() ='itemref']"):
            for item in self.manifest:
                if item.opfid == node.get("idref"):
                    if not node.get("linear") == "no":
                        item.linear = True
                    item.spine = True
                    self.spine.append(item)
                    
    def _readrefs (self):
        for node in self.opfdom.xpath("//*[local-name() ='guide']//*[local-name() ='reference']"):
            for item in self.filelist:
                if item.archloc == node.get("href"):
                    item.refs.append([node.get("type"), node.get("title")])
                    self.refs.append([node.get("type"), node.get("title"), item])
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
    