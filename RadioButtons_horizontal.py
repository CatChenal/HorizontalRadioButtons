
# coding: utf-8

# # Implementing matplotlib RadioButtons widget in the horizontal direction

# ## Motivation:
# 
# ### to obtain a RadioButton widget as a horizontal arry of circles & labels
# 

# ## The current (and only) behaviour is the vertical array:
# ![RadioButtons, vertical](./RadioButtonsV.png)

# ## My progress so far:
# ![RadioButtons, Horizontal](./RadioButtonsH.png)

# ## What's left to be done:
# <pre><code>
# . [x] Add orientation option to Radiobuttons widget
# . [ ] Fix the spacing of the (circle, label) pairs:: need to be relative to some axis
# . [ ] Test position of widget outside of frame, e.g. below x-axis title
# . [ ] Open a pull request
# </code></pre>

# In[64]:

get_ipython().magic('matplotlib notebook')


# In[65]:

import matplotlib.pyplot as plt

plt.rcParams["patch.force_edgecolor"] = True  # needed since python3
plt.rcParams["patch.edgecolor"] = 'black'
plt.rcParams["patch.linewidth"] = 0.25

import numpy as np


# In[66]:

# import the artist class from matplotlib
from matplotlib.artist import Artist

def rec_gc(art, depth=0):
    if isinstance(art, Artist):
        # increase the depth for pretty printing
        print("  " * depth + str(art))
        for child in art.get_children():
            rec_gc(child, depth+2)


# In[67]:

'''
    portion of https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/widgets.py
'''
import copy

import numpy as np
from matplotlib import rcParams

from matplotlib.patches import Circle, Rectangle, Ellipse
from matplotlib.lines import Line2D
from matplotlib.transforms import blended_transform_factory

class Widget(object):
    """
    Abstract base class for GUI neutral widgets
    """
    drawon = True
    eventson = True
    _active = True

    def set_active(self, active):
        """Set whether the widget is active.
        """
        self._active = active

    def get_active(self):
        """Get whether the widget is active.
        """
        return self._active

    # set_active is overridden by SelectorWidgets.
    active = property(get_active, lambda self, active: self.set_active(active),
                      doc="Is the widget active?")

    def ignore(self, event):
        """Return True if event should be ignored.
        This method (or a version of it) should be called at the beginning
        of any event callback.
        """
        return not self.active


class AxesWidget(Widget):
    """Widget that is connected to a single
    :class:`~matplotlib.axes.Axes`.
    To guarantee that the widget remains responsive and not garbage-collected,
    a reference to the object should be maintained by the user.
    This is necessary because the callback registry
    maintains only weak-refs to the functions, which are member
    functions of the widget.  If there are no references to the widget
    object it may be garbage collected which will disconnect the
    callbacks.
    Attributes:
    *ax* : :class:`~matplotlib.axes.Axes`
        The parent axes for the widget
    *canvas* : :class:`~matplotlib.backend_bases.FigureCanvasBase` subclass
        The parent figure canvas for the widget.
    *active* : bool
        If False, the widget does not respond to events.
    """
    def __init__(self, ax):
        self.ax = ax
        self.canvas = ax.figure.canvas
        self.cids = []

    def connect_event(self, event, callback):
        """Connect callback with an event.
        This should be used in lieu of `figure.canvas.mpl_connect` since this
        function stores callback ids for later clean up.
        """
        cid = self.canvas.mpl_connect(event, callback)
        self.cids.append(cid)

    def disconnect_events(self):
        """Disconnect all events created by this widget."""
        for c in self.cids:
            self.canvas.mpl_disconnect(c)

##### copy of class RadioButtons(AxesWidget) :: added 'direction' parameter            
class RadioButtons2(AxesWidget):
    """
    A GUI neutral radio button.
    For the buttons to remain responsive
    you must keep a reference to this object.
    The following attributes are exposed:
     *ax*
        The :class:`matplotlib.axes.Axes` instance the buttons are in
     *activecolor*
        The color of the button when clicked
     *labels*
        A list of :class:`matplotlib.text.Text` instances
     *circles*
        A list of :class:`matplotlib.patches.Circle` instances
     *value_selected*
        A string listing the current value selected
    Connect to the RadioButtons with the :meth:`on_clicked` method
    """
    def __init__(self, ax, labels, active=0, activecolor='blue', direction='v'):
        """
        Add radio buttons to :class:`matplotlib.axes.Axes` instance *ax*
        *labels*
            A len(buttons) list of labels as strings
        *active*
            The index into labels for the button that is active
        *activecolor*
            The color of the button when clicked
        """
        AxesWidget.__init__(self, ax)
        self.activecolor = activecolor
        self.value_selected = None
        
        ax.set_xticks([])
        ax.set_yticks([])
        
        ax.set_navigate(False)
        axcolor = ax.get_facecolor()
        
        cnt = 0
        self.labels = []
        self.circles = []
        
##### Amended section ##### 

        ## Validity test on direction:
        direction = direction.lower()
        if direction not in('v', 'h'):
            print('Unkown direction string: {}; Reverted to default(v).'.format(direction))
            direction ='v'
            
        x0_circle = 0.15  ## relative position of cicles or 1st circle if horizontal
        x0_text = 0.25    ## relative position of label or 1st label if horizontal
        
        if direction == 'v':
            # default: vertically aligned:
            dy = 1. / (len(labels) + 1)
            ys = np.linspace(1 - dy, dy, len(labels))

            # scale the radius of the circle with the spacing between each one
            circle_radius = (dy / 2) - 0.01

            # defaul to hard-coded value if the radius becomes too large
            if(circle_radius > 0.05):
                circle_radius = 0.05

            for y, label in zip(ys, labels):
                t = ax.text(x0_text, y, label, transform=ax.transAxes,
                            horizontalalignment='left',
                            verticalalignment='center')

                if cnt == active:
                    self.value_selected = label
                    facecolor = activecolor
                else:
                    facecolor = axcolor

                p = Circle(xy=(x0_circle, y), radius=circle_radius, edgecolor='black',
                           facecolor=facecolor, transform=ax.transAxes)

                self.labels.append(t)
                self.circles.append(p)
                ax.add_patch(p)
                cnt += 1
        else:
            # horizontally aligned:
            y0 = 0.8

            dx1 = 0.05  # spacing btw a circle and its label
            dx2 = 0.01  # spacing btw a label and the next circle
            dx = dx1 + dx2

            # scale the radius of the circle with the spacing between each one
            circle_radius = (y0 / 2) - dx2
            
            # defaul to hard-coded value if the radius becomes too large
            if(circle_radius > 0.05):
                circle_radius = 0.05
                
    
            # store the circles positions:
            dx_c = np.zeros((1, len(labels)))
            
            idx = range(len(labels))
            
            for i in idx:
                if i == 0:
                    dx_c[0, i] = x0_circle
                else:
                    dx_c[0, i] = dx_c[0, i-1] + dx + len(labels[i-1])/30
                    
                print(dx_c[0, i], labels[i], len(labels[i]))                ## debug

            
            for i, label in zip(idx, labels):
                t = ax.text(dx_c[0, i] + dx1, y0, label, transform=ax.transAxes,
                                             horizontalalignment='left',
                                             verticalalignment='center',
                                             multialignment='left')

                if cnt == active:
                    self.value_selected = label
                    facecolor = activecolor
                else:
                    facecolor = axcolor

                p = Circle(xy=(dx_c[0, i], y0), radius=circle_radius, edgecolor='black',
                           facecolor=facecolor, transform=ax.transAxes)

                self.labels.append(t)
                self.circles.append(p)
                ax.add_patch(p)
                cnt += 1
                
##### Amended section End #####                

        self.connect_event('button_press_event', self._clicked)

        self.cnt = 0
        self.observers = {}

    def _clicked(self, event):
        if self.ignore(event) or event.button != 1 or event.inaxes != self.ax:
            return
        xy = self.ax.transAxes.inverted().transform_point((event.x, event.y))
        pclicked = np.array([xy[0], xy[1]])
        for i, (p, t) in enumerate(zip(self.circles, self.labels)):
            if (t.get_window_extent().contains(event.x, event.y)
                    or np.linalg.norm(pclicked - p.center) < p.radius):
                self.set_active(i)
                break

    def set_active(self, index):
        """
        Trigger which radio button to make active.
        *index* is an index into the original label list
            that this object was constructed with.
            Raise ValueError if the index is invalid.
        Callbacks will be triggered if :attr:`eventson` is True.
        """
        if 0 > index >= len(self.labels):
            raise ValueError("Invalid RadioButton index: %d" % index)

        self.value_selected = self.labels[index].get_text()

        for i, p in enumerate(self.circles):
            if i == index:
                color = self.activecolor
            else:
                color = self.ax.get_facecolor()
            p.set_facecolor(color)

        if self.drawon:
            self.ax.figure.canvas.draw()

        if not self.eventson:
            return
        for cid, func in self.observers.items():
            func(self.labels[index].get_text())

    def on_clicked(self, func):
        """
        When the button is clicked, call *func* with button label
        A connection id is returned which can be used to disconnect
        """
        cid = self.cnt
        self.observers[cid] = func
        self.cnt += 1
        return cid

    def disconnect(self, cid):
        """remove the observer with connection id *cid*"""
        try:
            del self.observers[cid]
        except KeyError:
            pass


# In[74]:

#from matplotlib.widgets import RadioButtons
import matplotlib
#import string

def saveFig(d):
    figname = 'RadioButtons'+ str(d).upper() + '.png' 
    print(figname)
    plt.savefig(figname, dpi=100)

activecolors = {0:'#97FFFF', 1:'#FF7F24', 2:'#006400', 3:'#778899'}

plt.figure()

rax = plt.axes([0.1, 0.1, 0.9, 0.9], frameon=True ,aspect='equal')

rxl = rax.get_xlim()
axl = plt.gca()
print('rax: {}; gca: {}'.format(rxl, axl))

labels = ['one', 'could be two', 'and more than that']

dirx = 'h'
radios = RadioButtons2(rax, labels, active=a, activecolor=activecolors[1], direction=dirx);

for circle in radios.circles: # adjust radius here. The default is 0.05
    circle.set_radius(0.02)   # ?? working?

saveFig(dirx)

plt.show()


# In[126]:

# Call this function on the legend artist to see what the legend is made up of
rec_gc(rax)

np.clip()
'''
Given an interval, values outside the interval are clipped to
the interval edges.  For example, if an interval of ``[0, 1]``
is specified, values smaller than 0 become 0, and values larger
than 1 become 1.
'''