import json
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

    def get_membership(self, campaign):
        """ :rtype: Membership """
        query = DBSession.query(Membership).join(User).filter(Membership.campaign == campaign)
        membership = query.filter(Membership.user == self.user).first()
        return membership

    def get_memberships(self, campaign):
        query = DBSession.query(Membership).join(User).filter(Membership.campaign == campaign)
        query = query.filter(Membership.status >= Membership.Status.member.value)
        return query.options(contains_eager(Membership.user)).order_by(Membership.status.desc(), User.name).all()

    @view_config(route_name='campaigns_index', renderer='campaigns/index.html')
    def view_all(self):
        campaigns = DBSession.query(Campaign).order_by(Campaign.name).all()
        return {'campaigns': campaigns}

    @view_config(route_name='campaigns_view', renderer='campaigns/view.html')
    def view(self):
        campaign = self.get_campaign()
        memberships = self.get_memberships(campaign)
        membership = self.get_membership(campaign)
        return {'campaign': campaign, 'memberships': memberships, 'membership': membership}

    @view_config(route_name='campaigns_play', renderer='campaigns/play.html')
    def play(self):
        campaign = self.get_campaign()
        membership = self.get_membership(campaign)
        if not membership or not membership.is_member:
            raise httpexceptions.HTTPForbidden()
        form = forms.ChatForm(**self.form_kwargs)
        return {'campaign': campaign, 'form': form, 'chat_target': self.config['chat.target']}

    @view_config(route_name='campaigns_request_join')
    def request_join(self):
        form = forms.CampaignRequestJoinForm(**self.form_kwargs)
        if not self.validate(form):
            raise httpexceptions.HTTPBadRequest()
        campaign = self.get_campaign()
        membership = self.get_membership(campaign)
        if membership:
            raise httpexceptions.HTTPForbidden()
        membership = Membership()
        membership.user = self.user
        membership.campaign = campaign
        membership.status = Membership.Status.pending.value

        DBSession.add(membership)
        DBSession.flush()

        self.publish('chan:1', {'message': 'Created new membership for {}'.format(self.user.id)})

        return self.redirect('campaigns_view', campaign_id=campaign.id)

    @view_config(route_name='campaigns_create', renderer='campaigns/new.html')
    def create(self):
        form = forms.CampaignCreateForm(**self.form_kwargs)
        if self.validate(form):
            campaign = Campaign()
            campaign.name = form.campaign_name.data
            campaign.description = form.campaign_description.data

            membership = Membership()
            membership.user = self.user
            membership.campaign = campaign
            membership.status = Membership.Status.gm.value

            DBSession.add(campaign)
            DBSession.add(membership)
            return self.redirect('campaigns_index')
        return {'form': form}
