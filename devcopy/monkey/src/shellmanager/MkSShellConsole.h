#ifndef MKSSHELLCONSOLE_H
#define MKSSHELLCONSOLE_H

#include <objects/MonkeyExport.h>
#include <widgets/pConsole.h>

class Q_MONKEY_EXPORT MkSShellConsole : public pConsole
public:
    MkSShellConsole( parent = 0 )
    virtual ~MkSShellConsole()
    
    virtual QSize sizeHint()


#endif # MKSSHELLCONSOLE_H