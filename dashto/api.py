from pyramid.view import view_config


class APIController:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='api', renderer='json')
    def example(self):
        return {'item': 'something'}