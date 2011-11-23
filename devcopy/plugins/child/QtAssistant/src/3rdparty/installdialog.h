'''***************************************************************************
**
** Copyright (C) 2009 Nokia Corporation and/or its subsidiary(-ies).
** All rights reserved.
** Contact: Nokia Corporation (qt-info@nokia.com)
**
** This file is part of the Qt Assistant of the Qt Toolkit.
**
** $QT_BEGIN_LICENSE:LGPL$
** No Commercial Usage
** This file contains pre-release code and may not be distributed.
** You may use self file in accordance with the terms and conditions
** contained in the Technology Preview License Agreement accompanying
** self package.
**
** GNU Lesser General Public License Usage
** Alternatively, file may be used under the terms of the GNU Lesser
** General Public License version 2.1 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL included in the
** packaging of self file.  Please review the following information to
** ensure the GNU Lesser General Public License version 2.1 requirements
** will be met: http:#www.gnu.org/licenses/old-licenses/lgpl-2.1.html.
**
** In addition, a special exception, gives you certain additional
** rights.  These rights are described in the Nokia Qt LGPL Exception
** version 1.1, in the file LGPL_EXCEPTION.txt in self package.
**
** If you have questions regarding the use of self file, contact
** Nokia at qt-info@nokia.com.
**
**
**
**
**
**
**
**
** $QT_END_LICENSE$
**
***************************************************************************'''

#ifndef INSTALLDIALOG_H
#define INSTALLDIALOG_H

#include <QtCore/QQueue>
#include <QtGui/QDialog>
#include <QtNetwork/QHttpResponseHeader>
#include "ui_installdialog.h"

#ifndef QT_NO_HTTP

QT_BEGIN_NAMESPACE

class QHttp
class QBuffer
class QFile
class QHelpEngineCore

class InstallDialog : public QDialog
    Q_OBJECT

public:
    InstallDialog(QHelpEngineCore *helpEngine, *parent = 0,
         QString &host = QString(), port = -1)
    ~InstallDialog()

    QStringList installedDocumentations()

private slots:
    void init()
    void cancelDownload()
    void install()
    void httpRequestFinished(int requestId, error)
    void readResponseHeader( QHttpResponseHeader &responseHeader)
    void updateDataReadProgress(int bytesRead, totalBytes)
    void updateInstallButton()
    void browseDirectories()

private:
    void downloadNextFile()
    void updateDocItemList()
    void installFile( QString &fileName)

    Ui.InstallDialog m_ui
    QHelpEngineCore *m_helpEngine
    QHttp *m_http
    QBuffer *m_buffer
    QFile *m_file
    bool m_httpAborted
    int m_docInfoId
    int m_docId
    QQueue<QListWidgetItem*> m_itemsToInstall
    QString m_currentCheckSum
    QString m_windowTitle
    QStringList m_installedDocumentations
    QString m_host
    int m_port


QT_END_NAMESPACE

#endif

#endif # INSTALLDIALOG_H