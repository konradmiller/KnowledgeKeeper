from pdfdumper import pdfWords

def addToIndex( index, text, file ):
    writer = index.writer()
    if file != "":
        writer.add_document(content=unicode(" ".join([text, pdfWords(file)])), path=unicode(file))
    else:
        writer.add_document(content=unicode(text), path="")
    writer.commit()


def dropIndex( index ):
    print "dropIndex() not implemented yet"
    pass
