# import farm
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

from GameObject import *

# so Panda3D can look beyond root directory into Assets to find ../texture/
loadPrcFileData("", "model-path Assets")

from direct.showbase.ShowBaseGlobal import globalClock
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor

class Game(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

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

        self.updateTask = self.taskMgr.add(self.update, "update")

        # default variable for a traverser, a checker of physics objects for collisions
        self.cTrav = CollisionTraverser()
        # a pusher (prevents solid objects from intersecting other solids), can also send collision events
        self.pusher = CollisionHandlerPusher()

        # Limits the scene to two-dimensional, by allowing responses of the pusher
        # to be restricted to only the horizontal
        self.pusher.setHorizontal(True)

        # when an object enters a collision, emit an event of the pattern:
        # <from_obj>-into-<into_obj> ex "player-into-wall" (names are from GameObject.py and here)
        self.pusher.add_in_pattern("%fn-into-%in")

        self.accept("trapEnemy-into-wall", self.stopTrap)
        self.accept("trapEnemy-into-trapEnemy", self.stopTrap)
        self.accept("trapEnemy-into-player", self.trapCollision)
        self.accept("trapEnemy-into-walkingEnemy", self.trapCollision)

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

        # Game Objects
        self.player = Player()
        self.tempEnemy = WalkingEnemy(Vec3(5, 0, 0))
        self.tempTrap = TrapEnemy(Vec3(-2, 7, 0))


    
    # the method of which we are calling when we accept input
    def updateKeyMap(self, controlName, controlState):
        self.keyMap[controlName] = controlState
        # print(controlName, "set to", controlState)

    # returning task.cont says "run task again", otherwise it would only run once
    def update(self, task):
        # from my understading, deltatime equivalent
        dt = globalClock.getDt()

        self.player.update(self.keyMap, dt)

        self.tempEnemy.update(self.player, dt)

        self.tempTrap.update(self.player, dt)
        
        return task.cont
    

    def stopTrap(self, entry):
        collider = entry.getFromNodePath()
        if collider.hasPythonTag("owner"):
            trap = collider.getPythonTag("owner")
            trap.moveDirection = 0
            trap.ignorePlayer = False

    
    def trapCollision(self, entry):
        collider = entry.getFromNodePath()
        if collider.hasPythonTag("owner"):
            trap = collider.getPythonTag("owner")
            
            if trap.moveDirection == 0: 
                return
        
            collider = entry.getIntoNodePath()
            if collider.hasPythonTag("owner"):
                obj = collider.getPythonTag("owner")
                if isinstance(obj, Player):
                    if not trap.ignorePlayer:
                        obj.alterHealth(-1)
                        trap.ignorePlayer = True
                else:
                    obj.alterHealth(-10)



if __name__ == "__main__":
    game = Game()
    game.run()

