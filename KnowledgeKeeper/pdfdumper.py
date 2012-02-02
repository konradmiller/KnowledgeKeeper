from subprocess import Popen, PIPE

def pdfWords( filename, minLength=3 ):
    p = Popen(['pdftotext', filename, '-'], stdout=PIPE)
    allwords = set()
    okChars = "abcdefghijklmnopqrstuvwxyz"

    for word in p.communicate()[0].split():
        word = ''.join([x for x in word if x.lower() in okChars])
        if( len(word) >= minLength ):
            allwords.add(word)
    return ' '.join(allwords)


if __name__ == "__main__":
    import sys
    words = pdfWords( sys.argv[1] )
    print words
