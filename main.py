from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    Vec4, 
    WindowProperties, 
    loadPrcFileData
)

loadPrcFileData("", "model-path Assets")

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
        # models 
        self.tempActor.getChild(0).setH(180)
        self.tempActor.loop("walk")

        self.camera.setPos(0 ,0 ,32)
        self.camera.setP(-90)

        ambientLight = AmbientLight("ambient light")
        ambientLight.setColor(Vec4(0.2, 0.2 ,0.2 ,1))

        self.ambientLightNodePath = self.render.attachNewNode(ambientLight)
        self.render.setLight(self.ambientLightNodePath)

        mainLight = DirectionalLight("main light")
        self.mainLightNodePath = self.render.attachNewNode(mainLight)
        self.mainLightNodePath.setHpr(45, -45, 0)


game = Game()
game.run()