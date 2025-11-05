import pygame
import transforms
import enums
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
    def ToCameraSpace():
        pass

    #general rendering function that combines all for ease of use, others can be used for debug purposes
    def Render(self, renderingComp):
        pass
        #if 

    def RenderPrimitive(self, primitive):
        trans = primitive.gameObject.transform
        trans.SynchGlobals()

        if enums.PrimitiveType.CIRCLE:
            #for some reason rendering here does not require to flip y position
            drawPos = trans.Reposition(transforms.Vector([0, 0])).data
            #drawPos = trans.pos.data
            drawPos[1] = self.windowSize[1] - drawPos[1]
            pygame.draw.circle(self.screen, primitive.col, drawPos, trans.scale.MaxComponent(), primitive.width)

        if enums.PrimitiveType.LINE:
            pass

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


class Model():

    '''loads model from assets in game's memory'''
    def LoadModel(self):
        bothResults = [] #this will result both vertices and edges in 2 2 dimensional lists
        model = open(self.file, "r")
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

        #print(bothResults)

        model.close()
        self.verts = Vertices
        self.edges = Edges
        return bothResults
    
    #still mess, repair later
    def __init__(self, file, col):
        self.gameObject = None;
        self.file = file
        modelData = self.LoadModel()
        #self.verts = modelData[0]
        #self.edges = modelData[1]
        self.col = col


#LATER ADD ENUMS
class Primitive():

    def __init__(self, type, col, width):
        self.gameObject = None
        self.type = type
        self.width = width
        self.col = col

    def __init__(self, type, col):
        self.gameObject = None
        self.type = type
        self.width = 0 #0 width generates filled primitive
        self.col = col

class LinePrimitive(Primitive):
       
    def __init__(self, col, startTrans, endTrans):
        self.gameObject = None
        self.type = enums.PrimitiveType.LINE
        self.width = 1 #0 width generates filled primitive
        self.col = col
        self.startTrans = startTrans
        self.endTrans = endTrans

    def __init__(self, col, width, startTrans, endTrans):
        self.gameObject = None
        self.type = enums.PrimitiveType.LINE
        self.width = width
        self.col = col
        self.startTrans = startTrans
        self.endTrans = endTrans

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
        #DownLeft = transforms.Reposition([-1, -1], trans)
        #upRight = transforms.Reposition([1, 1], trans)
        #DownLeft[1] = windowSize[1] - DownLeft[1]
        #upRight[1] = windowSize[1] - upRight[1]
        center = transforms.Reposition([0, 0], trans)
        center[1] = windowSize[1] - center[1] - self.font.size(self.content)[1] / 2
        center[0] -= self.font.size(self.content)[0] / 2
        center = [center[0] - cameraPivot[0] + windowSize[0] / 2, center[1] + cameraPivot[1] - windowSize[1] / 2]
        render = self.font.render(self.content, True, self.col)
        screen.blit(render, center)
        pygame.display.update