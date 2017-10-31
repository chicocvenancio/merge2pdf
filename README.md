# merge2pdf
Tool to create PDFs from [Wikimedia Commons](https://commons.wikimedia.org) image files. 
It currently [lives](https://tools.wmflabs.org/merge2pdf/) in Wikimedia Toolforge

## Login
To be able to interact with Wikimedia projects the user must login and provide authorization
to the tool. There is a login on the top of the page.

## Usage
The tool provides a simple interface with three text boxes. The category, the desired filename
in commons, and the desired wikitext in commons.

Currently, only jpeg and tiff images are supported, more formats can be added later if needed.

## Quality
The PDFs images will have the same quality the original images have, for that the great 
[img2pdf](https://gitlab.mister-muffin.de/josch/img2pdf) library is used. It creates a simple
PDF skeleton and inputs the images without renconding them and keeping resolutions. This may
create very large PDFs if the original images are large. 

Commons itself sometimes does not generate thumbnails for large PDFs, diminishing their usefullness,
merge2pdf migh choke on these files as well and timeout. I will investigate and try to improve this
in the future.

## Roadmap
* ~~Direct upload to Commons~~
* Add OCR to pages
* Allow changes in page order
* Allow user list input
* Allow use of arbitrary images
* Allow use of basic text element pages
