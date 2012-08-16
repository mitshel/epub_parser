import zipfile
import os.path
import mimetypes
import re
import xml.dom.minidom
import tempfile
import shutil


class badEpubFile(Exception):
    pass


class epubError(badEpubFile):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class epubItem(object):
    """central location for opf/ncx data"""
    def __init__(self):
        self.archive = None
        self.absLoc = None
        self.compressiontype = zipfile.ZIP_DEFLATED
        self.compressed_size = 0
        self.file_size = 0
        self.idref = None
        self.ignore = False
        self.linear = False
        self.lastmodified = None
        self.mimetype = "text/plain"
        self.ncx = False
        self.opf = False
        self.opfEl = None
        self.opfid = None
        self.opfRelLoc = None
        self.spine = False
        self.refs = []
        self.rootRelLoc = None

    def open(self, openFor="r"):
        if self.absLoc:
            try:
                return open(self.absLoc, openFor)
            except:
                raise epubError("Unable to open '%s' for reading" % self.absLoc)
                pass
        elif self.archive:
            try:
                return self.archive.open(self.rootRelLoc)
            except:
                raise epubError("Unable to open '%s' for reading" % self.rootRelLoc)
                pass
        else:
            return None

    def read(self):
        try:
            f = self.open()
            c = f.read()
            f.close()
            return c
        except:
            return None

    def write(self):
        pass

    def info(self):
        return [self.compressiontype, self.compressed_size, self.file_size,
                self.idref, self.ignore, self.linear, self.lastmodified, self.mimetype,
                self.ncx, self.opf, self.opfEl, self.opfid, self.opfRelLoc,
                self.spine, self.refs, self.rootRelLoc]

    def __exit__():
        pass


class epubContents(object):
    """epubItems container"""
    def __init__(self, contents):
        self.contents = contents
        self.rootRelDir = {}
        self.opfRelDir = {}
        self.absRelDir = {}
        self.opfIdDir = {}

    def update(self, contents=None):
        if contents:
            self.contents = contents
        for item in self.contents:
            if item.rootRelLoc:
                self.rootRelDir[str(item.rootRelLoc)] = item
            if item.opfRelLoc:
                self.opfRelDir[str(item.opfRelLoc)] = item
            if item.absLoc:
                self.absRelDir[str(item.absLoc)] = item
            if item.opfid:
                self.opfIdDir[str(item.opfid)] = item

    def getItemFromRoot(self, path):
        try:
            return self.rootRelDir[str(path)]
        except:
            raise epubError("No epub item associated with root path '%s'" % str(path))

    def getItemFromOpf(self, path):
        try:
            return self.opfRelDir[str(path)]
        except:
            raise epubError("No epub item associated with opf path '%s'" % str(path))

    def getItemFromAbs(self, path):
        try:
            return self.absRelDir[str(path)]
        except:
            raise epubError("No epub item associated with absolute path '%s'" % str(path))

    def getItemFromOpfId(self, opfId):
        try:
            return self.opfIdDir[str(opfId)]
        except:
            raise epubError("No epub item associated with opf Id '%s'" % str(opfId))


class META(object):
    """docstring for META"""
    def __init__(self, info):
        self.opf = info.opf
        self.ncx = info.ncx


class OPF():
    """docstring for OPF"""
    def __init__(self, opfLocation, contents):
        self.location = opfLocation
        self.contents = contents
        self.opfdom = None
        self.clearopf()
        self.ncxFilename = None

        self.update()

    def clearopf(self):
        self.manifest = []
        self.spine = []
        self.guide = []

    def read(self):
        try:
            rootItem = self.contents.getItemFromRoot(self.location)
            root = rootItem.open()
        except:
            raise epubError("There is no item named '%s' in this epubfile" % self.location)

        try:
            self.opfdom = xml.dom.minidom.parse(root)
            self.opfdom.normalize()
        except:
            raise epubError("'%s' is invalid XML" % self.location)

    def update(self):
        self.read()
        self._getManifest()
        self._getSpine()
        self._getGuide()

    def _getManifest(self):
        if len(self.opfdom.getElementsByTagName("manifest")) > 0:
            protomani = self.opfdom.getElementsByTagName("manifest")[0]
            for node in protomani.getElementsByTagName("item"):
                relpath = node.getAttribute('href')
                rootpath = os.path.dirname(self.location) + "/" + relpath
                item = self.contents.getItemFromRoot(rootpath)
                item.opf = True
                item.opfEl = node
                item.opfRelLoc = relpath
                if node.getAttribute("id"):
                    item.opfid = node.getAttribute("id")
                if node.getAttribute("media-type"):
                            item.mimetype = node.getAttribute("media-type")
                item.opfRelLoc = relpath
                self.manifest.append(item)
            self.contents.update()

    def _getSpine(self):
        if len(self.opfdom.getElementsByTagName("spine")) > 0:
            spine = self.opfdom.getElementsByTagName("spine")[0]
            if spine.getAttribute("toc"):
                item = self.contents.getItemFromOpfId(spine.getAttribute("toc"))
                self.ncxLocation = item.rootRelLoc

            for node in spine.getElementsByTagName("itemref"):
                item = self.contents.getItemFromOpfId(node.getAttribute("idref"))
                if not node.getAttribute("linear") == "no":
                    item.linear = True
                item.spine = True
                self.spine.append(item)
            self.contents.update()

    def _getGuide(self):
        if len(self.opfdom.getElementsByTagName("guide")) > 0:
            refs = self.opfdom.getElementsByTagName("guide")[0]
            for node in refs.getElementsByTagName("reference"):
                item = self.contents.getItemFromOpf(node.getAttribute("href"))
                item.refs.append([node.getAttribute("type"), node.getAttribute("title")])
                self.guide.append([node.getAttribute("type"), node.getAttribute("title"), item])

            self.contents.update()


class NCX(object):
    """docstring for NCX"""
    def __init__(self, info):
        self.opf = info.opf
        self.path = info.opf.ncxFilename


class epubInfo(object):
    """docstring for epubInfo"""
    def __init__(self, path, openFor="r"):
        self.path = os.path.abspath(path)
        self.contentsArr = []
        self.contents = epubContents(self.contentsArr)
        self.container = "META-INF/container.xml"
        self.archive = None
        self.opfLocation = None
        self.tmpLocation = None
        self.openFor = openFor

        self.update()

        self.opfLocation = self._getOPFLocation()

        self.opf = OPF(self.opfLocation, self.contents)
        self.ncx = NCX(self)
        self.meta = META(self)

    def _isArchive(self):
        if self.path and os.path.exists(self.path):
            return zipfile.is_zipfile(self.path)

    def _readArchive(self):
        self.archive = zipfile.ZipFile(self.path, "r")
        if self.openFor == "w":
            self.tmpLocation = tempfile.mkdtemp()
            self.archive.extractall(self.tmpLocation)

        for member in self.archive.infolist():
            item = epubItem()
            item.archive = self.archive
            if self.openFor == "w":
                item.absLoc = os.path.normpath(os.path.join(self.tmpLocation, member.filename))
            item.rootRelLoc = member.filename
            item.compressiontype = member.compress_type
            item.lastmodified = member.date_time
            item.compressed_size = member.compress_size
            item.file_size = member.file_size
            self.contentsArr.append(item)
            if item.rootRelLoc == self.container:
                self.container = item
        self.contents.update(self.contentsArr)

    def _readDir(self):
        pass

    def update(self):
        if self._isArchive():
            self._readArchive()
        else:
            self.archive = None

    def _getOPFLocation(self):
        """Retreive OPF location from the container.xml file found in META-INF (Internal only)"""
        if self._isArchive():
            try:
                container = self.archive.open(self.container.rootRelLoc)
            except:
                raise epubError("META-INF/container.xml appears to be missing :(")
        elif self.tmpLocation:
            try:
                container = open(self.container.absLoc)
            except:
                raise epubError("META-INF/container.xml appears to be missing :(")

        try:
            dom = xml.dom.minidom.parse(container)
            dom.normalize()
        except:
            raise epubError("META-INF/container.xml is invalid XML")

        try:
            rootfile = dom.getElementsByTagName("rootfile")[0]
        except:
            raise epubError("META-INF/container.xml is improperly formatted (unable to find rootfile)")

        return rootfile.getAttribute("full-path")

    def close(self):
        if self.tmpLocation:
            shutil.rmtree(self.tmpLocation)


class epubFile(object):
    """docstring for epubFile"""
    def __enter__(self, path=None, openFor="r"):
        return self

    def __init__(self, path=None, openFor="r"):
        self.path = path
        self.info = epubInfo(self.path)
        self.tmpLocation = None

    def __del__(self):
        pass

    def __exit__(self, type, value, traceback):
        self.info.close()
