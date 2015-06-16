from django import forms
from models import *
import hashlib
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import re
import json

class HashPhotoForm(forms.ModelForm):
    tag_string = forms.CharField(label='Tags', max_length=400, help_text="(comma separated)")

    class Meta:
        model = HashPhoto
        fields = ['photo', 'tag_string', 'source', 'latitude', 'longitude', 'name']

    def save(self, post_variables):
        print "computeHashAndSaveWithTags" # are we in this function?
        metadata = json.dumps(post_variables.dict())

        # get the tags from the form
        tag_string = self.cleaned_data.get("tag_string")
        raw_tags = filter(None, re.split("[, ]", tag_string))

        # get the in-memory file data from the form 
        f = self.cleaned_data.get("photo")
        md5 = hashlib.md5()
        for chunk in f.chunks():
            md5.update(chunk)

        print "\tmd5: ", md5.hexdigest()

        orientation = post_variables.get("orientation", None)
        front_camera_str = post_variables.get("front_camera", None) # sends 'true' or 'false'
        rotation = int(post_variables.get("rotation", 0))
        print "\torientation: ", orientation
        print "\front_camera_str: ", front_camera_str
        print "\trotation: ", rotation

        # if photo with that hash exists already, great. otherwise, make a new one.
        try:
            new_photo = HashPhoto.objects.get(hexdigest=md5.hexdigest())
            print new_photo
        except ObjectDoesNotExist:
            new_photo = super(HashPhotoForm, self).save(commit=False)
            new_photo.hexdigest = md5.hexdigest()
            
            new_photo.date_uploaded = timezone.now()
            new_photo.metadata = metadata
            new_photo.save()
            new_photo.create_thumbnail(orientation=orientation, 
                front_camera_str=front_camera_str, 
                rotation=rotation)

        # associate tags with the photo object wherever it came from
        for t in raw_tags:
            new_tag = Tag(t)
            new_tag.save()
            new_photo.tags.add(new_tag)

        return new_photo