import pygame
import transforms
import enums
import singletons
#print

pygame.font.init()

class Camera():
    #Window Size is NOT a vector
    def __init__(self, windowSize, clearColor, windowName):
        self.gameObject = None
        self.windowSize = windowSize
        self.clearColor = clearColor
        self.screen = pygame.display.set_mode(self.windowSize)
        pygame.display.set_caption(windowName)

    def Clear(self):
        self.screen.fill(self.clearColor)

    #for now unused, here in case we want game object scale to not be connected to screen resolution
    def WorldToScreen():
        pass

    #general rendering function that combines all for ease of use, others can be used for debug purposes
    def Render(self, renderingComp):
        if type(renderingComp) is Model:
            if renderingComp.renderMode is enums.RenderMode.VERTICES:
                self.RenderVertices(renderingComp)
            elif renderingComp.renderMode is enums.RenderMode.WIREFRAME:
                self.RenderWireframe(renderingComp)
            elif renderingComp.renderMode is enums.RenderMode.POLYGON:
                self.RenderWireframe(renderingComp)
        elif type(renderingComp) is Primitive:
            self.RenderPrimitive(renderingComp)
        #if 

    def RenderPrimitive(self, primitive):
        trans = primitive.gameObject.transform
        trans.SynchGlobals()

        if primitive.type == enums.PrimitiveType.SPHERE:
            drawPos = trans.Reposition(transforms.Vector([0, 0])).data
            drawPos[1] = self.windowSize[1] - drawPos[1]
            pygame.draw.circle(self.screen, primitive.col, drawPos, trans.scale.MaxComponent(), primitive.width)

        if type(primitive) is LinePrimitive:
            startTrans = primitive.startTrans
            endTrans = primitive.endTrans
            startTrans.SynchGlobals()
            endTrans.SynchGlobals()
            startDrawPos = startTrans.pos
            endDrawPos = endTrans.pos
            startDrawPos[1] = self.windowSize[1] - startDrawPos[1]
            endDrawPos[1] = self.windowSize[1] - endDrawPos[1]

            pygame.draw.line(self.screen, primitive.col, startDrawPos, endDrawPos, primitive.width)

    def RenderRawLine(self, startPos, endPos, col, width):
        startDrawPos = startPos.data.copy()
        endDrawPos = endPos.data.copy()
        startDrawPos[1] = self.windowSize[1] - startDrawPos[1]
        endDrawPos[1] = self.windowSize[1] - endDrawPos[1]

        pygame.draw.line(self.screen, col, startDrawPos, endDrawPos, width)

    def RenderRawPoint(self, pos, col, size):
        drawPos = pos.data.copy()
        drawPos[1] = self.windowSize[1] - drawPos[1]
        pygame.draw.circle(self.screen, col, drawPos, size, 0)

    def RenderRawCircle(self, pos, col, size, width):
        drawPos = pos.data.copy()
        drawPos[1] = self.windowSize[1] - drawPos[1]
        pygame.draw.circle(self.screen, col, drawPos, size, width)

    def RenderRawArc(self, pos, col, size, startRot, endRot, width):
        drawPos = pos.data.copy()
        drawPos[1] = self.windowSize[1] - drawPos[1]
        drawSize = size.data.copy()
        drawDimensions = [drawPos[0] - drawSize[0], drawPos[1] - drawSize[1], drawSize[0] * 2, drawSize[1] * 2]
        pygame.draw.arc(self.screen, col, drawDimensions, startRot, endRot, width)

    def RenderVertices(self, model):
        trans = model.gameObject.transform
        trans.SynchGlobals()
        for vertice in model.verts:
            #correction for pygame rendering y in reverse
            drawPos = trans.Reposition(transforms.Vector(vertice)).data
            drawPos[1] = self.windowSize[1] - drawPos[1]
            pygame.draw.circle(self.screen, model.col, drawPos, 2)

    def RenderWireframe(self, model):
        cameraTrans = self.gameObject.transform
        trans = model.gameObject.transform
        trans.SynchGlobals()
        if abs(trans.pos.x()) + trans.scale.x() - abs(cameraTrans.pos.x()) > self.windowSize[0] or abs(trans.pos.y()) + trans.scale.y() - abs(cameraTrans.pos.y()) > self.windowSize[1]: 
            return #for optimization do not render a model that is outside of window
        #coordinate system correction
        for connection in model.edges:
            end1 = trans.Reposition(transforms.Vector(model.verts[connection[0] - 1])).data
            end2 = trans.Reposition(transforms.Vector(model.verts[connection[1] - 1])).data
            end1 = [end1[0] - cameraTrans.pos.x() + self.windowSize[0] / 2, end1[1] - cameraTrans.pos.y() + self.windowSize[1] / 2]
            end2 = [end2[0] - cameraTrans.pos.x() + self.windowSize[0] / 2, end2[1] - cameraTrans.pos.y() + self.windowSize[1] / 2]
            #correct y values to match pygame rendering
            end1[1] = self.windowSize[1] - end1[1]
            end2[1] = self.windowSize[1] - end2[1]
            pygame.draw.line(self.screen, model.col, end1, end2)

    def RenderPolygon(self, model):
        cameraTrans = self.gameObject.transform
        trans = model.gameObject.transform
        trans.SynchGlobals()

        points = []
        #coordinate system correction
        for vertice in model.verts:
            #correction for pygame rendering y in reverse
            drawPos = trans.Reposition(transforms.Vector(vertice)).data
            drawPos[1] = self.windowSize[1] - drawPos[1]
            points.append((drawPos[0], drawPos[1]))
            #pygame.draw.circle(self.screen, model.col, drawPos, 2)
        pygame.draw.polygon(self.screen, model.col, points, 0)


'''empty class for all classes suitable for rendering'''
class RenderObject():

    def __init__(self, col):
        self.gameObject = None
        self.col = col
        singletons.RenderObjects.append(self)

    def Destroy(self):
        singletons.RenderObjects.remove(self)

class Model(RenderObject):

    '''loads model from assets in game's memory'''
    @staticmethod
    def LoadModel(filename):
        bothResults = [] #this will result both vertices and edges in 2 2 dimensional lists
        model = open(filename, "r")
        if model == None:
            print("DebugError: cannot find file " + file)

        Vertices = [] #this contains only vertices
        Edges = [] #this contains egdes (aka connection beetween vertices)
        for line in model:
            currentVert = []
            currentEdge = []
            lineData = line.split()
            #print(lineData[0])

            if lineData[0] == 'v': #vertices
                Vertices.append([float(lineData[1]), float(lineData[2])])
            if lineData[0] == 'l': #edges
                Edges.append([int(lineData[1]), int(lineData[2])])
        bothResults.append(Vertices)
        bothResults.append(Edges)
        model.close()
        return bothResults
    
    def __init__(self, file, col, renderMode):
        super().__init__(col)
        self.file = file
        modelData = self.LoadModel(self.file)
        self.verts = modelData[0]
        self.edges = modelData[1]
        self.renderMode = renderMode

    #Alternate init, would use it but I have no idea how to do this in python
    '''
    def __init__(self, file, col):
        self.gameObject = None;
        self.file = file
        modelData = self.LoadModel()
        #self.verts = modelData[0]
        #self.edges = modelData[1]
        self.col = col
        self.renderMode = enums.RenderMode.WIREFRAME
    '''

class Primitive(RenderObject):

    def __init__(self, type, col, width):
        super().__init__(col)
        self.type = type
        self.width = width

    #Alternate init, would use it but I have no idea how to do this in python
    '''
    def __init__(self, type, col):
        self.gameObject = None
        self.type = type
        self.width = 0 #0 width generates filled primitive
        self.col = col
    '''

class LinePrimitive(Primitive):
       
    def __init__(self, col, width, startTrans, endTrans):
        self.gameObject = None
        self.type = enums.PrimitiveType.LINE
        self.width = width
        self.col = col
        self.startTrans = startTrans
        self.endTrans = endTrans
    
    #Alternate init, would use it but I have no idea how to do this in python
    '''
    def __init__(self, col, startTrans, endTrans):
        self.gameObject = None
        self.type = enums.PrimitiveType.LINE
        self.width = 1
        self.col = col
        self.startTrans = startTrans
        self.endTrans = endTrans
    '''

#UNUSED, but may come in handy at some point
class Text():

    def __init__(self, fontFile, content, col):
        self.gameObject = None
        self.file = fontFile
        self.font = pygame.font.Font(fontFile, 1) # make here some smart function for calculating font size
        self.content = content
        self.col = col
    #def LoadFont

    #as for now text is not rotating
    def Render(self, screen, windowSize, cameraPivot):
        trans = self.gameObject.transform
        trans.SynchGlobals()

        self.font = pygame.font.Font(self.file, int(max(trans.scale)))
        center = transforms.Reposition([0, 0], trans)
        center[1] = windowSize[1] - center[1] - self.font.size(self.content)[1] / 2
        center[0] -= self.font.size(self.content)[0] / 2
        center = [center[0] - cameraPivot[0] + windowSize[0] / 2, center[1] + cameraPivot[1] - windowSize[1] / 2]
        render = self.font.render(self.content, True, self.col)
        screen.blit(render, center)
        pygame.display.update