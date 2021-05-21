
# Major library imports
from numpy import array, asarray
from numpy.linalg import norm

# Enthought library imports
from enthought.traits.api import Any, Array, Bool, Enum, Float, Int, List, Tuple, Trait
from enthought.enable2.api import ColorTrait

# Local, relative imports
from scatterplot import render_markers
from scatter_markers import marker_trait
from tooltip import ToolTip


# Used to specify the position of the label relative to its target
LabelPositionTrait = Enum("top right", "bottom", "left", "right", "top", "top left",
                         "bottom left", "bottom right", "center")


def draw_arrow(gc, pt1, pt2, color, arrowhead_size=10.0, offset1=0,
               offset2=0, arrow=None):
    """ Renders an arrow from pt1 to pt2

    Parameters
    ==========
    gc: the graphics context on which to render the arrow
    pt1: the origin point of the arrow
    pt2: the point to which the arrow is pointing
    color: a 3- or 4-tuple of color value to use for the arrow stem and head
    arrowhead_size: the number of screen units corresponding to the length
                    of the arrowhead
    offset1: the amount of space from the start of the arrow to pt1
    offset2: the amount of space from the tip of the arrow to pt2
    arrow: an opaque object returned by previous calls to draw_arrow.  If this
           is provided, all other arguments (except gc) are ignored

    Returns
    =======
    an 'arrow' (opaque object) which can be passed in to subsequent
    calls to this method which short-circuit some of the computation.
    """

    if arrow is None:
        pt1 = asarray(pt1)
        pt2 = asarray(pt2)

        unit_vec = (pt2-pt1)
        unit_vec /= norm(unit_vec)

        if unit_vec[0] == 0:
            perp_vec = array((0.3 * arrowhead_size,0))
        elif unit_vec[1] == 0:
            perp_vec = array((0,0.3 * arrowhead_size))
        else:
            slope = unit_vec[1]/unit_vec[0]
            perp_slope = -1/slope
            perp_vec = array((1.0, perp_slope))
            perp_vec *= 0.3 * arrowhead_size / norm(perp_vec)

        pt1 = pt1 + offset1 * unit_vec
        pt2 = pt2 - offset2 * unit_vec
        
        arrowhead_l = pt2 - (arrowhead_size*unit_vec + perp_vec)
        arrowhead_r = pt2 - (arrowhead_size*unit_vec - perp_vec)
        arrow = (pt1, pt2, arrowhead_l, arrowhead_r)
    else:
        pt1, pt2, arrowhead_l, arrowhead_r = arrow
        
    gc.set_stroke_color(color)
    gc.set_fill_color(color)
    gc.begin_path()
    gc.move_to(*pt1)
    gc.line_to(*pt2)
    gc.stroke_path()
    gc.move_to(*pt2)
    gc.line_to(*arrowhead_l)
    gc.line_to(*arrowhead_r)
    gc.fill_path()
    return arrow


class DataLabel(ToolTip):
    """ Labels a point in data space """

    # The point in data space where this label should anchor itself
    data_point = Trait(None, None, Tuple, List, Array)

    # The location of the data label relative to the data point
    label_position = LabelPositionTrait

    # Should the label clip itself against the main plot area?  If not, then
    # the label will draw  into the padding area (where axes typically reside).
    clip_to_plot = Bool(True)

    #----------------------------------------------------------------------
    # Marker traits
    #----------------------------------------------------------------------

    # Whether or not to mark the point on the data that this label refers to
    marker_visible = Bool(True)

    # The type of marker to use.  This is a mapped trait using strings as the
    # keys.
    marker = marker_trait
    
    # The pixel size of the marker (doesn't include the thickness of the outline)
    marker_size = Int(4)
    
    # The thickness, in pixels, of the outline to draw around the marker.  If
    # this is 0, no outline will be drawn.
    marker_line_width = Float(1.0)

    # The color of the inside of the marker
    marker_color = ColorTrait("red")

    # The color out of the border drawn around the marker
    marker_line_color = ColorTrait("black")

    #----------------------------------------------------------------------
    # Arrow traits
    #----------------------------------------------------------------------
    
    # Whether or not to draw an arrow from the label to the data point.  Only
    # used if data_point is not None.
    # FIXME: replace with some sort of ArrowStyle
    arrow_visible = Bool(True)

    # The length of the arrowhead, in screen points (e.g. pixels)
    arrow_size = Float(5)

    # The color of the arrow
    arrow_color = ColorTrait("black")

    # Determines the position of the base of the arrow on the label.  If
    # 'auto', then uses label_position.  Otherwise, treats the label as if
    # it were at the label position indicated in arrow_root.
    arrow_root = Trait("auto", "auto", "top left", "top right", "bottom left",
                       "bottom right")

    #-------------------------------------------------------------------------
    # Private traits
    #-------------------------------------------------------------------------

    # Tuple (sx, sy) of the mapped screen coords of self.data_point
    _screen_coords = Any

    _cached_arrow = Any

    # When arrow_root is 'auto', this determines the location on the data label
    # from which the arrow is drawn based on the position of the label relative
    # to its data point.
    position_root_map = {
        "top left": ("x2", "y"),
        "top right": ("x", "y"),
        "bottom left": ("x2", "y2"),
        "bottom right": ("x", "y2"),
        }


    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        if self.clip_to_plot:
            gc.save_state()
            c = component
            gc.clip_to_rect(c.x, c.y, c.width, c.height)

        self.do_layout()
        
        # draw the arrow if necessary
        if self.arrow_visible:
            if self._cached_arrow is None:
                if self.arrow_root == "auto" or self.arrow_root not in self.position_root_map:
                    ox, oy = self.position_root_map.get(self.label_position,
                                       (self.x+self.width/2, self.y+self.height/2))
                else:
                    ox, oy = self.position_root_map.get(self.arrow_root)
                    
                if type(ox) == str:
                    ox = getattr(self, ox)
                    oy = getattr(self, oy)
                self._cached_arrow = draw_arrow(gc, (ox, oy), self._screen_coords,
                                                self.arrow_color_,
                                                offset1=3,
                                                offset2=self.marker_size+3)
            else:
                draw_arrow(gc, None, None, None, arrow=self._cached_arrow)

        # layout and render the label itself
        ToolTip.overlay(self, component, gc, view_bounds, mode)

        # draw the marker
        if self.marker_visible:
            render_markers(gc, [self._screen_coords], self.marker, self.marker_size,
                           self.marker_color_, self.marker_line_width, self.marker_line_color_)

        if self.clip_to_plot:
            gc.restore_state()

    def _do_layout(self, size=None):
        if not self.component or not hasattr(self.component, "map_screen"):
            return
        ToolTip._do_layout(self)

        self._screen_coords = self.component.map_screen(self.data_point)
        sx, sy = self._screen_coords
        orientation = self.label_position
        if ("left" in orientation) or ("right" in orientation):
            if " " not in orientation:
                self.y = sy - self.height / 2
            if "left" in orientation:
                self.outer_x = sx - self.outer_width - 1
            elif "right" in orientation:
                self.outer_x = sx
        if ("top" in orientation) or ("bottom" in orientation):
            if " " not in orientation:
                self.x = sx - self.width / 2
            if "bottom" in orientation:
                self.outer_y = sy - self.outer_height - 1
            elif "top" in orientation:
                self.outer_y = sy
        if orientation == "center":
            self.x = sx - (self.width/2)
            self.y = sy - (self.height/2)

        self._cached_arrow = None
        return

    def _data_point_changed(self, old, new):
        if new is not None:
            self.lines = [str(new)]
