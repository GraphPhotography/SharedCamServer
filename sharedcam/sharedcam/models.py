from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Tag(models.Model):
    text = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return "Tag #%s" % (self.text)

class HashPhoto(models.Model):
    # core data
    hexdigest = models.CharField(max_length=32, primary_key=True)
    photo = models.ImageField(upload_to='photostore')

    # metadata
    date_uploaded = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=200, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    metadata = models.TextField(null=True, blank=True)
    hidden = models.BooleanField(default=True)

    # tags
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return "%s [%s] (%s)" % (self.photo, self.hexdigest, self.date_uploaded)

    def thumbnail(self):
        path = str(self.photo).replace(".jpg", "-thumb.jpg")
        return path

    def simple(self):
        return dict(source=self.source, name=self.name, metadata=self.metadata, hash=self.hexdigest, date_uploaded=self.date_uploaded)

    def print_source(self):
        if not self.source:
            return "unknown"
        else: 
            return self.source

    def url(self):
        return settings.MEDIA_URL + str(self.photo)
    
    def create_thumbnail(self, orientation=None, front_camera_str=None, rotation=None):
        print "creating thumbnail"

        # original code for this method came from
        # http://snipt.net/danfreak/generate-thumbnails-in-django-with-pil/

        # If there is no image associated with this.
        # do not create thumbnail
        if not self.photo:
            return

        from PIL import Image
        from cStringIO import StringIO
        # Set our max thumbnail size in a tuple (max width, max height)
        THUMBNAIL_SIZE = (200,200)

      
        PIL_TYPE = 'jpeg'
        FILE_EXTENSION = 'jpg'

        # Open original photo which we want to thumbnail using PIL's Image
        image = Image.open(StringIO(self.photo.read()))

        if orientation == "Portrait":
            if front_camera_str == "true":
                image = image.rotate(90)
            else:
                image = image.rotate(-90)
            print "rotating portrait image", str(self.photo)

        elif orientation == "Landscape":
            if rotation == 3:
                image = image.rotate(180)
                print "rotating upside down landscape image"
        
        image.save(str(self.photo), PIL_TYPE)
        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

        # Save the thumbnail
        thumb_filename = str(self.photo).replace(".jpg", "-thumb.jpg")
        image.save(thumb_filename, PIL_TYPE)

        print "making this picture not hidden anymore", self.hidden
        self.hidden = False
        self.save()
        print "hidden value:", self.hidden
