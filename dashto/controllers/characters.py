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
        characters = DBSession.query(Character).all()
        return {'characters': characters}

    @view_config(route_name='characters_view', renderer='simple.html')
    def view(self):
        character = self.get_character()
        return {
            'title': 'View character {}'.format(character.id),
            'body': character.name
        }

    @view_config(route_name='characters_create', renderer='characters/new.html')
    def create(self):
        form = forms.CharacterCreateForm(**self.form_kwargs)
        if self.validate(form):
            character = Character()
            character.name = form.character_name.data

            DBSession.add(character)
            return self.redirect('characters_index')
        return {'form': form}
