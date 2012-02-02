from django.conf import settings
import os, sys

runningDir=os.path.dirname(sys.argv[0])
sys.path.append(os.path.join(runningDir, "KnowledgeKeeper"))
sys.path.append(os.path.join(os.path.join(runningDir, ".."), "KnowledgeKeeper"))

DATABASE_ENGINE="sqlite3"
DATABASE_HOST="localhost"
DATABASE_NAME="knowledgekeeper.sqlite3"
DATABASE_USER="user"
DATABASE_PASSWORD="password"
INSTALLED_APPS = ('orm',)

settings.configure(DATABASE_ENGINE=DATABASE_ENGINE,
                   DATABASE_HOST=DATABASE_HOST,
                   DATABASE_NAME=DATABASE_NAME,
                   DATABASE_USER=DATABASE_USER,
                   DATABASE_PASSWORD=DATABASE_PASSWORD,
                   INSTALLED_APPS=INSTALLED_APPS)

