from django.conf.urls import patterns, include, url
from django.contrib import admin

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = patterns('',
    url(r'^$', 'sharedcam.views.index', name='index'),
    url(r'^photos$', 'sharedcam.views.photos', name='photos'),
    url(r'^photos/(?P<tag>[^/]+)$', 'sharedcam.views.photos_by_tag', name='tag'),
    url(r'^photo/(?P<hash>[^/]+)$', 'sharedcam.views.photo', name='photo'),

    url(r'^recent/$',  
        'sharedcam.views.recent_content',   name='recent_content'),
    url(r'^recent/(?P<hash>[^/]+)$',  
        'sharedcam.views.recent_content',   name='recent_content'),


    url(r'^flag_content$',      'sharedcam.views.flag',       name='flag_content'),

    url(r'^testphoto_page$', 'sharedcam.views.testphoto_page', name='testphoto_page'),
    url(r'^add$', 'sharedcam.views.process_photo', name='process_photo'),


    # cross-domain problems with remote server, here's a fake stand in, with tags
    url(r'^fake_sharecams$', 'sharedcam.views.fake_sharecams', name='fake_sharecams'),

    url(r'^registry/', include('registry.urls')),


    url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
