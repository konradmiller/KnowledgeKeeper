#!/usr/bin/env python

import os, sys
import KnowledgeKeeper

try:
    runningDir=os.path.dirname(sys.argv[0])
    sys.path.append(os.path.join(runningDir, "KnowledgeKeeper"))
    sys.path.append(os.path.join(os.path.join(runningDir, ".."), "KnowledgeKeeper"))
    import forms
except ImportError:
    print "ERROR importing forms"
    raise

KnowledgeKeeper.run()
