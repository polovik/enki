"""
detectindent --- Automatic indentation detection
================================================
"""

from mks.core.core import core


class Plugin:
    """Plugin interface
    """
    def __init__(self):
        #autodetect indent, need
        core.workspace().documentOpened.connect(self._onDocumentOpened)
        core.workspace().languageChanged.connect(self._onLanguageChanged)

    def del_(self):
        """Explicitly called destructor
        """
        core.workspace().documentOpened.disconnect(self._onDocumentOpened)
        core.workspace().languageChanged.disconnect(self._onLanguageChanged)

    def moduleConfiguratorClass(self):
        """Module configurator
        """
        return None

    def _onDocumentOpened(self, document):
        """Signal handler. Document had been opened
        """
        self._detectAndApplyIndentation(document)

    def _onLanguageChanged(self, document, old, new):
        """Signal handler. Document language had been changed
        """
        if new == 'Makefile':
            self._detectAndApplyIndentation(document, True)


    def _detectAndApplyIndentation(self, document, isMakefile=False):
        """Delect indentation automatically and apply detected mode
        Handler for signal from the workspace
        """
        
        #TODO improve algorythm sometimes to skip comments
        
        if not core.config()["Editor"]["Indentation"]["AutoDetect"]:
            return

        def _lineIndent(line):
            """Detect indentation for single line.
            Returns whitespaces from the start of the line
            """
            return line[:len(line) - len(line.lstrip())]
        
        def _diffIndents(a, b):
            """Compare two indentations and return its difference or None
            """
            if a == b:
                return None
            elif a.startswith(b):
                return a[len(b):]  # rest of a
            elif b.startswith(a):
                return b[len(a):]  # rest of b
            else:  # indents are totally not equal
                return None
        
        lines = document.lines()
        lastIndent = ''
        popularityTable = {}
        for l in lines:
            currentIndent = _lineIndent(l)
            diff = _diffIndents(currentIndent, lastIndent)
            if diff is not None:
                if diff in popularityTable:
                    popularityTable[diff] += 1
                else:
                    popularityTable[diff] = 1
            lastIndent = currentIndent
        
        if not popularityTable:  # no indents. Empty file?
            return  # give up
        
        sortedIndents = sorted(popularityTable.iteritems(), key = lambda item: item[1], reverse = True)
        theMostPopular = sortedIndents[0]
        secondPopular = sortedIndents[1]
        if len(sortedIndents) >= 2:
            if theMostPopular[1] == secondPopular[1]:  # if equal results - give up
                return
        
        indent, count = theMostPopular
        if count > 2:  # if more than 2 indents
            if indent == '\t':
                document.setIndentUseTabs(True)
            elif all([char == ' ' for char in indent]):  # if all spaces
                document.setIndentUseTabs(False)
                document.setIndentWidth(len(indent))
        # Else - give up. If can't detect, leave as is
