# import farm
from constants import (
    KEYBINDS, 
    ACTION_UP, 
    ACTION_DOWN, 
    ACTION_LEFT, 
    ACTION_RIGHT, 
    ACTION_SHOOT
)

from panda3d.core import (
    AmbientLight,
    CollisionHandlerPusher,
    CollisionNode,
    CollisionSphere,
    CollisionTraverser,
    CollisionTube,
    DirectionalLight,
    Vec3,
    Vec4, 
    WindowProperties, 
    loadPrcFileData
)

# so Panda3D can look beyond root directory into Assets to find ../texture/
loadPrcFileData("", "model-path Assets")

from direct.showbase.ShowBaseGlobal import globalClock
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor

class Game(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        # initialize window and edit size
        properties = WindowProperties()
        properties.setSize(1280, 720)
        self.win.requestProperties(properties)

        # disable mouse-based camera-control
        self.disableMouse()
        # nodes work similar to unity, same in terms of position

        # loader is a globally accessible variable which loads objects
        # doesnt use '.egg' suffix to allow Panda to detect in case of .bam / .egg
        self.environment = self.loader.loadModel("Assets/Environment/environment")
        # wont show until you paraent it to somethin that is already in the scene graph
        # in this case attach to root which is known as render
        self.environment.reparentTo(self.render)

        # actors are animated models
        # you pass into the constructor the file for the model itself
        # then you pass in a dict {animation names, animation files} 
        self.tempActor = Actor("Assets/PandaChan/act_p3d_chan", {"walk" : "Assets/PandaChan/a_p3d_chan_run"})
        self.tempActor.reparentTo(self.render)

        # models usually arent single nodes and tend to have a child node containing
        # the models themselves. Choose to rotate model themselves instead of NodePath
        # to avoid any potential future complications with rotations
        self.tempActor.getChild(0).setH(180)
        # as opposed to "play" which runs through it once
        self.tempActor.loop("walk")

        # to get a topdown feel
        self.camera.setPos(0 ,0 ,32)
        self.camera.setP(-90)

        # many lights, rn js directional/ambient/pointlight/spotlight/etc
        # note that light slows down rendering, half-dozen is ezpz, one hundred is bad
        # Ambient Light: uniformly distributed everywhere in the world, usually never alone
        ambientLight = AmbientLight("ambient light")
        ambientLight.setColor(Vec4(0.2, 0.2 ,0.2 ,1))

        # compared to reparentTo, attachNewNode returns a NodePath when attach node
        self.ambientLightNodePath = self.render.attachNewNode(ambientLight)
        # specifically pass in NodePath, not the node
        self.render.setLight(self.ambientLightNodePath)

        mainLight = DirectionalLight("main light")
        self.mainLightNodePath = self.render.attachNewNode(mainLight)
        self.mainLightNodePath.setHpr(45, -45, 0)
        self.render.setLight(self.mainLightNodePath)

        # Panda3D provides a built-in shader-generator
        self.render.setShaderAuto()

        # input dict (better than an enum since native string acceptance and avoid .value)
        # using this recommendation from tutorial for more sophistication
        self.keyMap = {
            ACTION_UP : False,
            ACTION_DOWN : False,
            ACTION_LEFT : False,
            ACTION_RIGHT : False,
            ACTION_SHOOT : False
        }

        for key, action in KEYBINDS.items():   
            # "to register our interest in an event, tell the DirectObject
            # to 'accept' that event" (done by passing in a method to call when it occurs)
            self.accept(key, self.updateKeyMap, [action, True])
            # process is same for interest in release, add -up
            self.accept(f"{key}-up", self.updateKeyMap, [action, False])

        # use the task manager to run an update loop
        self.updateTask = self.taskMgr.add(self.update, "update")

        # default variable for a traverser, a checker of physics objects for collisions
        self.cTrav = CollisionTraverser()
        # a pusher (prevents solid objects from intersecting other solids), can also send collision events
        self.pusher = CollisionHandlerPusher()
        colliderNode = CollisionNode("player")
        colliderNode.addSolid(CollisionSphere(0, 0, 0, 0.3))
        collider = self.tempActor.attachNewNode(colliderNode)
        # uncomment to show the collider of the player
        # collider.show()
        # effectively tells the traverser and pusher should collide with other objects
        self.pusher.addCollider(collider, self.tempActor)
        self.cTrav.addCollider(collider, self.pusher)

        # Limits the scene to two-dimensional, by allowing responses of the pusher
        # to be restricted to only the horizontal
        self.pusher.setHorizontal(True)

        # this section should be able to be easily refactored
        wallSolid = CollisionTube(-8.0, 0, 0, 8.0, 0, 0, 0.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = self.render.attachNewNode(wallNode)
        wall.setY(8.0)

        wallSolid = CollisionTube(-8.0, 0, 0, 8.0, 0, 0, 0.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = self.render.attachNewNode(wallNode)
        wall.setY(-8.0)

        wallSolid = CollisionTube(0, -8.0, 0, 0, 8.0, 0, 0.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = self.render.attachNewNode(wallNode)
        wall.setX(8.0)

        wallSolid = CollisionTube(0, -8.0, 0, 0, 8.0, 0, 0.2)
        wallNode = CollisionNode("wall")
        wallNode.addSolid(wallSolid)
        wall = self.render.attachNewNode(wallNode)
        wall.setX(-8.0)

    
    # the method of which we are calling when we accept input
    def updateKeyMap(self, controlName, controlState):
        self.keyMap[controlName] = controlState
        # print(controlName, "set to", controlState)

    # returning task.cont says "run task again", otherwise it would only run once
    def update(self, task):
        # from my understading, deltatime equivalent
        dt = globalClock.getDt()

        # interesting method of doing movement, if some key is pressed,
        # use dt to calculate distance, then apply
        if self.keyMap[ACTION_UP]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(0, 5.0*dt, 0))
        if self.keyMap[ACTION_DOWN]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(0, -5.0*dt, 0))
        if self.keyMap[ACTION_LEFT]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(-5.0*dt, 0, 0))
        if self.keyMap[ACTION_RIGHT]:
            self.tempActor.setPos(self.tempActor.getPos() + Vec3(5.0*dt, 0, 0))
        if self.keyMap[ACTION_SHOOT]:
            print("Shot!")
        
        return task.cont



if __name__ == "__main__":
    game = Game()
    game.run()

