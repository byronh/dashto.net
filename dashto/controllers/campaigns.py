from dashto import forms
from dashto.controllers.base import BaseController
from dashto.models import DBSession
from dashto.models import Campaign, Membership, User
from pyramid import httpexceptions
from pyramid.view import view_config
from sqlalchemy.orm import contains_eager


class CampaignsController(BaseController):

    def get_campaign(self):
        """ :rtype: Campaign """
        campaign = DBSession.query(Campaign).get(self.params['campaign_id'])
        if not campaign:
            raise httpexceptions.HTTPNotFound()
        return campaign

    def get_memberships(self, campaign):
        query = DBSession.query(Membership).join(User).filter(Membership.campaign == campaign)
        return query.options(contains_eager(Membership.user)).order_by(Membership.is_gm.desc(), User.name).all()

    @view_config(route_name='campaigns_index', renderer='campaigns/index.html')
    def view_all(self):
        campaigns = DBSession.query(Campaign).order_by(Campaign.name).all()
        return {'campaigns': campaigns}

    @view_config(route_name='campaigns_view', renderer='campaigns/view.html')
    def view(self):
        campaign = self.get_campaign()
        memberships = self.get_memberships(campaign)
        user_ids = [membership.user.id for membership in memberships]
        return {'campaign': campaign, 'memberships': memberships, 'user_ids': user_ids}

    @view_config(route_name='campaigns_play', renderer='campaigns/play.html')
    def play(self):
        campaign = self.get_campaign()
        memberships = self.get_memberships(campaign)
        if self.user.id not in [membership.user.id for membership in memberships]:
            raise httpexceptions.HTTPForbidden()
        form = forms.ChatForm(**self.form_kwargs)
        return {'campaign': campaign, 'form': form}

    @view_config(route_name='campaigns_create', renderer='campaigns/new.html')
    def create(self):
        form = forms.CampaignCreateForm(**self.form_kwargs)
        if self.validate(form):
            campaign = Campaign()
            campaign.name = form.campaign_name.data

            membership = Membership()
            membership.user = self.user
            membership.campaign = campaign
            membership.is_gm = True

            DBSession.add(campaign)
            DBSession.add(membership)
            return self.redirect('campaigns_index')
        return {'form': form}
