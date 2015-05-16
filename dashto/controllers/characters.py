from dashto import forms
from dashto.controllers.base import BaseController
from dashto.models import DBSession
from dashto.models import Character
from pyramid import httpexceptions
from pyramid.view import view_config


class CharactersController(BaseController):

    def get_character(self):
        """ :rtype: Character """
        character = DBSession.query(Character).get(self.params['character_id'])
        if not character:
            raise httpexceptions.HTTPNotFound()
        return character

    @view_config(route_name='characters_index', renderer='characters/index.html')
    def view_all(self):
        characters = DBSession.query(Character).filter(Character.user == self.user).all()
        return {'characters': characters}

    @view_config(route_name='characters_view', renderer='characters/view.html')
    def view(self):
        character = self.get_character()
        return {'character': character}

    @view_config(route_name='characters_edit', renderer='characters/edit.html')
    def edit(self):
        character = self.get_character()
        form = forms.CharacterEditForm(**self.form_kwargs)
        if self.request.method == 'GET':
            form.character_name.data = character.name
            form.character_full_name.data = character.full_name
            form.character_biography.data = character.biography
        if self.validate(form):
            character.name = form.character_name.data
            character.full_name = form.character_full_name.data
            character.biography = form.character_biography.data
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
            return self.redirect('characters_index')
        return {'form': form}
