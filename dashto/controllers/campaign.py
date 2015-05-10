from dashto import forms
from dashto.auth.permissions import Permissions
from dashto.controllers.base import BaseController
from dashto.models import DBSession
from dashto.models import Campaign
from pyramid.view import view_config


class CampaignController(BaseController):

    @view_config(route_name='chat', renderer='chat.html', permission=Permissions.PUBLIC)
    def chat(self):
        form = forms.ChatForm(**self.form_kwargs)
        return {'form': form}

    @view_config(route_name='campaign', match_param='action=new', renderer='campaign/new.html', permission=Permissions.CREATE)
    def campaign_create(self):
        form = forms.CampaignCreateForm(**self.form_kwargs)
        if self.validate(form):
            campaign = Campaign()
            campaign.name = form.campaign_name.data
            DBSession.add(campaign)
            return self.redirect('home')
        return {'form': form}
