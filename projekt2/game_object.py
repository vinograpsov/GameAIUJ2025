#import pygame
import transforms
import singletons

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
        self.components = components
        singletons.GlobalObjects.append(self)

    '''custom destructor, the reason why it is not native function is because python natively do not supports destructors and __del__ or any other kind of native function is NOT a destructor for object'''
    def Destroy(self):
        #it is impossible to trully delete object in python, why why is it so...
        if self in singletons.GlobalObjects:
            singletons.GlobalObjects.remove(self)
        if self.parent:
            self.parent = None #this essentially releases this object from parent
        for child in self.childs:
            child.Destroy()
        for comp in self.components:
            #this weird code calls destructors in components, but only when they are defined bypassing actual inheritance requirement
            #it is stupid, but it is the least convoluted method of utilizing actual destructor
            try:
               comp.Destroy()
               self.components.remove(comp)
            except AttributeError:
                #special destructor not defined
                self.components.remove(comp)

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

    '''returns added component back so it can be easily accesed'''
    def AddComp(self, comp):
        self.components.append(comp)
        comp.gameObject = self
        return comp

    '''can remove specified component or an indexed component'''
    def RemoveComp(self, toRemove):
        if toRemove == type(int):
            if toRemove > components.len():
                print("DebugError: index out of range")
                return
            del self.components[toRemove]
        else:
            try:
               toRemove.Destroy()
               self.components.remove(toRemove)
            except AttributeError:
                #special destructor not defined
                self.components.remove(toRemove)

    '''returns first component of specified type'''
    def GetComp(self, compType):
        for comp in self.components:
            if isinstance(comp, compType):
                return comp
        #debugging
        #print("LogWarning: no " + compType.__class__.__name__ + "found")
        return None

    '''returns all components of specified type'''
    def GetComps(self, compType):
        result = []
        for comp in self.components:
            if isinstance(comp, compType):
                result.append(comp)
        #debugging
        if result == []:
            #print("LogWarning: no " + str(compType) + "found")
            pass
        return result

    '''returns all components of specified type in reversed order'''
    def GetCompsReverse(self, compType):
        result = []
        for i in range(len(self.components) - 1, -1, -1):
            if isinstance(comp, compType):
                result.append(comp)
        #debugging
        if result == []:
            #print("LogWarning: no " + str(compType) + "found")
            pass
        return result

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
        if self.parent != None and self.parent != self: #programmer's stupidity check
            if type(requiredComp) == type(self):
                result.append(parent)
            else:
                for parentComp in self.parent.components:
                    if type(parentComp) == type(requiredComp):
                        result.append(parent)
                        break;
            result.extend(self.parent.GetObjsInParents(requiredComp))
        return result


    #unused for now
    '''deep searches for all components in children of object'''
    def GetCompsInChilds(self, compType):
        result = []
        for child in self.childs:
            if len(child.childs) > 0: #if child of an object has childs itself
                result.extend(child.GetCompsInChilds(compType))
            for comp in child.components:
                if isinstance(comp, compType):
                    result.append(comp)
        return result

    '''deep searches for all components in children of object'''
    def GetCompsInChildsReversed(self, compType):
        result = []
        for i in range(len(self.childs) - 1, -1, -1):
            if len(self.childs[i].childs) > 0: #if child of an object has childs itself
                result.extend(child.GetCompsInChildsReversed(compType))
            for j in range(len(child.components) - 1, -1, -1):
                if isinstance(child.components[j], compType):
                    result.append(child.components[j])
        return result