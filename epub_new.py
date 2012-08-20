import zipfile
import os.path
import mimetypes
import re
import xml.dom.minidom
import tempfile
import shutil


class badEpubFile(Exception):
    """Main Exception"""
    pass


class epubError(badEpubFile):
    """Error handling"""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class epubItem(object):
    """central location for opf/ncx data"""
    def __init__(self):

        # archive zipfile object
        self.archive = None

        # abspath to extracted content (if set ~= you are working with an extracted folder not a zipfile)
        self.absLoc = None

        # node id as defined in the OPF
        self.opfid = None

        # OPF relative path
        self.opfRelLoc = None

        # zipInfo data
        self.compressiontype = zipfile.ZIP_DEFLATED
        self.compressed_size = 0
        self.file_size = 0
        self.lastmodified = None

        # mimetype as defined in OPF
        self.mimetype = "text/plain"

        # is present in the ncx
        self.ncx = False

        # is present in the opf
        self.opf = False

        # is present in the spine (i.e. is file that will be read by the reader)
        self.spine = False

        # opf dom mainfest node
        self.opfEl = None

        # is a file to ignore when extracting/compressing
        self.ignore = False

        # is linear in spine (default is generally true)
        self.linear = True

        # guide references as defined in the OPF
        self.refs = []

    def open(self, openFor="r"):
        """Open item for reading/writing"""
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
        """Open Item for reading only"""
        try:
            f = self.open()
            c = f.read()
            f.close()
            return c
        except:
            return None

    def write(self):
        """write file to epubFile"""
        pass

    def info(self):
        """return all info in an arrary"""
        return [self.compressiontype, self.compressed_size, self.file_size,
                self.ignore, self.linear, self.lastmodified, self.mimetype,
                self.ncx, self.opf, self.opfEl, self.opfid, self.opfRelLoc,
                self.spine, self.refs, self.rootRelLoc]

    def __exit__():
        pass


class epubContents(object):
    """epubItems container

    useful for search and path to epubItem fuctions
    """
    def __init__(self, contents):
        # contentsArr inherited from epubInfo
        self.contents = contents

        # Directory of file root relative paths to items
        self.rootRelDir = {}

        # Directory of opf file relative paths to items
        self.opfRelDir = {}

        # Directory of absolute paths to items
        self.absRelDir = {}

        # Directory of OPF manifest ID's to items
        self.opfIdDir = {}

    def update(self, contents=None):
        """Updates epubContents from a contentsArr"""
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
        "get epubItem object from file root relative path"
        try:
            return self.rootRelDir[str(path)]
        except:
            raise epubError("No epub item associated with root path '%s'" % str(path))

    def getItemFromOpf(self, path):
        "get epubItem object from opf file relative path"
        try:
            return self.opfRelDir[str(path)]
        except:
            raise epubError("No epub item associated with opf path '%s'" % str(path))

    def getItemFromAbs(self, path):
        "get epubItem object from file absolute relative path"
        try:
            return self.absRelDir[str(path)]
        except:
            raise epubError("No epub item associated with absolute path '%s'" % str(path))

    def getItemFromOpfId(self, opfId):
        "get epubItem object from opf manifest ID"
        try:
            return self.opfIdDir[str(opfId)]
        except:
            raise epubError("No epub item associated with opf Id '%s'" % str(opfId))


class META(object):
    """docstring for META"""
    def __init__(self, opfDom, ncxDom, contents):
        self.opfDom = opfDom
        self.ncxDom = ncxDom
        self.contents = contents
        self.metaDom = None

        self.data = {}
        self.templates = {
                    "title": {"name": "dc:title", "attr": None, "id": None, "unique": False, "required": True},
                    "author": {"name": "dc:creator", "attr": [("opf:role", "aut")], "id": None, "unique": False, "required": True},
                    "identifer": {"name": "dc:identifier", "attr": [("opf:scheme", None)], "id": None, "unique": False, "required": True},
                    "language": {"name": "dc:language", "attr": None, "id": None, "unique": False, "required": True},
                    "cover": {"name": "meta", "attr": [("name", "cover"), ("content", None)], "id": None, "unique": True, "required": True},
                    }
        self.getMetaDom()
        self.getData()

    def getMetaDom(self):
        # check for metadata in OPF
        if len(self.opfDom.getElementsByTagName("metadata")) > 0:
            self.metaDom = self.opfDom.getElementsByTagName("metadata")[0]
        else:
            return False

    def _loopNodes(self, parent, cnodes=[]):
        for node in parent.childNodes:
            if not node.nodeType == node.TEXT_NODE:
                cnodes.append(node)
                if len(node.childNodes):
                    cnodes = self._loopNodes(node, cnodes)
        return cnodes

    def addDataTemplate(self, name, nodeName, attr=None, nid=None, unique=False, required=None):
        if not name in self.templates:
            self.templates[name] = {"name": nodeName, "attr": attr, "id": nid, "unique": unique, "required": required}
        else:
            print "Already a template with the name '%s' (this name must be unique to the template array and should not be confused with node name)" % name

    def getData(self):
        self.data = []
        for node in self._loopNodes(self.metaDom):
            for temp_name, temp_pattern in self.templates.iteritems():
                if self._testNodeAgainstTemplate(node, temp_pattern):
                    if not temp_name in self.data:
                        self.data[temp_name] = []
                    self.data[temp_name].append(node)

    def _testNodeAgainstTemplate(self, node, template):
        if node.nodeName == template["name"]:
            if template["attr"]:
                if not node.hasAttributes():
                    return False
                for attr in template["attr"]:
                    attr_name = attr[0]
                    attr_value = attr[1]
                    if not node.hasAttribute(attr_name):
                        return False
                    if attr_value:
                        if not node.getAttribute(attr_name) == attr_value:
                            return False
            if template["id"]:
                if node.hasAttribute("id"):
                    if not node.getAttribute(attr_name) == template["id"]:
                        return False
                else:
                    return False
            return True

        else:
            return False

class OPF():
    """OPF handling class"""
    def __init__(self, opfLocation, contents):
        # location of OPF file
        self.location = opfLocation

        # location of NCX file
        self.ncxLocation = None

        # contentsArr inherited from epubInfo
        self.contents = contents

        # opf xml dom
        self.opfdom = None

        self.clearopf()
        self.update()

    def clearopf(self):
        """clears section arrays"""
        self.manifest = []
        self.spine = []
        self.guide = []

    def read(self):
        """reads opf file as xml dom"""
        # open the file
        try:
            rootItem = self.contents.getItemFromRoot(self.location)
            root = rootItem.open()
        except:
            raise epubError("There is no item named '%s' in this epubfile" % self.location)

        # parse the file as xml
        try:
            self.opfdom = xml.dom.minidom.parse(root)
            self.opfdom.normalize()
        except:
            raise epubError("'%s' is invalid XML" % self.location)

    def update(self):
        """populate sections from OPF dom"""
        self.read()
        self._getManifest()
        self._getSpine()
        self._getGuide()

    def _getManifest(self):
        """matches nodes in OPF manifest to epubItems in epubContents"""

        # check manifest exists
        if len(self.opfdom.getElementsByTagName("manifest")) > 0:

            # manifest only dom
            protomani = self.opfdom.getElementsByTagName("manifest")[0]

            # loop over child "item" nodes
            for node in protomani.getElementsByTagName("item"):

                # opf relative path as defined in OPF
                relpath = node.getAttribute('href')

                # root path in (imaginary)? zipfile
                rootpath = os.path.dirname(self.location) + "/" + relpath

                # get epubItem from contents and set relevant data
                item = self.contents.getItemFromRoot(rootpath)
                item.opf = True
                item.opfEl = node
                item.opfRelLoc = relpath
                if node.getAttribute("id"):
                    item.opfid = node.getAttribute("id")
                if node.getAttribute("media-type"):
                            item.mimetype = node.getAttribute("media-type")
                item.opfRelLoc = relpath

                # add our item to the manifest
                self.manifest.append(item)

            # because we have changed important information in epubItems we need to update epubContents to reflect this
            self.contents.update()

    def _getSpine(self):
        """matches nodes in OPF manifest to epubItems in epubContents"""

        # check spine exists
        if len(self.opfdom.getElementsByTagName("spine")) > 0:
            # spine only dom
            spine = self.opfdom.getElementsByTagName("spine")[0]

            # find the NCX file location
            if spine.getAttribute("toc"):
                item = self.contents.getItemFromOpfId(spine.getAttribute("toc"))
                self.ncxLocation = item.rootRelLoc

            # loop over child "itemref" nodes
            for node in spine.getElementsByTagName("itemref"):

                # get epubItem from contents and relevant data
                item = self.contents.getItemFromOpfId(node.getAttribute("idref"))
                if not node.getAttribute("linear") == "no":
                    item.linear = True
                item.spine = True

                # add our item to the spine
                self.spine.append(item)

            # because we have changed important information in epubItems we need to update epubContents to reflect this
            self.contents.update()

    def _getGuide(self):
        """matches nodes in OPF manifest to epubItems in epubContents"""

        # check guide exists
        if len(self.opfdom.getElementsByTagName("guide")) > 0:

            # guide only dom
            refs = self.opfdom.getElementsByTagName("guide")[0]

            # loop over child "references" nodes
            for node in refs.getElementsByTagName("reference"):

                # get item from OPF relative location
                item = self.contents.getItemFromOpf(node.getAttribute("href"))

                # update the item with it's references
                item.refs.append([node.getAttribute("type"), node.getAttribute("title")])

                # add the epubItem to the guide
                self.guide.append([node.getAttribute("type"), node.getAttribute("title"), item])

            # because we have changed important information in epubItems we need to update epubContents to reflect this
            self.contents.update()


class NCX(object):
    """docstring for NCX"""
    def __init__(self, ncxLocation, contents):
        self.path = ncxLocation
        self.ncxdom = None


class epubInfo(object):
    """Information about and Epub file

    should only really be publicly used for reading data with no intention of writing. if you plan on writing you should be using epubFile() instead
    """
    def __init__(self, path, openFor="r"):
        # epubfile path
        self.path = os.path.abspath(path)

        # Contents of (imagineary)? epubfile
        self.contentsArr = []
        self.contents = epubContents(self.contentsArr)

        # container file (becomes container item I think at the moment and this needs to be fixed)
        self.container = "META-INF/container.xml"

        # zipfile object
        self.archive = None

        # location of OPF file
        self.opfLocation = None

        # loction of extracted temporary files
        self.tmpLocation = None

        # open for reading/writing
        self.openFor = openFor

        # update and get opf location from file container
        self.update()
        self.opfLocation = self._getOPFLocation()

        # OPF Data
        self.opf = OPF(self.opfLocation, self.contents)

        # NCX Data
        self.ncx = NCX(self.opf.ncxLocation, self.contents)

        # Meta data
        self.meta = META(self.opf.opfdom, self.ncx.ncxdom, self.contents)

    def _isArchive(self):
        """this is somewhat retarded but.... meh! it deffinately made sense at the time"""
        if self.path and os.path.exists(self.path):
            return zipfile.is_zipfile(self.path)

    def _readArchive(self):
        """read contents of archive into contents"""
        # create zipfile object
        self.archive = zipfile.ZipFile(self.path, "r")

        # if we want to do some writing then we need to extract to a tmp folder as you can't read and write from a zipfile at the same time
        if self.openFor == "w":
            self.tmpLocation = tempfile.mkdtemp()
            self.archive.extractall(self.tmpLocation)

        # build epubItems from contents of zipfile
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

            # add this epubItem to the contents array
            self.contentsArr.append(item)

            # if this item is the container file then cheesecake
            if item.rootRelLoc == self.container:
                self.container = item
        # epubItems have changed so we need to update epubContents for serch etc.
        self.contents.update(self.contentsArr)

    def _readDir(self):
        """read contents of directory as an extracted epubfile"""
        pass

    def update(self):
        """updates objects from source"""
        if self._isArchive():
            self._readArchive()
        elif os.path.isdir(self.path):
            self._readDir()
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
        # destory tempfiles when done
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
