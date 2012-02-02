# django orm models
from orm.models import *

def addToDB(title, authors, tags, year, file, commentFileName, doi):
    title, authors, tags, file, commentFileName, doi = map(unicode, (title, authors, tags, file, commentFileName, doi))

    # create authors
    newAuthors = []
    for a in authors.split(','):
        a = a.strip()
        newAuthor, created = KKAuthor.objects.get_or_create(name = a)
        # reference counter
        if created:
            newAuthor.save()
        newAuthors.append(newAuthor)

    # create tags
    newTags = []
    for t in tags.split(','):
        t = t.strip()
        newTag, created = KKTag.objects.get_or_create(tag = t)
        # reference counter
        if created:
            newTag.save()
        newTags.append( newTag )

    # create document
    newDocument = KKDocument(
        title     = title,
        localFile = file,
        year      = year,
        doi       = doi,
        read      = 0,
        commentFile = commentFileName
    )
    newDocument.save()

    for a in newAuthors:
        newDocument.authors.add( a )

    for t in newTags:
        newDocument.tags.add( t )

    newDocument.save()
