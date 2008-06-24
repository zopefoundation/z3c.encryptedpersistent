##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import cPickle
import persistent
import zope.interface

import interfaces

class EncryptedPersistent(persistent.Persistent):
    zope.interface.implements(interfaces.IEncryptedPersistent)

    # See interfaces.IEncryptedPersistent
    __key__ = None

    def __getstate__(self):
        # 1. Check that the key is really in the client.
        encryption = zope.component.getUtility(interfaces.IEncryption)
        if self.__key__ not in encryption:
            raise interfaces.InvalidKey(self.__key__)
        # 2. Get the state of the object using the Persistent implementation.
        state = super(EncryptedPersistent, self).__getstate__()
        # 3. Convert the state to a string.
        stateStr = cPickle.dumps(state)
        # 4. Encrypt the state string and return it as the state.
        return (self.__key__, encryption[self.__key__].encrypt(stateStr))

    def __setstate__(self, (key, encryptedState)):
        # 1. Set the key on the object first:
        self.__key__ = key
        # 2. Decrypt the state string.
        encryption = zope.component.getUtility(interfaces.IEncryption)
        stateStr = encryption[self.__key__].decrypt(encryptedState)
        # 3. Convert the state string to the state
        state = cPickle.loads(stateStr)
        # 4. Set the state of the object using the Persistent implementation.
        super(EncryptedPersistent, self).__setstate__(state)
