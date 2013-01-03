from cornice.resource import resource, view
from gnome.weather import Wind

from webgnome import util
from webgnome.model_manager import WebWindMover
from webgnome.schema import WindMoverSchema
from webgnome.views.services.base import BaseResource


@resource(collection_path='/model/{model_id:\d+}/mover/wind',
          path='/model/{model_id:\d+}/mover/wind/{id:\d+}',
          renderer='gnome_json', description='A wind mover.')
class WindMover(BaseResource):

    def get_wind(self, wind_data):
        """
        Return a :class:`gnome.weather.Wind` object initialized with the data
        in ``wind_data``, a dict.
        """
        return Wind(units=wind_data['units'],
                    timeseries=wind_data['timeseries'])

    @view(validators=util.valid_model_id, schema=WindMoverSchema)
    def collection_post(self):
        """
        Create a WindMover from a JSON representation.
        """
        data = self.request.validated
        data['wind'] = self.get_wind(data['wind'])
        model = data.pop('model')
        mover = WebWindMover(**data)
        model.add_mover(mover)

        return {
            'success': True,
            'id': mover.id
        }

    @view(validators=util.valid_mover_id)
    def get(self):
        """
        Return a JSON representation of WindMover matching the ``id`` matchdict
        value.
        """
        model = self.request.validated.pop('model')
        return model.get_mover(self.id).to_dict()

    @view(validators=util.valid_mover_id, schema=WindMoverSchema)
    def put(self):
        """
        Update an existing WindMover from a JSON representation.
        """
        data = self.request.validated
        data['wind'] = self.get_wind(data['wind'])
        model = data.pop('model')
        mover = model.get_mover(self.id).from_dict(data)

        return {
            'success': True,
            'id': mover.id
        }

    @view(validators=util.valid_mover_id)
    def delete(self):
        """
        Delete a WindMover.
        """
        self.request.validated['model'].remove_mover(self.id)
        message = util.make_message('success', 'Deleted wind mover.')

        return {
            'success': True,
            'mover_id': self.id,
            'message': message
        }
