from dashto import forms
from dashto.auth import Permissions
from dashto.controllers.base import BaseController
from dashto.models import DBSession
from dashto.models import Campaign
from pyramid.view import view_config


class CampaignsController(BaseController):

    @view_config(route_name='campaigns_index', renderer='campaigns/index.html')
    def view_all(self):
        campaigns = DBSession.query(Campaign).all()
        return {'campaigns': campaigns}

    @view_config(route_name='campaigns_view', renderer='simple.html')
    def view(self):
        campaign = DBSession.query(Campaign).get(self.params['campaign_id'])
        return {
            'title': 'View campaign {}'.format(campaign.id),
            'body': campaign.name
        }

    @view_config(route_name='chat', renderer='chat.html', permission=Permissions.PUBLIC)
    def chat(self):
        form = forms.ChatForm(**self.form_kwargs)
        return {'form': form}

    @view_config(route_name='campaigns_create', match_param='action=new', renderer='campaigns/new.html')
    def campaign_create(self):
        form = forms.CampaignCreateForm(**self.form_kwargs)
        if self.validate(form):
            campaign = Campaign()
            campaign.name = form.campaign_name.data
            DBSession.add(campaign)
            return self.redirect('home')
        return {'form': form}
