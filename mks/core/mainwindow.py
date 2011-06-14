"""
mainwindow --- Main window of the UI. Fills main menu.
======================================================


Module contains :class:`mks.core.mainwindow.MainWindow` implementation
"""

from PyQt4.QtCore import pyqtSignal, QModelIndex, QSize, Qt
from PyQt4.QtGui import qApp, QIcon, QSizePolicy, QVBoxLayout, QWidget

from PyQt4.fresh import pDockWidget, pMainWindow, pActionsModel

from mks.core.core import core
import mks.core.workspace

class MainWindow(pMainWindow):
    """
    Main UI window
    
    Class creates window elements, fills main menu with items.
    
    If you need to access to some existing menu items - check action path 
    in the class constructor, than use next code: ::
        
        self._actionModel.action( "mFile/aOpen" ).setEnabled(True)
        self._actionModel.action( "mFile/aOpen" ).triggered.connect(self.myCoolMethod)
    
    MainWindow instance is accessible as: ::
    
        from mks.core.core import core
        core.mainwindow()
    
    Created by monkeycore
    """
    
    """TODO  urlsDropped = pyqtSignal()
    urlsDropped = pyqtSignal()
    """

    hideAllWindows = pyqtSignal()
    """
    hideAllWindows()
    
    **Signal** emitted, when user toggled "Hide all" .
    Dock widgets are closed automatically, but other widgets, i.e. search widget, must catch this signal and close
    semself.
    """
    
    def __init__(self):
        pMainWindow.__init__(self)
        self.setUnifiedTitleAndToolBarOnMac( True )
        self.setIconSize( QSize( 16, 16 ) )
        self.setAcceptDrops( True )
        
        # Set corner settings for dock widgets
        self.setCorner( Qt.TopLeftCorner, Qt.LeftDockWidgetArea )
        self.setCorner( Qt.TopRightCorner, Qt.RightDockWidgetArea )
        self.setCorner( Qt.BottomLeftCorner, Qt.LeftDockWidgetArea )
        self.setCorner( Qt.BottomRightCorner, Qt.RightDockWidgetArea )
        
        self.setWindowTitle(self.defaultTitle())  # overwriten by workspace when file or it's modified state changes
        self.setWindowIcon( QIcon(':/mksicons/monkey2.png') )

        self._initMenuBar()
        
        # Default exclusive settings for the tool bars
        self.dockToolBar( Qt.LeftToolBarArea ).setExclusive(False)
        self.dockToolBar( Qt.RightToolBarArea ).setExclusive(False)
        
        # Move docks tool bar to statusbar
        modernDocksToolBar = self.dockToolBarManager().modernToolBar()
        self.removeToolBar(modernDocksToolBar)
        modernDocksToolBar.setOrientation(Qt.Horizontal)
        modernDocksToolBar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        modernDocksToolBar.setIconSize(QSize(16, 16))
        self.statusBar().addPermanentWidget(modernDocksToolBar)
        # create central layout
        widget = QWidget(self)
        self._centralLayout = QVBoxLayout(widget)
        self._centralLayout.setMargin(0)
        self.setCentralWidget(widget)
    
    def __del__(self):
        for act in self._createdActions:
            self._actionModel.removeAction(act)
        for menuPath in self._createdMenuPathes:
            self._actionModel.removeMenu(menuPath)
        
        self.menuBar().setModel( None )
        self.settings().sync()  # write window and docs geometry

    def _initMenuBar(self):
        """Fill menu bar with items. The majority of items are not connected to the slots,
        Connections made by module, which implements menu item functionality, but, all items are in one place,
        because it's easier to create clear menu layout
        """
        # create menubar menus and actions
        self._actionModel = pActionsModel(self)
        self.menuBar().setModel(self._actionModel)

        """TODO restore or delete old actions
        mb.action( "aNew", tr( "&New..." ), QIcon(":/mksicons/new.png" ),"Ctrl+N", tr( "Create a new file" ) )
        mb.menu( "mRecents", tr( "&Recents" ), QIcon(":/mksicons/recents.png" ) )
        mb.action( "mRecents/aClear", tr( "&Clear" ), QIcon(":/mksicons/clear.png" ), '', tr( "Clear the recents files list" ) )
        mb.action( "mRecents/aSeparator1" )
        mb.action( "aSeparator1" )
        mb.menu( "mSession", tr( "Session" ), QIcon(":/mksicons/session.png" ) )
        mb.action( "mSession/aSave", tr( "Save" ), QIcon(":/mksicons/save.png" ), '', tr( "Save the current session files list" ) )
        mb.action( "mSession/aRestore", tr( "Restore" ), QIcon(":/mksicons/restore.png" ), '', tr( "Restore the current session files list" ) )
        mb.action( "aSeparator2" )
        mb.action( "mClose/aAll", tr( "Close &All" ), QIcon(":/mksicons/closeall.png" ), '', tr( "Close all files" ) ).setEnabled( False )
        mb.action( "aSaveAsBackup", tr( "Save As &Backup" ), QIcon(":/mksicons/backup.png" ), '', tr( "Save a backup of the current file" ) ).setEnabled( False )
        mb.action( "aSeparator4" )
        mb.action( "aQuickPrint", tr( "Quic&k Print" ), QIcon(":/mksicons/quickprint.png" ), '', tr( "Quick print the current file" ) ).setEnabled( False )
        mb.action( "aPrint", tr( "&Print..." ), QIcon(":/mksicons/print.png" ), "Ctrl+P", tr( "Print the current file" ) ).setEnabled( False )
        mb.action( "aSeparator5" )
        mb.action( "aSettings", tr( "Settings..." ), QIcon( ":/mksicons/settings.png" ), "", tr( "Edit the application settings" ) )
        mb.action( "aTranslations", tr( "Translations..." ), QIcon( ":/mksicons/translations.png" ), "Ctrl+T", tr( "Change the application translations files" ) )
        mb.action( "aSeparator1" )
        mb.action( "aSeparator3" )
        mb.menu( "mAllCommands", tr( "&All Commands" ), QIcon( ":/mksicons/commands.png" ) )
        
        mb.action( "aSeparator5" )
        mb.action( "aExpandAbbreviation", tr( "Expand Abbreviation" ), QIcon( ":/mksicons/abbreviation.png" ), "Ctrl+E", tr( "Expand Abbreviation" ) ).setEnabled( False )
        mb.action( "aPrepareAPIs", tr( "Prepare APIs" ), QIcon( ":/mksicons/prepareapis.png" ), "Ctrl+Alt+P", tr( "Prepare the APIs files for auto completion / calltips" ) )
        mb.menu( "mStyle", tr( "&Style" ), QIcon( ":/mksicons/style.png" ) )
        mb.menu( "mProject", tr( "Project" ) )
        mb.beginGroup( "mProject" )
        
        mb.addAction( '', core.projectsManager().action( XUPProjectManager.atNew ) )
        mb.addAction( '', core.projectsManager().action( XUPProjectManager.atOpen ) )
        mb.action( "aSeparator1" )
        mb.addAction( '', core.projectsManager().action( XUPProjectManager.atClose ) )
        mb.addAction( '', core.projectsManager().action( XUPProjectManager.atCloseAll ) )
        mb.action( "aSeparator2" )
        mb.addAction( '', core.projectsManager().action( XUPProjectManager.atEdit ) )
        mb.action( "aSeparator3" )
        mb.addAction( '', core.projectsManager().action( XUPProjectManager.atAddFiles ) )
        mb.addAction( '', core.projectsManager().action( XUPProjectManager.atRemoveFiles ) )
        mb.action( "aSeparator4" )
        
        mb.menu( "mRecents", tr( "&Recents" ), QIcon( ":/mksicons/recents.png" ) )
        mb.action( "mRecents/aClear", tr( "&Clear" ), QIcon( ":/mksicons/clear.png" ), '', tr( "Clear the recents projects list" ) )
        mb.action( "mRecents/aSeparator1" )
        mb.endGroup()
        
        mb.menu( "mBuilder", tr( "Build" ) ).menuAction().setEnabled( False )
        mb.menu( "mBuilder" ).menuAction().setVisible( False )
        
        mb.beginGroup( "mBuilder" )
        mb.menu( "mBuild", tr( "&Build" ), QIcon( ":/mksicons/build.png" ) )
        mb.menu( "mRebuild", tr( "&Rebuild" ), QIcon( ":/mksicons/rebuild.png" ) )
        mb.menu( "mClean", tr( "&Clean" ), QIcon( ":/mksicons/clean.png" ) )
        mb.menu( "mExecute", tr( "&Execute" ), QIcon( ":/mksicons/execute.png" ) )
        mb.menu( "mUserCommands", tr( "&User Commands" ), QIcon( ":/mksicons/misc.png" ) )
        mb.action( "aSeparator1" )
        mb.endGroup()
        
        mb.menu( "mDebugger", tr( "Debugger" ) ).menuAction().setEnabled( False )
        mb.menu( "mDebugger" ).menuAction().setVisible( False )
        mb.menu( "mInterpreter", tr( "Interpreter" ) ).menuAction().setEnabled( False )
        mb.menu( "mInterpreter" ).menuAction().setVisible( False )
        mb.menu( "mPlugins", tr( "Plugins" ) )
        
        mb.beginGroup( "mPlugins" )
        mb.action( "aSeparator1" )
        mb.endGroup()
        
        mb.menu( "mWindow", tr( "Window" ) )

        mb.beginGroup( "mWindow" )
        mb.action( "aCascase", tr( "&Cascade" ), QIcon( "" ), '', tr( "Cascade" ) )
        mb.action( "aTile", tr( "&Tile" ), QIcon( "" ), '', tr( "Tile" ) )
        mb.action( "aMinimize", tr( "&Minimize" ), QIcon( "" ), '', tr( "Minimize" ) )
        mb.action( "aRestore", tr( "&Restore" ), QIcon( "" ), '', tr( "Restore normal size" ) )
        mb.endGroup()
        
        mb.action( "aAbout", tr( "&About..." ), QIcon( ":/mksicons/monkey2.png" ), '', tr( "About application..." ) )
        # create action for styles
        agStyles = pStylesActionGroup( tr( "Use %1 style" ), mb.menu( "mNavigation/mStyle" ) )
        agStyles.setCurrentStyle( core.settings().value( "MainWindow/Style" ).toString() )
        mb.menu( "mNavigation/mStyle" ).addActions( agStyles.actions() )
        
        # create plugins actions
        core.pluginsManager().menuHandler().setMenu( mb.menu( "mPlugins" ) )        
        """
        
        self._createdMenuPathes = []
        self._createdActions = []
        
        def menu(path, name, icon):
            """Subfunction for create a menu in the main menu"""
            menuObject = self._actionModel.addMenu(path, name)
            if icon:
                menuObject.setIcon(QIcon(':/mksicons/' + icon))
            self._createdMenuPathes.append(path)
            
        def action(path, name, icon, shortcut, tooltip, enabled):
            """Subfunction for create an action in the main menu"""
            if icon:  # has icon
                actObject = self._actionModel.addAction(path, name, QIcon(':/mksicons/' + icon))
            else:
                actObject = self._actionModel.addAction(path, name)
            if shortcut:
                actObject.setShortcut(shortcut)
            actObject.setStatusTip(tooltip)
            actObject.setEnabled(enabled)
            self._createdActions.append(actObject)
        
        def seperator(menu):
            """Subfunction for insert separator to the menu"""
            self._actionModel.action(menu).menu().addSeparator()
        
        # Menu or action path                   Name                                Icon            Shortcut        Hint                                        Action enabled
        tr = self.tr
        menu  ("mFile",                               tr("File"                   ), ""            )
        action("mFile/aOpen",                         tr( "&Open..."              ), "open.png",     "Ctrl+O" ,      tr( "Open a file"            ), True )
        menu  ("mFile/mSave",                         tr("&Save"                  ), "save.png"    ),
        action("mFile/mSave/aCurrent",                tr( "&Save"                 ), "save.png" ,    "Ctrl+S" ,      tr( "Save the current file"  ), False)
        action("mFile/mSave/aAll",                    tr( "Save &All"             ), "saveall.png",  'Shift+Ctrl+S', tr( "Save all files"         ), False)
        menu  ("mFile/mReload",                       tr("&Reload"                ), "reload.png"    ),
        action( "mFile/mReload/aCurrent",             tr( "Reload"                ), "reload.png"  , 'F5',           tr( "Reload the current file"), False)
        action( "mFile/mReload/aAll",                 tr( "Reload All"            ), "reload.png"  , 'Alt+Shift+F5', tr( "Reload all files"), True)
        action( "mFile/aNew",                         tr( "&New file..."          ), "new.png",      'Ctrl+N',       tr( "New file" ), True )
        menu  ("mFile/mClose",                        tr( "&Close"                ), "close.png"   ),
        action("mFile/mClose/aCurrent",               tr( "&Close"                ), "close.png",    "Ctrl+W",       tr( "Close the current file" ), False)
        seperator("mFile")
        action("mFile/aQuit",                         tr( "&Quit"                 ), "quit.png",     "Ctrl+Q",       tr( "Quit the application"   ), True )
        
        menu ("mNavigation",                          tr("Navigation"             ), ""            ) 
        menu ("mNavigation/mSearchReplace",           tr( "&Search && Replace"    ), "search-replace-directory.png")
        menu ("mNavigation/mBookmarks",               tr( "&Bookmarks"            ), "bookmark.png")
        menu ("mNavigation/mZoom",                    tr( "&Zoom"                 ), "search.png")

        action("mNavigation/aNext",                   tr( "&Next file"            ), "next.png",     "Alt+Right",    tr( "Next file"    ), False)
        action("mNavigation/aPrevious",               tr( "&Previous file"        ), "previous.png", "Alt+Left",     tr( "Previous file"), False)
        action("mNavigation/aFocusCurrentDocument",   tr( "Focus to editor"       ), "text.png",     "Ctrl+Return",  tr( "Focus current document" ), False)
        action("mNavigation/aGoto",                   tr( "Go go line..."         ), "goto.png",     "Ctrl+G",  tr( "Go to line..." ), False)

        menu  ("mEdit",                               tr( "Edit"                  ), ""            )

        menu  ("mSettings",                           tr( "Settings"              ), ""            )
        action("mSettings/aConfigFile",               tr( "Edit config file" ),   "",             "Ctrl+Alt+S", tr( "Edit config file"    ), True)

        menu  ("mDocks",                              tr( "Docks"                 ), ""            )
        action("mDocks/aHideAll",                     tr( "Hide all"              ),   "",            "Ctrl+ Esc", tr( "Hide all"    ), True)

        menu  ("mHelp",                               tr( "Help"                  ), ""            )
        action("mHelp/aAboutQt",                      tr( "About &Qt..." ),          "qt.png",       "",             tr( "About Qt..."            ), True )
        
        self._actionModel.action( "mFile/aQuit" ).triggered.connect(self.close)
        self._actionModel.action( "mHelp/aAboutQt" ).triggered.connect(qApp.aboutQt)
        # docks
        self._actionModel.action( "mDocks" ).menu().aboutToShow.connect(self._menu_Docks_aboutToShow)
        self._actionModel.action( "mDocks/aHideAll" ).triggered.connect(self._onHideAllWindows)

        """TODO restore or delete old connections
        self._actionModel.action( "mFile/aNew" ).triggered.connect(core.workspace().fileNew_triggered)
        core.recentsManager().openFileRequested.connect(core.fileManager().openFile)
        self._actionModel.action( "mFile/mSession/aSave" ).triggered.connect(core.workspace().fileSessionSave_triggered)
        self._actionModel.action( "mFile/mSession/aRestore" ).triggered.connect(core.workspace().fileSessionRestore_triggered)
        self._actionModel.action( "mFile/mClose/aAll" ).triggered.connect(core.workspace().fileCloseAll_triggered)
        self._actionModel.action( "mFile/aSaveAsBackup" ).triggered.connect(core.workspace().fileSaveAsBackup_triggered)
        self._actionModel.action( "mFile/aQuickPrint" ).triggered.connect(core.workspace().fileQuickPrint_triggered)
        self._actionModel.action( "mFile/aPrint" ).triggered.connect(core.workspace().filePrint_triggered)
        # edit connection
        self._actionModel.action( "mEdit/aSettings" ).triggered.connect(core.workspace().editSettings_triggered)
        self._actionModel.action( "mEdit/aTranslations" ).triggered.connect(core.workspace().editTranslations_triggered)
        self._actionModel.action( "mEdit/aExpandAbbreviation" ).triggered.connect(core.workspace().editExpandAbbreviation_triggered)
        self._actionModel.action( "mEdit/aPrepareAPIs" ).triggered.connect(core.workspace().editPrepareAPIs_triggered)
        # view connection
        agStyles.styleSelected.connect(self.changeStyle)

        # project connection
        core.recentsManager().openProjectRequested.connect(core.projectsManager().openProject)
        core.projectsManager().fileDoubleClicked.connect(core.workspace().openFile)
        # builder debugger interpreter menu
        self._actionModel.menu( "mBuilder" ).aboutToShow.connect(self.menu_CustomAction_aboutToShow)
        self._actionModel.menu( "mDebugger" ).aboutToShow.connect(self.menu_CustomAction_aboutToShow)
        self._actionModel.menu( "mInterpreter" ).aboutToShow.connect(self.menu_CustomAction_aboutToShow)
        # plugins menu
        # window menu
        self._actionModel.action( "mWindow/aTile" ).triggered.connect(core.workspace().tile)
        self._actionModel.action( "mWindow/aCascase" ).triggered.connect(core.workspace().cascade)
        self._actionModel.action( "mWindow/aMinimize" ).triggered.connect(core.workspace().minimize)
        self._actionModel.action( "mWindow/aRestore" ).triggered.connect(core.workspace().restore)
        # help menu
        self._actionModel.action( "mHelp/aAbout" ).triggered.connect(core.workspace().helpAboutApplication_triggered)
        """
    
    def setWorkspace(self, workspace):
        """Set central widget of the main window.
        Normally called only by core when initializing system
        """
        self._centralLayout.addWidget(workspace)
        self.setFocusProxy(workspace)
    
    def defaultTitle(self):
        """Default title. Contains MkS name and version
        """
        return "%s v.%s" % (mks.core.defines.PACKAGE_NAME, mks.core.defines.PACKAGE_VERSION)
    
    def _menu_Docks_aboutToShow(self):
        """Fill docs menu with currently existing docs
        """
        # get menu
        menu = self._actionModel.action( "mDocks" ).menu()
        
        # add actions
        for dock in self.findChildren(pDockWidget):
            action = dock.showAction()
            menu.addAction( action )
            self._actionModel.addAction( "mDocks", action )
    
    def centralLayout(self):
        """Layout of the central widget. Contains Workspace and search widget
        """
        return self._centralLayout
    
    def closeEvent( self, event ):
        """NOT A PUBLIC API
        Close event handler.
        Shows save files dialog. Cancels close, if dialog was rejecteds
        
        """
        
        """TODO save session on close
        # save session if needed
        if  mks.monkeystudio.saveSessionOnClose() :
            core.workspace().fileSessionSave_triggered()
        """
        # request close all documents
        if not core.workspace().closeAllDocuments():
            event.ignore()
            return
        return super(MainWindow, self).closeEvent(event)
    
    def _onHideAllWindows(self):
        """Close all visible windows for get as much space on the screen, as possible
        """
        self.hideAllWindows.emit()
        for dock in self.findChildren(pDockWidget):
            dock.hide()

    
"""TODO restore or delete old code
    def dragEnterEvent( self, event ):
        # if correct mime and same tabbar
        if  event.mimeData().hasUrls() :
            # accept drag
            event.acceptProposedAction()
        
        # default event
        pMainWindow.dragEnterEvent( self, event )
    
    def dropEvent( self, event ):
        if  event.mimeData().hasUrls() :
            self.urlsDropped.emit( event.mimeData().urls () )
        
        # default event
        pMainWindow.dropEvent( self, event )
    
    def createPopupMenu(self):
        # create default menu
        menu = QMenu( self );
        # add exclusive action of pDockToolBar
        tbs = self.findChildren(pDockToolBar)
        
        for tb in tbs:
            if  tb.parent() != self :
                continue
            
            menu.addAction( tb.toggleExclusiveAction() )
        
        return menu

def updateMenuVisibility( self, menu ):
        menuAction = menu.menuAction()
        
        menuVisible = False

        for action in menu.actions():
            if  action.isSeparator() :
                continue
            
            subMenu = action.menu()

            if  subMenu :
                if  self.updateMenuVisibility( subMenu ) :
                    menuVisible = True
            else:
                menuVisible = True
        
        menuAction.setVisible( menuVisible )
        menuAction.setEnabled( menuVisible )
        
        return menuVisible
    
    def menu_CustomAction_aboutToShow(self):
        menus = []

        if  sender() :
            menus.append(sender())
        else:
            menus.append[self._actionModel.menu( "mBuilder" )]
            menus.append[self._actionModel.menu( "mDebugger")]
            menus.append[self._actionModel.menu( "mInterpreter")]

        for m in menus:
            self.updateMenuVisibility( m )
    
    def changeStyle( style ):
        qApp.setStyle( style )
        qApp.setPalette( qApp.style().standardPalette() )
        self.settings().setValue( "MainWindow/Style", style )
"""