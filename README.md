# SharedCamServer
Image repository and registry for shared cam app. Written in Django.

## App #1: `sharedcam`
Acceps new images at `<url>/add`
- Stores image by hash of content to prevent duplicate photos
- Resizes image to generate a thumbnail
- Images saved to local `photostore/` directory inside app

## App #2: `registry`
Manages a registry of realtime guides, available through a custom Jumpchat mobile app.

## App #3: `experimental`
Experimental/spare app for exploratory proramming and prototyping.