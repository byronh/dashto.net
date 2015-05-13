from dashto import forms
from dashto.controllers.base import BaseController
from dashto.models import DBSession
from dashto.models import Campaign, CampaignMembership
from pyramid import httpexceptions
from pyramid.view import view_config


class CampaignsController(BaseController):

    def get_campaign(self):
        """ :rtype: Campaign """
        campaign = DBSession.query(Campaign).get(self.params['campaign_id'])
        if not campaign:
            raise httpexceptions.HTTPNotFound()
        return campaign

    @view_config(route_name='campaigns_index', renderer='campaigns/index.html')
    def view_all(self):
        campaigns = DBSession.query(Campaign).all()
        return {'campaigns': campaigns}

    @view_config(route_name='campaigns_view', renderer='simple.html')
    def view(self):
        campaign = self.get_campaign()
        return {
            'title': 'View campaign {}'.format(campaign.id),
            'body': campaign.name
        }

    @view_config(route_name='campaigns_play', renderer='campaigns/play.html')
    def play(self):
        campaign = self.get_campaign()
        form = forms.ChatForm(**self.form_kwargs)
        return {'campaign': campaign, 'form': form}

    @view_config(route_name='campaigns_create', renderer='campaigns/new.html')
    def create(self):
        form = forms.CampaignCreateForm(**self.form_kwargs)
        if self.validate(form):
            campaign = Campaign()
            campaign.name = form.campaign_name.data

            membership = CampaignMembership()
            membership.user = self.user
            membership.campaign = campaign
            membership.is_gm = True

            DBSession.add(campaign)
            DBSession.add(membership)
            return self.redirect('campaigns_index')
        return {'form': form}
