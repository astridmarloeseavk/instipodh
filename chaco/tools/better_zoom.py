import numpy

from chaco.grid_mapper import GridMapper
from enable.api import BaseTool, KeySpec
from traits.api import Enum, Float, Instance, Bool, HasTraits, List

from tool_history_mixin import ToolHistoryMixin
from tool_states import ZoomState, PanState, GroupedToolState, ToolState


class BetterZoom(BaseTool, ToolHistoryMixin):

    # Keys to zoom in/out
    zoom_in_key = Instance(KeySpec, args=("+",))
    zoom_out_key = Instance(KeySpec, args=("-",))

    # Keys to zoom in/out in x direction only
    zoom_in_x_key = Instance(KeySpec, args=("Right", "shift"))
    zoom_out_x_key = Instance(KeySpec, args=("Left", "shift"))

    # Keys to zoom in/out in y direction only
    zoom_in_y_key = Instance(KeySpec, args=("Up", "shift"))
    zoom_out_y_key = Instance(KeySpec, args=("Down", "shift"))

    # Key to go to the previous state in the history.
    prev_state_key = Instance(KeySpec, args=("z", "control"))

    # Key to go to the next state in the history.
    next_state_key = Instance(KeySpec, args=("y", "control"))

    # Enable the mousewheel for zooming?
    enable_wheel = Bool(True)

    # if the mouse pointer should be used to control the center
    # of the zoom action
    zoom_to_mouse = Bool(False)

    # The axis to which the selection made by this tool is perpendicular. This
    # only applies in 'range' mode.
    axis = Enum("both", "index", "value")

    # The maximum ratio between the original data space bounds and the zoomed-in
    # data space bounds.  If No limit is desired, set to inf
    x_max_zoom_factor = Float(1e5)
    y_max_zoom_factor = Float(1e5)

    # The maximum ratio between the zoomed-out data space bounds and the original
    # bounds.  If No limit is desired, set to -inf
    x_min_zoom_factor = Float(1e-5)
    y_min_zoom_factor = Float(1e-5)

    # The amount to zoom in by. The zoom out will be inversely proportional
    zoom_factor = Float(2.0)

    # The zoom factor on each axis
    _index_factor = Float(1.0)
    _value_factor = Float(1.0)

    # inherited from ToolHistoryMixin, but requires instances of ZoomState
    _history = List(ToolState, [ZoomState((1.0, 1.0), (1.0, 1.0))])

    #--------------------------------------------------------------------------
    #  public interface
    #--------------------------------------------------------------------------

    def zoom_in(self, factor=0):
        if factor == 0:
            factor = self.zoom_factor

        new_index_factor = self._index_factor * factor
        new_value_factor = self._value_factor * factor

        if self.axis == 'value':
            new_index_factor = self._index_factor
        elif self.axis == 'index':
            new_value_factor = self._value_factor

        if self.component.orientation == 'h':
            if self._zoom_limit_reached(new_index_factor, 'x'):
                return
            if self._zoom_limit_reached(new_value_factor, 'y'):
                return
        else:
            if self._zoom_limit_reached(new_index_factor, 'y'):
                return
            if self._zoom_limit_reached(new_value_factor, 'x'):
                return

        if self.zoom_to_mouse:
            location = self.position

            x_map = self._get_x_mapper()
            y_map = self._get_y_mapper()

            next = (x_map.map_data(location[0]),
                    y_map.map_data(location[1]))
            prev = (x_map.map_data(self.component.bounds[0]/2),
                    y_map.map_data(self.component.bounds[1]/2))

            pan_state = PanState(prev, next)
            zoom_state = ZoomState((self._index_factor, self._value_factor),
                                   (new_index_factor, new_value_factor))

            states = GroupedToolState([pan_state, zoom_state])
            states.apply(self)
            self._append_state(states)

        else:

            zoom_state = ZoomState((self._index_factor, self._value_factor),
                                   (new_index_factor, new_value_factor))

            zoom_state.apply(self)
            self._append_state(zoom_state)

    def zoom_out(self, factor=0):
        if factor == 0:
            factor = self.zoom_factor

        new_index_factor = self._index_factor / factor
        new_value_factor = self._value_factor / factor

        if self.axis == 'value':
            new_index_factor = self._index_factor
        elif self.axis == 'index':
            new_value_factor = self._value_factor

        if self.component.orientation == 'h':
            if self._zoom_limit_reached(new_index_factor, 'x'):
                return
            if self._zoom_limit_reached(new_value_factor, 'y'):
                return
        else:
            if self._zoom_limit_reached(new_index_factor, 'y'):
                return
            if self._zoom_limit_reached(new_value_factor, 'x'):
                return

        if self.zoom_to_mouse:
            location = self.position

            x_map = self._get_x_mapper()
            y_map = self._get_y_mapper()

            next = (x_map.map_data(location[0]),
                    y_map.map_data(location[1]))
            prev = (x_map.map_data(self.component.bounds[0]/2),
                    y_map.map_data(self.component.bounds[1]/2))

            pan_state = PanState(prev, next)
            zoom_state = ZoomState((self._index_factor, self._value_factor),
                                   (new_index_factor, new_value_factor))

            states = GroupedToolState([pan_state, zoom_state])
            states.apply(self)
            self._append_state(states)

        else:

            zoom_state = ZoomState((self._index_factor, self._value_factor),
                                   (new_index_factor, new_value_factor))

            zoom_state.apply(self)
            self._append_state(zoom_state)

    def zoom_in_x(self, factor=0):
        if factor == 0:
            factor = self.zoom_factor

        if self.component.orientation == 'h':
            new_index_factor = self._index_factor * factor
            new_value_factor = self._value_factor
            if self._zoom_limit_reached(new_index_factor, 'x'):
                return
        else:
            new_index_factor = self._index_factor
            new_value_factor = self._value_factor * factor
            if self._zoom_limit_reached(new_value_factor, 'x'):
                return

        if self.zoom_to_mouse:
            location = self.position

            x_map = self._get_x_mapper()
            y_map = self._get_y_mapper()

            next = (x_map.map_data(location[0]),
                    y_map.map_data(location[1]))
            prev = (x_map.map_data(self.component.bounds[0]/2),
                    y_map.map_data(self.component.bounds[1]/2))

            pan_state = PanState(prev, next)
            zoom_state = ZoomState((self._index_factor, self._value_factor),
                                   (new_index_factor, new_value_factor))

            states = GroupedToolState([pan_state, zoom_state])
            states.apply(self)
            self._append_state(states)

        else:

            zoom_state = ZoomState((self._index_factor, self._value_factor),
                                   (new_index_factor, new_value_factor))

            zoom_state.apply(self)
            self._append_state(zoom_state)

    def zoom_out_x(self, factor=0):
        if factor == 0:
            factor = self.zoom_factor

        if self.component.orientation == 'h':
            new_index_factor = self._index_factor / factor
            new_value_factor = self._value_factor
            if self._zoom_limit_reached(new_index_factor, 'x'):
                return
        else:
            new_index_factor = self._index_factor
            new_value_factor = self._value_factor / factor
            if self._zoom_limit_reached(new_value_factor, 'x'):
                return

        if self.zoom_to_mouse:
            location = self.position

            x_map = self._get_x_mapper()
            y_map = self._get_y_mapper()

            next = (x_map.map_data(location[0]),
                    y_map.map_data(location[1]))
            prev = (x_map.map_data(self.component.bounds[0]/2),
                    y_map.map_data(self.component.bounds[1]/2))

            pan_state = PanState(prev, next)
            zoom_state = ZoomState((self._index_factor, self._value_factor),
                                   (new_index_factor, new_value_factor))

            states = GroupedToolState([pan_state, zoom_state])
            states.apply(self)
            self._append_state(states)

        else:

            zoom_state = ZoomState((self._index_factor, self._value_factor),
                                   (new_index_factor, new_value_factor))

            zoom_state.apply(self)
            self._append_state(zoom_state)

    def zoom_in_y(self, factor=0):
        if factor == 0:
            factor = self.zoom_factor

        if self.component.orientation == 'v':
            new_index_factor = self._index_factor * factor
            new_value_factor = self._value_factor
            if self._zoom_limit_reached(new_index_factor, 'y'):
                return
        else:
            new_index_factor = self._index_factor
            new_value_factor = self._value_factor * factor
            if self._zoom_limit_reached(new_value_factor, 'y'):
                return

        if self.zoom_to_mouse:
            location = self.position

            x_map = self._get_x_mapper()
            y_map = self._get_y_mapper()

            next = (x_map.map_data(location[0]),
                    y_map.map_data(location[1]))
            prev = (x_map.map_data(self.component.bounds[0]/2),
                    y_map.map_data(self.component.bounds[1]/2))

            pan_state = PanState(prev, next)
            zoom_state = ZoomState((self._index_factor, self._value_factor),
                                   (new_index_factor, new_value_factor))

            states = GroupedToolState([pan_state, zoom_state])
            states.apply(self)
            self._append_state(states)

        else:

            zoom_state = ZoomState((self._index_factor, self._value_factor),
                                   (new_index_factor, new_value_factor))

            zoom_state.apply(self)
            self._append_state(zoom_state)

    def zoom_out_y(self, factor=0):
        if factor == 0:
            factor = self.zoom_factor

        if self.component.orientation == 'v':
            new_index_factor = self._index_factor / factor
            new_value_factor = self._value_factor
            if self._zoom_limit_reached(new_index_factor, 'y'):
                return
        else:
            new_index_factor = self._index_factor
            new_value_factor = self._value_factor / factor
            if self._zoom_limit_reached(new_value_factor, 'y'):
                return

        if self.zoom_to_mouse:
            location = self.position

            x_map = self._get_x_mapper()
            y_map = self._get_y_mapper()

            next = (x_map.map_data(location[0]),
                    y_map.map_data(location[1]))
            prev = (x_map.map_data(self.component.bounds[0]/2),
                    y_map.map_data(self.component.bounds[1]/2))

            pan_state = PanState(prev, next)
            zoom_state = ZoomState((self._index_factor, self._value_factor),
                                   (new_index_factor, new_value_factor))

            states = GroupedToolState([pan_state, zoom_state])
            states.apply(self)
            self._append_state(states)

        else:

            zoom_state = ZoomState((self._index_factor, self._value_factor),
                                   (new_index_factor, new_value_factor))

            zoom_state.apply(self)
            self._append_state(zoom_state)

    #--------------------------------------------------------------------------
    #  BaseTool interface
    #--------------------------------------------------------------------------

    def normal_key_pressed(self, event):
        """ Handles a key being pressed when the tool is in the 'normal'
        state.
        """
        if self.zoom_in_key.match(event):
            self.position = self._center_screen()
            self.zoom_in()
            event.handled = True
        elif self.zoom_out_key.match(event):
            self.position = self._center_screen()
            self.zoom_out()
            event.handled = True
        elif self.zoom_in_x_key.match(event):
            self.position = self._center_screen()
            self.zoom_in_x(self.zoom_factor)
            event.handled = True
        elif self.zoom_out_x_key.match(event):
            self.position = self._center_screen()
            self.zoom_out_x(self.zoom_factor)
            event.handled = True
        elif self.zoom_in_y_key.match(event):
            self.position = self._center_screen()
            self.zoom_in_y(self.zoom_factor)
            event.handled = True
        elif self.zoom_out_y_key.match(event):
            self.position = self._center_screen()
            self.zoom_out_y(self.zoom_factor)
            event.handled = True

        ToolHistoryMixin.normal_key_pressed(self, event)

        return

    def normal_mouse_wheel(self, event):
        if not self.enable_wheel:
            return

        if event.mouse_wheel != 0:
            if event.mouse_wheel > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.handled = True

    def normal_mouse_move(self, event):
        self.position = (event.x, event.y)

    def normal_mouse_enter(self, event):
        """ Try to set the focus to the window when the mouse enters, otherwise
            the keypress events will not be triggered.
        """
        if self.component._window is not None:
            self.component._window._set_focus()

    #--------------------------------------------------------------------------
    #  private interface
    #--------------------------------------------------------------------------

    def _center_screen(self):
        return self.component.bounds[0]/2, self.component.bounds[1]/2

    def _zoom_limit_reached(self, factor, xy_axis):
        """ Returns True if the new low and high exceed the maximum zoom
        limits
        """

        if xy_axis == 'x':
            if factor <= self.x_max_zoom_factor and factor >= self.x_min_zoom_factor:
                return False
            return True
        else:
            if factor <= self.y_max_zoom_factor and factor >= self.y_min_zoom_factor:
                return False
            return True

    def _zoom_in_mapper(self, mapper, factor):

        high = mapper.range.high
        low = mapper.range.low
        range = high-low

        center = (low + high)/2.0

        new_range = range/factor
        mapper.range.high = center + new_range/2
        mapper.range.low = center - new_range/2

    def _get_x_mapper(self):
        if isinstance(self.component.index_mapper, GridMapper):
            if self.component.orientation == "h":
                return self.component.index_mapper._xmapper
            return self.component.index_mapper._ymapper
        else:
            if self.component.orientation == "h":
                return self.component.index_mapper
            return self.component.value_mapper

    def _get_y_mapper(self):
        if isinstance(self.component.index_mapper, GridMapper):
            if self.component.orientation == "h":
                return self.component.index_mapper._ymapper
            return self.component.index_mapper._xmapper
        else:
            if self.component.orientation == "h":
                return self.component.value_mapper
            return self.component.index_mapper

    #--------------------------------------------------------------------------
    #  ToolHistoryMixin interface
    #--------------------------------------------------------------------------

    def _next_state_pressed(self):
        """ Called when the tool needs to advance to the next state in the
        stack.

        The **_history_index** will have already been set to the index
        corresponding to the next state.
        """

        self._current_state().apply(self)

    def _prev_state_pressed(self):
        """ Called when the tool needs to advance to the previous state in the
        stack.

        The **_history_index** will have already been set to the index
        corresponding to the previous state.
        """
        self._history[self._history_index+1].revert(self)

    def _reset_state_pressed(self):
        """ Called when the tool needs to reset its history.

        The history index will have already been set to 0.
        """
        for state in self._history[::-1]:
            state.revert(self)
        self._history = []
