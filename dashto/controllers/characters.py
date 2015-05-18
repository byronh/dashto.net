from dashto import errors, files, forms
from dashto.controllers.base import BaseController
from dashto.models import DBSession
from dashto.models import Character
from pyramid import httpexceptions
from pyramid.view import view_config
from sqlalchemy.orm import undefer


class CharactersController(BaseController):

    def get_character(self, full=False):
        """ :rtype: Character """
        query = DBSession.query(Character)
        if full:
            query = query.options(undefer('biography'))
        character = query.get(self.params['character_id'])
        if not character:
            raise httpexceptions.HTTPNotFound()
        return character

    @view_config(route_name='characters_view', renderer='characters/view.html')
    def view(self):
        character = self.get_character(full=True)
        return {'character': character}

    @view_config(route_name='characters_edit', renderer='characters/edit.html')
    def edit(self):
        character = self.get_character(full=True)
        if character.user != self.user:
            raise httpexceptions.HTTPForbidden()
        form = forms.CharacterEditForm(**self.form_kwargs)
        if self.request.method == 'GET':
            form.character_name.data = character.name
            form.character_full_name.data = character.full_name
            form.character_biography.data = character.biography
        if self.validate(form):
            character.name = form.character_name.data
            character.full_name = form.character_full_name.data
            character.biography = form.character_biography.data
            portrait = form.character_portrait.data
            if portrait is not None and hasattr(portrait, 'file') and portrait.file != b'':
                old_portrait = character.portrait
                try:
                    thumbnail = files.create_thumbnail(portrait.file)
                    filename = files.file_upload(self.request, thumbnail, portrait.filename, folder='portraits')
                    thumbnail.close()
                    character.portrait = filename
                    return self.redirect('characters_view', character_id=character.id)
                except errors.InvalidFileError:
                    form.character_portrait.errors.append('Only image files are allowed')
                finally:
                    if old_portrait and self.request.storage.exists(old_portrait):
                        self.request.storage.delete(old_portrait)
            else:
                return self.redirect('characters_view', character_id=character.id)
        return {'character': character, 'form': form}

    @view_config(route_name='characters_create', renderer='characters/new.html')
    def create(self):
        form = forms.CharacterCreateForm(**self.form_kwargs)
        if self.validate(form):
            character = Character()
            character.name = form.character_name.data
            character.user = self.user
            DBSession.add(character)
            return self.redirect('users_view', user_id=self.user.id)
        return {'form': form}
