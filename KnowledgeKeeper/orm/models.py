from django.db import models

class CiteSeerAuthor( models.Model ):
    name = models.CharField( max_length=255, default='' )
    clusterid = models.IntegerField( default=0 )

    def __unicode__( self ):
        return self.name


class CiteSeerDocument( models.Model ):
    doi       = models.CharField( max_length=50 )
    clusterid = models.IntegerField()
    title     = models.CharField( max_length=400 )
    abstract  = models.TextField()
    year      = models.IntegerField()
    crawldate = models.CharField( max_length=20 )
    url       = models.URLField()
    authors   = models.ManyToManyField( CiteSeerAuthor )
    citings   = models.CharField( max_length=10000 )

    def __unicode__( self ):
        return "%s, %d (%s)" % (self.title, self.year, self.doi)
#        return "DOCUMENT: %s  (%d)" % (self.title, self.year)


class CiteSeerCitation( models.Model ):
    clusterid = models.IntegerField( default=0 )
    document  = models.ForeignKey( CiteSeerDocument )


###############################################################


class KKAuthor( models.Model ):
    name = models.CharField( max_length=255, default='' )
#    refcount = models.IntegerField()

    def __unicode__( self ):
        return self.name


class KKTag( models.Model ):
    tag = models.CharField( max_length=64 )
#    refcount = models.IntegerField()

    def __unicode__( self ):
        return self.tag

class KKDocument( models.Model ):
    authors     = models.ManyToManyField( KKAuthor )
    title       = models.CharField( max_length=511 )
    year        = models.IntegerField()
    note        = models.TextField()
    localFile   = models.CharField( max_length=255 )
    tags        = models.ManyToManyField( KKTag )
    doi         = models.CharField( max_length=50 )
    cites       = models.ForeignKey( 'self', blank=True, null=True )
    read        = models.IntegerField()
    commentFile = models.CharField( max_length=31 )

    def __unicode__( self ):
        return "KKDocument: %s (%d)" % (self.title, self.year)

