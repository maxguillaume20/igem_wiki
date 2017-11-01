#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple Script to upload multiple HTML, CSS or JS files to the iGEM Wiki.

Copyright under MIT License, see LICENSE.
"""
from __future__ import print_function
from igem_manager import BaseIGemWikiManager
import os
import sys

if sys.version_info[0] < 3:
    from urlparse import urlparse, urlunparse
else:
    from urllib.parse import urlparse, urlunparse

__author__ = "Joeri Jongbloets <joeri@jongbloets.net>"


class IGemFile(object):

    IMAGE_EXTENSIONS = ('jpg', 'jpeg', 'png', 'bmp', 'gif', 'mp4')

    def __init__(self, path, destination=None, prefix=None, mime=None, base=None, **kwargs):
        self._path = path
        self._destination = destination
        # prefix to add to url
        self._prefix = prefix
        # path to remove from full path
        self._base = base
        self._url = None
        self._mime = mime
        self._arguments = kwargs

    @property
    def path(self):
        result = self._path.strip("./")
        if self._base is not None:
            result = self._path.replace(self._base, "", 1)
        # path relative to base
        return result

    @property
    def base_path(self):
        return self._base

    @property
    def full_path(self):
        # full path to file, the way it was found
        return self._path

    @property
    def real_path(self):
        # full path to file, normalized to filesystem root
        return os.path.realpath(self.path)

    @property
    def extension(self):
        extension = os.path.splitext(self.path)[1]
        return extension.strip(".")

    @property
    def prefix(self):
        return self._prefix

    @property
    def destination(self):
        result = self._destination
        if isinstance(result, str):
            result = result.lower()
        return result

    @destination.setter
    def destination(self, d):
        self._destination = d

    @property
    def url(self):
        result = self._url
        if isinstance(result, str):
            result = result.lower()
        return result

    @url.setter
    def url(self, u):
        self._url = u

    @property
    def mime(self):
        return self._mime

    @mime.setter
    def mime(self, m):
        self._mime = m

    def exists(self):
        return os.path.exists(self.full_path)

    def is_html(self):
        return self.extension == "html"

    def is_stylesheet(self):
        return self.extension == "css"

    def is_javascript(self):
        return self.extension == "js"

    def is_image(self):
        return self.extension in self.IMAGE_EXTENSIONS

    def is_resource(self):
        return self.extension not in ("html", "css", "js")

    def __str__(self):
        return "{} => {}".format(self.path, self.destination)


class IGemUploader(BaseIGemWikiManager):

    def __init__(self, team=None, year=None):
        super(IGemUploader, self).__init__(team=team, year=year)
        self._files_collected = {}
        self._files_uploaded = {}
        self._strip_prefix = None
        self._library = None
        self._skip_resources = False
        self._skip_javascripts = False
        self._skip_stylesheets = False
        self._skip_html = False

    @property
    def collected_files(self):
        """Dictionary of all files collected from the given patterns

        :return: Dictionary with path -> IGemFile
        :rtype: dict[str, IGemFile]
        """
        return self._files_collected

    @property
    def uploaded_files(self):
        """List of all files uploaded to the wiki

        :return: Dictionary with url -> IGemFile
        :rtype: dict[str, IGemFile]
        """
        return self._files_uploaded

    @property
    def library(self):
        return self._library

    @library.setter
    def library(self, value):
        self._library = value

    def do_strip(self):
        return self.get_strip() is not None

    def get_strip(self):
        return self._strip_prefix

    def set_strip(self, value):
        self._strip_prefix = value

    def execute(self, action):
        # collect files
        self.collect_patterns(self._files)
        if action == "upload":
            if self.login():
                if isinstance(self.library, str):
                    self.read_library(self.library)
                uploads = self.upload_files()
                self.get_logger().info("Uploaded {} files".format(uploads))
                if isinstance(self.library, str):
                    self.write_library(self.library, self.uploaded_files)
            else:
                self.get_logger().info("Unable to login with the given username/password")

    def collect_patterns(self, patterns):
        results = {}
        for pattern in patterns:
            result = self.collect_pattern(pattern)
            results.update(result)
            self.get_logger().debug("Collected {} files matching pattern {}".format(
                    len(result), pattern
                )
            )
        # do post processing ?!
        self._files_collected = results
        self.get_logger().debug("Collected {} files in total".format(
                len(results)
            )
        )
        return results

    def collect_pattern(self, pattern, base=None):
        import glob
        results = {}
        if self.do_strip():
            if base is None:
                base = self.get_strip()
            if base is None:
                base = os.path.dirname(pattern)
        for source in glob.glob(pattern):
            if os.path.exists(source):
                if os.path.isdir(source):
                    # take all files from the directory
                    results.update(self.collect_pattern(os.path.join(source, "*"), base=base))
                if os.path.isfile(source):
                    result = self.collect_file(source, base=base)
                    # TODO: Duplicate destination check?!
                    results[source] = result
        # squash files
        return results

    def collect_file(self, source, base=None):
        destination = None
        return IGemFile(source, destination=destination, base=base)

    def read_file(self, fn):
        if isinstance(fn, IGemFile):
            fn = fn.full_path
        return super(IGemUploader, self).read_file(fn)

    def upload_files(self):
        results = 0
        # first we upload resources so we can update their destinations
        if not self._skip_resources:
            resources = filter(lambda f: f.is_resource(), self.collected_files.values())
            print("## Uploading {} resources".format(len(resources)))
            for resource in resources:
                results += 1 if self.upload_resource(resource) else 0
        # upload all stylesheets
        if not self._skip_stylesheets:
            resources = filter(lambda f: f.is_stylesheet(), self.collected_files.values())
            print("## Uploading {} stylesheets".format(len(resources)))
            for resource in resources:
                results += 1 if self.upload_stylesheet(resource) else 0
        if not self._skip_javascripts:
            resources = filter(lambda f: f.is_javascript(), self.collected_files.values())
            print("## Uploading {} javascripts".format(len(resources)))
            for resource in resources:
                results += 1 if self.upload_javascript(resource) else 0
        if not self._skip_html:
            # upload all html
            resources = filter(lambda f: f.is_html(), self.collected_files.values())
            print("## Uploading {} html files".format(len(resources)))
            for resource in resources:
                results += 1 if self.upload_html(resource) else 0
        return results

    def upload_file(self, f, content=None):
        """Core function acts as interface between edit and the upload methods

        :type f: IGemFile
        """
        result = False
        if f.is_resource():
            # upload using the upload method
            if f.exists():
                result = self.upload(f.destination, f.full_path)
                url = result.get("url")
                mime = result.get("mime")
                if url is not None:
                    f.url = url
                if mime is not None:
                    f.mime = mime
                result = result['result']
        else:
            if content is None and f.exists():
                content = self.read_file(f.full_path)
            if content is not None:
                result = self.edit(f.destination, content)
                self.get_logger().debug("Uploaded {}: {}".format(f, result))
                f.url = self.prefix_url(f.destination)
        if result:
            self.collected_files.pop(f.full_path)
            self.uploaded_files[f.url] = f
        return result

    def upload_html(self, f):
        """Upload HTML files

        :type f: IGemFile
        """
        result = False
        # remove any .html extension from the file
        if f.destination is None:
            f.destination = f.path
        name = f.destination
        name = name.lstrip("./")
        if name.endswith(".html"):
            name = name.replace(".html", "")
        f.destination = self.prefix_title(name)
        if f.exists():
            # obtain content
            content = self.read_file(f)
            # process content
            content = self.prepare_html(content)
            self.upload_file(f, content)
        return result

    def upload_stylesheet(self, f):
        """Upload a CSS Stylesheet

         :type f: IGemFile
        """
        result = False
        if f.destination is None:
            f.destination = f.path
        name = f.destination
        name = name.lstrip("./")
        if name.endswith(".css"):
            name = name.replace(".css", "")
        f.destination = self.prefix_title(name)
        if f.exists():
            # obtain content
            content = self.read_file(f)
            # process content
            content = self.prepare_stylesheet(content)
            self.upload_file(f, content)
        return result

    def upload_javascript(self, f):
        """Upload a CSS Stylesheet

         :type f: IGemFile
        """
        result = False
        if f.destination is None:
            f.destination = f.path
        name = f.destination
        name = name.lstrip("./")
        if name.endswith(".js"):
            name = name.replace(".js", "")
        f.destination = self.prefix_title(name)
        if f.exists():
            # obtain content
            content = self.read_file(f)
            # process content
            content = self.prepare_javascript(content)
            self.upload_file(f, content)
        return result

    def upload_resource(self, f):
        """Upload resources like Images, PDFs etc."""
        result = False
        if f.destination is None:
            f.destination = f.path
        fp = f.destination
        fp = fp.lstrip("./")
        fd = os.path.dirname(fp)
        fn = os.path.basename(fp)
        if isinstance(self.resource_prefix, str) and self.resource_prefix != "":
            fn = "{}{}".format(self.resource_prefix, fn)
        f.destination = os.path.join(fd, fn)
        if f.exists():
            result = self.upload_file(f)
            self.get_logger().info("Upload attachment {} => {}: {}".format(f.path, f.url, result))
        return result

    def prepare_html(self, html):
        from bs4 import BeautifulSoup
        doc = BeautifulSoup(html, "html.parser")
        # fix all stylesheet imports
        elements = doc.find_all("link", rel="stylesheet")
        for e in elements:
            href = e.get("href")
            if href is not None:
                uri = self.fix_stylesheet_link(href)
                self.get_logger().debug("Changed stylesheet href {} to {}".format(href, uri))
                e["href"] = uri
        elements = doc.find_all("script")
        # fix all javascript imports
        for e in elements:
            src = e.get("src")
            if src is not None:
                uri = self.fix_javascript_source(src)
                self.get_logger().debug("Changed script src {} to {}".format(src, uri))
                e["src"] = uri
        # fix all links
        elements = doc.find_all("a")
        for e in elements:
            href = e.get("href")
            if href is not None:
                uri = self.fix_html_link(href)
                self.get_logger().debug("Changed link href {} to {}".format(href, uri))
                e["href"] = uri
        # fix all image links
        elements = doc.find_all("img")
        for e in elements:
            src = e.get("src")
            if src is not None:
                uri = self.fix_image_link(src)
                self.get_logger().debug("Changed img src {} to {}".format(src, uri))
                e["src"] = uri
        # fix all movie links
        elements = doc.find_all("source")
        for e in elements:
            src = e.get("src")
            if src is not None:
                uri = self.fix_image_link(src)
                self.get_logger().debug("Changed source src {} to {}".format(src, uri))
                e["src"] = uri
        # write to string
        result = doc.prettify()
        return result

    def prepare_stylesheet(self, stylesheet):
        """Inspect a stylesheet on URL's we should change"""
        result = stylesheet
        return result

    def prepare_javascript(self, script):
        """Inspect a JavaScript on URL's we should change"""
        result = script
        return result

    def fix_stylesheet_link(self, href):
        match = self.find_actual_link(href)
        if isinstance(match, IGemFile):
            uri = match.url
        elif isinstance(match, str):
            uri = match
        else:
            uri = href.rsplit(".", 1)[0]
            uri = self.prefix_url(uri)
        if not uri.endswith("?action=raw&ctype=text/css"):
            uri += "?action=raw&ctype=text/css"
        return uri

    def fix_javascript_source(self, src):
        url = src
        # we need to be careful, images can be both internal and external!
        # take url apart
        parts = list(urlparse(src))
        # get base url
        base_url = self.get_base_uri()
        # extract local path
        path = str(parts[2])  # .strip("/")
        # check if this is a local file
        if path != "" and parts[1] in ("", base_url):
            ctype = "?action=raw&ctype=text/javascript"
            # locate whether we uploaded this file before
            match = self.find_actual_link(src)
            if isinstance(match, IGemFile):
                url = match.url
            elif isinstance(match, str):
                url = match
            else:
                url = src.rsplit(".", 1)[0]
                url = self.prefix_url(url)
            if not url.endswith(ctype):
                url += ctype
        return url

    def fix_image_link(self, src):
        url = src
        # we need to be careful, images can be both internal and external!
        # take url apart
        parts = list(urlparse(src))
        # get base url
        base_url = self.get_base_uri()
        # extract local path
        path = str(parts[2])  # .strip("/")
        # check if this is a local file
        if path != "" and parts[1] in ("", base_url):
            ctype = "&ctype=text/plain"
            mime = None
            url = self.prefix_url(url)
            match = self.find_actual_link(src)
            if isinstance(match, IGemFile):
                mime = match.mime
                url = match.url
                if url is None:
                    url = self.prefix_url(match.destination)
            elif isinstance(match, str):
                url = match
            if mime is None:
                mime = os.path.splitext(url)[1]
            if isinstance(mime, str):
                mime = mime.strip(".")
            if mime in IGemFile.IMAGE_EXTENSIONS:
                ctype = "&ctype=image/{}".format(mime)
            # if not url.endswith("?action=raw{}".format(ctype)):
            #     url += "?action=raw{}".format(ctype)
        else:
            url = self.fix_html_link(src)
        return url

    def fix_html_link(self, href):
        url = href
        # we have to be careful, we only want to change the uri not any params or internal links
        parts = list(urlparse(href))
        # get a clean base url
        base_url = self.get_base_uri()
        # extract local path
        path = str(parts[2]) #.strip("/")
        if path != "" and parts[1] == "" and "@" not in href:
            target = ""
            pieces = path.rsplit("#", 1)
            path = pieces[0]
            if len(pieces) > 1:
                target = pieces[-1]
            target = target.strip("/")
            path = path.rsplit(".", 1)[0]
            if path == "/index":
                path = "/"
            # we will set the parts["netloc"] to the right server
            # so we do not worry about that part
            path = self.prefix_title(path)
            # reassemble
            parts[0] = "http"
            parts[1] = base_url
            parts[2] = path + target
            url = urlunparse(parts)
        return url

    def find_actual_link(self, fn):
        """Searches through the uploaded files list to get the actual link of the files

        This can be a link or an source but will always return the actual destination
        """
        return self.match_to_uploaded(fn)

    def match_to_uploaded(self, fn):
        result = None
        fn = fn.lower()

        def is_match(item):
            r = False
            k, v = item
            if not r and isinstance(k, str):
                url = self.prefix_title(fn)
                r = fn.strip("./") == k.strip("./") or url.strip("./") == k.strip("./")
            if not r and isinstance(v, IGemFile):
                matches_names = fn.strip("./") in (v.destination, v.path, v.full_path, v.url)
                matches_paths = False
                try:
                    matches_paths = fn.strip("./") in (
                        v.destination.strip("./"), v.path.strip("./"), v.full_path.strip("./"), v.url.strip("./")
                    )
                except AttributeError:
                    pass
                r = matches_names or matches_paths
            if not r and isinstance(v, str):
                r = fn.strip("./") == v.lower().strip("./")
            return r

        matches = filter(is_match, self.uploaded_files.items())
        if len(matches) > 0:
            self.get_logger().debug("Matched {} to:\n{}".format(fn, [str(m) for m in matches]))
            match = matches[0]
            result = match[0]
        return result

    def read_library(self, fp):
        results = {}
        if os.path.exists(fp):
            with open(fp, "rb") as src:
                for line in src.readlines():
                    k, v = line.strip("\n").split("\t")
                    if None not in (k, v) and "" not in (k, v):
                        results[k] = v
        self.get_logger().info("Read Uploaded Files Libary from {}, found {} files".format(
            fp, len(results)
        ))
        # update collected files
        self._files_uploaded.update(results)
        return results

    def write_library(self, fp, library):
        result = False
        fd = os.path.dirname(os.path.realpath(fp))
        if not self.runs_dry() and os.path.exists(fd):
            with open(fp, "wb") as dest:
                for k, v in library.items():
                    if isinstance(v, IGemFile):
                        dest.write("{}\t{}\n".format(k, v.path))
                    else:
                        dest.write("{}\t{}\n".format(k, v))
            result = True
        self.get_logger().info("Write Uploaded Files Library to {}: {}".format(fp, result))
        return result

    @classmethod
    def create_parser(cls, parser=None):
        parser = super(IGemUploader, cls).create_parser(parser)
        parser.description = "Simple file upload script for the iGEM wiki"
        parser.add_argument(
            '--strip', help="Remove pattern from filename", nargs="?", default=None
        )
        parser.add_argument(
            '--library', '-L', dest="library", help="Location of the library file to record file locations"
        )
        parser.add_argument(
            '--skip-resources', action="store_true", dest="skip_resources",
            help="Do not upload resources (requires library with URL mappings to get fix_html to work)"
        )
        parser.add_argument(
            '--skip-stylesheets', action="store_true", dest="skip_stylesheets",
            help="Do not upload CSS Stylesheets (requires library with URL mappings to get fix_html to work)"
        )
        parser.add_argument(
            '--skip-javascripts', action="store_true", dest="skip_javascripts",
            help="Do not upload JavaScript files (requires library with URL mappings to get fix_html to work)"
        )
        parser.add_argument(
            '--skip-html', action="store_true", dest="skip_html",
            help="Do not upload HTML Files"
        )
        return parser

    def parse_arguments(self, arguments):
        super(IGemUploader, self).parse_arguments(arguments)
        strip_prefix = arguments.get("strip")
        if isinstance(strip_prefix, str):
            self.set_strip(strip_prefix)
        library = arguments.get("library")
        if library is not None:
            self.library = library
        skip_resources = arguments.get("skip_resources")
        if skip_resources is not None:
            self._skip_resources = skip_resources is True
        skip_stylesheets = arguments.get("skip_stylesheets")
        if skip_stylesheets is not None:
            self._skip_stylesheets = skip_stylesheets is True
        skip_javascripts = arguments.get("skip_javascripts")
        if skip_javascripts is not None:
            self._skip_javascripts = skip_javascripts is True
        skip_html = arguments.get("skip_html")
        if skip_html is not None:
            self._skip_html = skip_html is True


if __name__ == "__main__":
    IGemUploader.run()
