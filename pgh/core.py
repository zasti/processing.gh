import scriptcontext as sc
import Rhino
import rhinoscriptsyntax as rs
from Rhino.Geometry import * #?
import Grasshopper.Kernel.Data.GH_Path as Path
import Grasshopper.DataTree as DataTree
import Grasshopper.Kernel as gh #!
import ghpythonlib.components as gc #!
import time
import math
from math import * #!
PI = math.pi
constrain = Rhino.RhinoMath.Clamp
import System.Drawing.Color as Color
import System.Drawing.Rectangle
import perlin
from random import seed as randomSeed
from random import gauss as randomGaussian
from random import shuffle, choice
from random import uniform
from interact import *
Simplex = perlin.SimplexNoise()
def random(a = 1,b = 0):
    "random(a,b)->[a,b], random(a)->[0,a], random()->[0,1]"
    return uniform(a,b)
def noise(*args):
    "Simplex noise 1,2,3d"
    if len(args) == 1:
        return Simplex.noise2(args[0],0)
    elif len(args) == 2:
        return Simplex.noise2(*args)
    else:
        return Simplex.noise3(*args)
def noiseDetial():
    raise NotImplemented

# viewport size
width = 640
height = 800
## global setting
P2D = Rhino.Display.DefinedViewportProjection.Top
P3D = Rhino.Display.DefinedViewportProjection.Perspective
if "DISPLAY" not in sc.sticky:
    sc.sticky["DISPLAY"] = Rhino.Display.CustomDisplay(True)
DISPLAY = sc.sticky["DISPLAY"]

## display setting
class Style:
    def __init__(self):
        self.IS_FILL = True
        self.FILL_COLOR = Color.FromArgb(255,255,255)
        self.IS_STROKE = True
        self.STROKE_COLOR = Color.FromArgb(0,0,0,0)
        self.STROKE_WEIGHT = 1
style = Style()
STYLESTACK = []


CPLANES = [Plane.WorldXY]
#current cplane = CPLANES[-1]
AUTO_DISPLAY = True
GEOMETRY_OUTPUT = True
COLOR_OUTPUT = False

## general setting
TORLERENCE = Rhino.RhinoDoc.ActiveDoc.PageAbsoluteTolerance
# mouse variable
def update_mouse():
    global mouseX,screenX,mouseY,screenY,pmouseX,pmouseY,\
           _pmousePressed,mousePressed,mouseMoved,mouseDragged,mouseClicked
    pmouseX = mouseX
    pmouseY = mouseY
    _pmousePressed = mousePressed
    _posInfo = rs.GetCursorPos()
    mouseX = _posInfo[0].X
    screenX = _posInfo[1].X
    mouseY = _posInfo[0].Y
    screenY = _posInfo[1].Y
    client = VIEWPORT.ClientToWorld(_posInfo[3])
    tup = Intersect.Intersection.LinePlane(client,CPLANES[-1])
    if tup[0]:
        ptOnPlane = client.PointAt(tup[1])
        mouseX = ptOnPlane.X
        mouseY = ptOnPlane.Y
    mousePressed = isMousePressed()
    mouseMoved = pmouseX != mouseX or pmouseY != mouseY
    mouseDragged = mouseMoved and mousePressed
    mouseClicked = _pmousePressed and not mousePressed

# buildin func
def show_grid(switch = False):
    " turn off cplane grid "
    Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.ActiveViewport.ConstructionGridVisible = switch
    Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.ActiveViewport.ConstructionAxesVisible = switch
def get_class(ghenv):
    param = ghenv.Component.Params.Input[1]
    for data in param.VolatileData.AllData(True):
        cls =  data.Value
        ghenv.Script.SetVariable(cls.__name__, cls)

def _clear():
    for uniquevar in [var for var in globals().copy() if var[0] != "_"]:
        del globals()[uniquevar]
def _time_test(fn,arg,time = 1000):
    before = time.clock()
    for i in range(time):
        fn(*arg)
    after = time.clock()
    ms = (after - before)*1000
    print("cost %i ms for %i times"%(ms,count))
    return ms

def NewView(name,Projection,screenX = 0,screenY = 0,seperate = True):
    exist = Rhino.RhinoDoc.ActiveDoc.Views.Find(name,True)
    if not exist:
        exist = Rhino.RhinoDoc.ActiveDoc.Views.Add(
        name,
        Projection,
        System.Drawing.Rectangle(screenX,screenY,screenX+width,screenY+height),
        seperate)
        viewRect = Rectangle3d(CPLANES[-1],width,height)
        exist.ActiveViewport.ZoomBoundingBox(viewRect.BoundingBox)
    return exist
def convert_polyline(curve):
    " return a polyline, if convert fail, raise IndexOutOfBound "
    if isinstance(curve,Polyline):
        return curve
    else:
        nc = curve.ToNurbsCurve()
        return toPolyline(nc).TryGetPolyline()[1]
def toPolyline(curve,maxAngleRadians = 0.1, tolerance = 0.1):
    " simplify ToPolyline buildin "
    return curve.ToPolyline(0,0,maxAngleRadians,0,0, tolerance,0.01,0,True)

## basic processing function ##
def toggleColor(state = False):
    "cancel color out mode"
    global COLOR_OUTPUT
    COLOR_OUTPUT = state
def color(*args):
    "accept : (gray), (gray,alphy), (r,g,b), (r,g,b,a)\
    return : Color"
    length = len(args)
    if length == 1:
        if isinstance(args[0],Color):
            return args[0]
        else:
            return Color.FromArgb(args[0],args[0],args[0])
    elif length == 2:
        return Color.FromArgb(args[1],args[0],args[0],args[0])
    elif length == 3:
        return Color.FromArgb(*args)
    elif length == 4:
        return Color.FromArgb(args[3],args[0],args[1],args[2])
def map(value,a,b,c,d):
    "return remap value from (a,b) --> (c,d)"
    return (value-a)*(d-c)/(b-a) + c
def background(*args):
    " clear OUTPUT, if has args, set backgound color(a,r,g,b) "
    if len(args):
        c = color(*args)
        Rhino.ApplicationSettings.AppearanceSettings.ViewportBackgroundColor = c
    _clearOutput()
def size(w,h,mode=P2D,name='processing'):
    " set size of new viewport "
    global width,height,VIEWPORT
    width = w
    height = h
    VIEWPORT = NewView(name,mode).ActiveViewport

#### add display


### create shape api ###
class Shape(Curve):
    def __init__():
        self.shape = super(self,Shape).__init__()
        self.plist = []
def createShape():
    return Shape()
def beginShape(kind = None):
    #! add fiiled polygon
    num = len(_SHAPESTACK)
    _SHAPESTACK.append([])
    _CSHAPE = _SHAPESTACK[num]
def vertex(x,y,z):
    _CSHAPE.append(Point3d(x,y,z))
def endShape():
    pline = Polyline(_SHAPESTACK.pop())
    if AUTO_DISPLAY:
        Display(pline)
    return pline

### matrix manipulation ###
def translate(*args):
    "translate CPLANES[-1] with (x,y,[z]) or Vector3d"
    if isinstance(args[0],Vector3d):
        CPLANES[-1].Translate(Vector3d)
    else:
        CPLANES[-1].Translate(Vector3d(CPLANES[-1].PointAt(*args)))
def rotate(rad,axis=None,center=None):
    "return True if success"
    cplane = VIEWPORT.ConstructionPlane()
    if not axis:
        axis = cplane.ZAxis
    if not center:
        center = cplane.Origin
    return cplane.Rotate(rad,axis,center)

def pushMatrix():
    CPLANES.append(CPLANES[-1])
def popMatrix():
    if len(CPLANES)>1:
        CPLANES.pop()
def setMatrix(plane):
    "change CPLANES[-1] to given plane"
    CPLANES[-1] = plane
### time related ###
def frameRate(fps):
    ms = 1000/fps
    print("Set Timer Interval to : %i ms" % (ms))
    return ms
def millis():
     return int((time.clock() - _time)*1000)

# other useful buildin
def dist(pt1,pt2):
    return pt1.DistanceTo(pt2)
class PVector():
    " processing PVector interface as Vector3d "
    def __init__(self,*args):
        self.__data = Vector3d(CPLANES[-1].PointAt(*args))
    def __repr__(self):
        return 'self.__data'
    def __str__(self):
        return str(self.__data)
    def __getattr__(self,attr):
        return getattr(self.__data,attr)
    def mag(self):
        return self.Length
    def add(self,v):
        return self + v
    def sub(self,v):
        return self-v
    def mult(self,s):
        return self-s
    def div(self,s):
        return self/s
    def dot(self,v):
        return self*v
    def cross(self,v):
        return Vector3d.CrossProduct(self,v)
    def normalize(self):
        return self.Unitize()
    def rotate(self,radians):
        self.Rotate(radians,CPLANES[-1].ZAxis)
    @classmethod
    def angleBetween(cls,a,b):
        return Vector3d.VectorAngle(a,b,CPLANES[-1])
    @classmethod
    def random2D(cls):
        theta = uniform(0,2*PI)
        return Vector3d(math.cos(theta),math.sin(theta),0)
    @classmethod
    def random3D(cls):
        z = uniform(-1,1)
        theta = uniform(0,2*PI)
        v = PVector.random2D() * (1-z*z)**0.5
        return Vector3d(v.X,v.Y,z)
# basic geometry drawing
def loadImage(fpath):
    "load image"
    pass
def image(img,x,y):
    "position image"
    pass
def arc(x,y,w,h,start,stop,mode='PIE'):
    " construct a elliptic arc "
    if w == h:
        res = Arc(Circle(CPLANES[-1],w),Interval(start,stop))
        spt = res.StartPoint
        ept = res.EndPoint
        cpt = CPLANES[-1].Origin
    else:
        a = w/2
        b = h/2
        pl = Plane(CPLANES[-1])
        pl.Translate(Vector3d(x,y,0))
        cpt = pl.Origin
        spt = pl.PointAt( a*math.cos(start),b*math.sin(start),0 )
        ept = pl.PointAt( a*math.cos(stop),b*math.sin(stop),0 )
        ellip = Ellipse(pl,a,b).ToNurbsCurve()
        t0 = ellip.ClosestPoint(spt)[1]
        t1 = ellip.ClosestPoint(ept)[1]
        res = ellip.Trim(t0,t1)
    if mode == "PIE":
        c1 = LineCurve(ept,cpt)
        c2 = LineCurve(cpt,spt)
        res = Curve.JoinCurves([res,c1,c2])[0]
    Display(res)
def line(x1,y1,x2,y2,z1=0,z2=0):
    " simple line "
    pl = Plane(CPLANES[-1])
    ln = Line(pl.PointAt(x1,y1,z1),pl.PointAt(x2,y2,z2))
    if AUTO_DISPLAY:
        Display(ln)
    return ln

def rect(x1,y1,x2,y2):
    rec = Rectangle3d(CPLANES[-1],Point3d(x1,y1,0),Point3d(x2,y2,0))
    if AUTO_DISPLAY:
        Display(rec)
    return rec
def ellipse(x,y,a,b):
    pl = Plane(CPLANES[-1])
    pl.Translate(Vector3d(x,y,0))
    ell = Ellipse(pl,a,b)
    if AUTO_DISPLAY:
        Display(ell)
    return ell
def text(content,x,y,z=0,height=None):
    " add text to screen "
    te = TextEntity()
    te.Text = content
    te.Plane = CPLANES[-1]
    if height:
        te.TextHeight = height
    te.Translate(Vector3d(CPLANES[-1].PointAt(x,y,z)))
    txtcrvs = Curve.JoinCurves(te.Explode())
    if AUTO_DISPLAY:
        for crv in txtcrvs:
            Display(crv)
    return txtcrvs

### help func?
def constrain_region( pt,geo):
    Max = geo.GetBoundingBox(CPLANES[-1]).Max
    Min = geo.GetBoundingBox(CPLANES[-1]).Min
    pt.X = Rhino.RhinoMath.Clamp(pt.X,Min.X,Max.X)
    pt.Y = Rhino.RhinoMath.Clamp(pt.Y,Min.Y,Max.Y)
    pt.Z = Rhino.RhinoMath.Clamp(pt.Z,Min.Z,Max.Z)
    return pt

### decorator for simplicity
def loop(fn):
    if not isLoop:
        return # should stop timer instead
    global LOOP_COUNT
    LOOP_COUNT += 1
    update_mouse()
    if _MODE == 'overlay' : CPLANES[-1].OriginZ += TORLERENCE
    def wrapped():
        fn()
    return wrapped
def _insureRightOutput(ghenv):
    # slove multiply instance problem
    global GeoOut,ColorOut
    GeoOut = DataTree[object](ghenv.Component.Params.Output[1].VolatileData)
    ColorOut = DataTree[object](ghenv.Component.Params.Output[2].VolatileData)
def initialize(this,name = 'processing',autodisplay = True):
    global isLoop,LOOP_COUNT,_time,AUTO_DISPLAY,CPLANES,VIEWPORT
    _time = time.clock()
    isLoop = True
    VIEWPORT = Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.ActiveViewport
    LOOP_COUNT = 0
    CPLANES = [Plane.WorldXY]
    AUTO_DISPLAY = autodisplay
    _insureRightOutput(this)
    _clearOutput()
    get_class(this)

def noLoop():
    global isLoop
    isLoop = False
def GO(ghenv):
    param = ghenv.Component.Params.Input[0]
    RESET = False
    for data in param.VolatileData.AllData(True):
        RESET = data
    if RESET.Value == True:
        try:
            _setup = ghenv.LocalScope.setup
        except MissingMemberException:
            pass
        initialize(this = ghenv)
        _setup()
    elif isLoop:
        try:
            _draw = ghenv.LocalScope.draw
        except MissingMemberException:
            return
        global LOOP_COUNT
        _insureRightOutput(ghenv)
        LOOP_COUNT += 1
        update_mouse()
        _draw()
