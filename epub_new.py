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
        self.opfRelLoc = None
        self.idref = None
        self.opf = False
        self.opfid = None
        self.spine = False
        self.ncx = False
        self.opfEl = None
        self.linear = False
        self.ignore = False
        self.lastModified = None
        self.refs = []
        self.mimetype = "text/plain"

    def open(self):
        pass

    def read(self):
        pass

    def write(self):
        pass

    def __exit__():
        pass


class META(object):
    """docstring for META"""
    def __init__(self, info):
        self.opf = info.opf
        self.ncx = info.ncx


class OPF():
    """docstring for OPF"""
    def __init__(self, path, contents):
        self.opf = path
        self.contents = None
        self.manifest = []
        self.spine = []
        self.guide = []
        self.ncxFilename = None

    def read(self):
        pass

    def update(self):
        pass

    def findItemFromPath(self, path, src=None):
        pass

    def _getNcxFilename(self):
        pass

    def _getManifest(self):
        pass

    def _getSpine(self):
        pass

    def _getGuide(self):
        pass

    def _createItem(self, args):
        pass


class NCX(object):
    """docstring for NCX"""
    def __init__(self, contents, opf):
        self.opf = opf
        self.path = opf.ncxFilename


class epubInfo(object):
    """docstring for epubInfo"""
    def __init__(self, path):
        self.path = path
        self.opf = OPF(self)
        self.ncx = NCX(self)
        self.meta = META(self)
        self.contents = []
        self.container = "META-INF/container.xml"
        self.opfLocation = None

    def _isArchive(self):
        if self.path and os.path.exists(os.path.normalise(self.path)):
            print type(self.path)

    def _readArchive(self):
        pass

    def _readDir(self):
        pass

    def update(self):
        pass

    def _getOPFLocation(self):
        pass


class epubFile(object):
    """docstring for epubFile"""
    def __enter__(self, path=None, openFor="r"):
        return self

    def __init__(self, path=None, openFor="r"):
        self.path = path
        self.info = epubInfo(self.path)
        self.tmpLocation = None

    def __del__(self):
        if self.tmpLocation and os.path.exists(self.tmpLocation):
            shutil.rmtree(self.tmpLocation)

    def __exit__(self, type, value, traceback):
        if self.tmpLocation and os.path.exists(self.tmpLocation):
            shutil.rmtree(self.tmpLocation)

