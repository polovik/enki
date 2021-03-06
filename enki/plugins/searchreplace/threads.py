"""
threads --- Search and Replace threads
======================================

This threads are used for asynchronous search and replace
"""

import os.path
import re
import time
import fnmatch

from PyQt4.QtCore import pyqtSignal, \
                         QThread

from enki.core.core import core
import searchresultsmodel
import substitutions

def _isBinary(fileObject):
    """Expects, that file position is 0, when exits, file position is 0
    """
    binary = '\0' in fileObject.read( 4096 )
    fileObject.seek(0)
    return binary


class StopableThread(QThread):
    """Stoppable thread class. Used as base for search and replace thread.
    """
    _exit = False
    
    def __init__(self):
        QThread.__init__(self)
    
    def __del__(self):
        self.stop()

    def stop(self):
        """Stop thread synchronously
        """
        self._exit = True
        self.wait()
    
    def start(self):
        """Ensure thread is stopped, and start it
        """
        self.stop()
        self._exit = False
        QThread.start(self)

class SearchThread(StopableThread):
    """Thread builds list of files for search and than searches in this files.append
    """
    RESULTS_EMIT_TIMEOUT = 1.0

    resultsAvailable = pyqtSignal(list)  # list of searchresultsmodel.FileResults
    progressChanged = pyqtSignal(int, int)  # int value, int total

    def search(self, regExp, mask, inOpenedFiles, searchPath):
        """Start search process.
        context stores search text, directory and other parameters
        """
        self.stop()
        
        self._regExp = regExp
        self._mask = mask
        self._inOpenedFiles = inOpenedFiles
        self._searchPath = searchPath
        
        self._openedFiles = {}
        for document in core.workspace().documents():
            if document.filePath() is not None:
                self._openedFiles[document.filePath()] = document.text()

        self.start()

    def _getFiles(self, path, maskRegExp, filterRegExp):
        """Get recursive list of files from directory.
        maskRegExp is regExp object for check if file matches mask
        """
        retFiles = []
        for root, dirs, files in os.walk(os.path.abspath(path)):  # pylint: disable=W0612
            if root.startswith('.') or (os.path.sep + '.') in root:
                continue
            for fileName in files:
                if fileName.startswith('.'):
                    continue
                if maskRegExp and not maskRegExp.match(fileName):
                    continue
                
                if filterRegExp.match(fileName):
                    continue
                
                fullPath = os.path.join(root, fileName)
                if not os.path.isfile(fullPath):
                    continue
                retFiles.append(root + os.path.sep + fileName)

            if self._exit :
                break

        return retFiles
    
    def _getFilesToScan(self):
        """Get list of files for search.
        """
        files = set()

        if self._mask:
            regExPatterns = [fnmatch.translate(pat) for pat in self._mask]
            maskRegExpPattern = '(' + ')|('.join(regExPatterns) + ')'
            maskRegExp = re.compile(maskRegExpPattern)
        else:
            maskRegExp = None

        if self._inOpenedFiles:
            files = self._openedFiles.keys()
            if maskRegExp:
                basenames = [os.path.basename(f) for f in files]
                files = [f for f in basenames if maskRegExp.match(f)]
            return files
        else:
            path = self._searchPath
            return self._getFiles(path, maskRegExp, core.fileFilter().regExp())

    def _fileContent(self, fileName):
        """Read text from file
        """
        if fileName in self._openedFiles:
            return self._openedFiles[ fileName ]

        try:
            with open(fileName) as openedFile:
                if _isBinary(openedFile):
                    return ''
                return unicode(openedFile.read(), 'utf8', errors = 'ignore')
        except IOError as ex:
            print ex
            return ''

    def run(self):
        """Start point of the code, running in thread.
        Build list of files for search, than do search
        """
        startTime = time.clock()
        self.progressChanged.emit( -1, 0 )

        files = sorted(self._getFilesToScan())

        if  self._exit :
            return
        
        self.progressChanged.emit( 0, len(files))
        
        # Prepare data for search process        
        lastResultsEmitTime = time.clock()
        notEmittedFileResults = []
        # Search for all files
        for fileIndex, fileName in enumerate(files):
            results = self._searchInFile(fileName)
            if  results:
                newFileRes = searchresultsmodel.FileResults(self._searchPath,
                                                            fileName,
                                                            results)
                notEmittedFileResults.append(newFileRes)

            if notEmittedFileResults and \
               (time.clock() - lastResultsEmitTime) > self.RESULTS_EMIT_TIMEOUT:
                self.progressChanged.emit( fileIndex, len(files))
                self.resultsAvailable.emit(notEmittedFileResults)
                notEmittedFileResults = []
                lastResultsEmitTime = time.clock()

            if  self._exit :
                self.progressChanged.emit( fileIndex, len(files))
                break
        
        if notEmittedFileResults:
            self.resultsAvailable.emit(notEmittedFileResults)

    def _searchInFile(self, fileName):
        """Search in the file and return searchresultsmodel.Result s
        """
        lastPos = 0
        eolCount = 0
        results = []
        eol = "\n"
        
        content = self._fileContent( fileName )
        
        # Process result for all occurrences
        for match in self._regExp.finditer(content):
            start = match.start()
            
            eolStart = content.rfind( eol, 0, start)
            eolEnd = content.find( eol, start + len(match.group(0)))
            eolCount += content[lastPos:start].count( eol )
            lastPos = start
            
            wholeLine = content[eolStart+1 : eolEnd]
            column = start - eolStart
            if eolStart != 0:
                column -= 1
            
            result = searchresultsmodel.Result( fileName = fileName, \
                             wholeLine = wholeLine, \
                             line = eolCount, \
                             column = column, \
                             match=match)
            results.append(result)

            if self._exit:
                break
        return results

class ReplaceThread(StopableThread):
    """Thread does replacements in the directory according to checked items
    
    Replacements in opened documents are done by GUI thread, in other - by new thread
    """
    resultsHandled = pyqtSignal(unicode, list)
    finalStatus = pyqtSignal(unicode)
    error = pyqtSignal(unicode)

    def replace(self, results, replaceText):
        """Run replace process
        """
        self.stop()
        
        self._replaceText = replaceText
        self._totalCount = sum([len(v) for v in results.itervalues()])
        
        # do replacements in opened files, prepare for replacing in not opened
        self._results = {}
        for filePath, matches in results.iteritems():
            foundDocument = core.workspace().findDocumentForPath(filePath)
            if foundDocument is not None:
                self._replaceInOpenedDocument(foundDocument, matches)
                self.resultsHandled.emit( filePath, matches)
            else:
                self._results[filePath] = matches
        
        self.start()

    def _replaceInOpenedDocument(self, document, matches):
        """Do replacements in opened document
        """
        oldText = document.text()
        newText = self._doReplacements(document.text(), matches)
        document.replace(newText, startAbsPos=0, endAbsPos=len(oldText))

    def _saveContent(self, fileName, content):
        """Write text to the file
        """
        try:
            content = content.encode('utf8')
        except UnicodeEncodeError as ex:
            pattern = self.tr("Failed to encode file to utf8: %s")
            text = unicode(str(ex), 'utf8')
            self.error.emit(pattern % text)
            return
        
        try:
            with open(fileName, 'w') as openFile:
                openFile.write(content)
        except IOError as ex:
            pattern = self.tr("Error while saving replaced content: %s")
            text = unicode(str(ex), 'utf8')
            self.error.emit(pattern % text)

    def _fileContent(self, fileName):
        """Read file
        """
        try:
            with open(fileName) as openFile:
                content = openFile.read()
        except IOError as ex:
            self.error.emit( self.tr( "Error opening file: %s" % str(ex) ) )
            return ''
        
        try:
            return unicode(content, 'utf8')
        except UnicodeDecodeError as ex:
            self.error.emit(self.tr( "File %s not read: unicode error '%s'. File may be corrupted" % \
                            (fileName, str(ex) ) ))
            return None

    def run(self):
        """Start point of the code, running i thread
        Does thread job
        """
        startTime = time.clock()
        
        for fileName in self._results.keys():
            content = self._fileContent(fileName)
            if content is None:  # if failed to read file
                continue
            
            matches = self._results[ fileName ]
            
            content = self._doReplacements(content, matches)
            
            self._saveContent(fileName, content)
            
            self.resultsHandled.emit( fileName, matches)

            if  self._exit :
                break

        self.finalStatus.emit("%d replacements in %d second(s)" % \
                              (self._totalCount,
                               time.clock() - startTime))

    def _doReplacements(self, content, matches):
        """Do replacements for one file
        """
        for result in matches[::-1]:  # count from end to begin because we are replacing by offset in content
            replaceTextWithMatches = substitutions.makeSubstitutions(self._replaceText,
                                                                     result.match)
            content = content[:result.match.start()] + replaceTextWithMatches + content[result.match.end():]
        
        return content