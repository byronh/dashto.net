import io
from dashto import errors
from pyramid_storage import exceptions as fileexceptions
from wand.exceptions import WandException
from wand.image import Image


def create_thumbnail(image_file, thumbnail_size=(64, 64), thumbnail_format='png'):
    try:
        thumbnail_file = io.BytesIO()
        with Image(file=image_file) as image:
            with image.clone() as converted:
                converted.resize(*thumbnail_size)
                converted.format = thumbnail_format
                converted.save(file=thumbnail_file)
                return thumbnail_file
    except WandException:
        raise errors.InvalidFileError()

def file_upload(request, file, filename, extensions=None, folder=None):
    try:
        return request.storage.save_file(file, filename, extensions=extensions, folder=folder, randomize=True)
    except fileexceptions.FileNotAllowed:
        raise errors.InvalidFileError()
