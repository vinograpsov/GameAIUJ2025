#import pygame
import transforms

def GetObjGlobally(requiredComp):
    pass



class GameObject:
    #transform
    #childs
    #components

    #transform is Transform class, and component is an unspecified class
    def __init__(self, transform, components, parent):
        self.transform = transform
        self.transform.gameObject = self
        self.parent = None
        self.childs = []
        if parent != None:
            self.SetParent(parent)
            #self.transforms.Reparent
        self.components = components

        self.isRemoved = False

    '''destroys entire gameObject once with all it's components'''
    def __delete__(self):
        print('I am deleting')
        for child in self.childs:
            del child
        del self.transform
        for comp in self.components:
            del comp
        del self
    
    def Destroy(self):
        print('I am trying')
        del self

    def Update():
        pass

    #Gets and sets for objects hierarchy

    def SetParent(self, parentObject):
        if self.parent != None: #remove child from earlier parent
            self.parent.childs.remove(self)
        self.parent = parentObject
        self.parent.childs.append(self)

    #currently unused
    def GetParent(self):
        if self.parent != None:
            return self.parent
        return None

    def AddComp(self, comp): #may add several components at once # not yet
        self.components.append(comp)
        comp.gameObject = self

    def RemoveComp(self, toRemove): #can remove specified component or an indexed component
        if toRemove == type(int):
            if toRemove > components.len():
                print("DebugError: index out of range")
                return
            del self.components[toRemove]
        else:
            #also schould be debug but not for now
            self.components.remove(toRemove)

    def GetComps(self, compName):
        result = []
        for comp in self.components:
            if comp.__class__.__name__ == compName:
                result.append(comp)
        #debugging
        if result == []:
            #print("LogWarning: no " + str(compType) + "found")
            pass
        return result

    def GetComp(self, compName):
        for comp in self.components:
            if comp.__class__.__name__ == compName:
                return comp
        #debugging
        #print("LogWarning: no " + comp.__class__.__name__ + "found")
        return None

    '''returns all childs with the specified component, if GameObject is required, returns ALL childs'''
    def GetObjsInChilds(self, requiredComp):
        results = []
        for child in self.childs:
            for childComp in child.components:
                if type(childComp) == type(requiredComp) or type(requiredComp) == type(self): #if it is gameObject it is always true
                    results.append(child)
                    break
            results.extend(child.GetObjsInChilds(requiredComp)) #this recursion allows for deep searching (in childs of childs ect.)
        return results

    def GetObjsInParents(self, requiredComp):
        result = []
        if self.parent != None:
            if type(requiredComp) == type(self):
                result.append(parent)
            else:
                for parentComp in self.parent.components:
                    if type(parentComp) == type(requiredComp):
                        result.append(parent)
                        break;
            result.extend(GetObjsInParents(parent, requiredComp))
        return result

    #made better in future
    #unused for now
    def GetCompsInChilds(self, compName):
        result = []
        for child in self.childs:
            if child.childs: #if child of an object has childs itself
                result.extend(child.GetCompsInChilds(compName))
            for comp in child.components:
                if comp.__class__.__name__ == compName:
                    result.append(comp)
        return result