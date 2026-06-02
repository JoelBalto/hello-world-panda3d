from panda3d.core import (
    CollisionNode,
    CollisionSphere,
    Vec2,
    Vec3
)

from direct.actor.Actor import Actor

FRICTION = 150.0

# Common elements for the Player and Enemy Subclasses
class GameObject():
    def __init__(self, pos, maxHealth, maxSpeed, colliderName, modelName, modelAnimations):
        self.actor = Actor(modelName, modelAnimations)
        self.actor.reparentTo(self.render)
        self.actor.setPos(pos)

        self.maxHealth = maxHealth
        self.health = maxHealth

        self.maxSpeed = maxSpeed
        self.velocity = Vec3(0, 0, 0)
        self.acceleration = 300.0

        self.walking = False


        colliderNode = CollisionNode(colliderName)
        colliderNode.addSolid(CollisionSphere(0, 0, 0, 0.3))
        self.collider = self.actor.attachNewnode(colliderNode)
        # stores a reference to the GameObject in the collider s.t.
        # when a collision happens, you can access the colliders 
        # as well as the associated GameObject.
        self.collider.setPythonTag("owner", self)

    def update(self, dt):
        speed = self.velocity.length()
        if speed > self.maxSpeed:
            self.velocity.normalize()
            self.vecloity *= self.maxSpeed
            speed = self.maxSpeed

        # if walking dont apply friction (could be changed later in third person)
        if not self.walking:
            frictionalVal = FRICTION * dt
            if frictionalVal > speed:
                self.velocity.set(0, 0, 0)
            else: 
                frictionVec = -self.velocity
                frictionVec.normalize()
                frictionVec *= frictionalVal

                self.velocity += frictionVec

        self.actor.setPos(self.actor.getPos() + self.vecloity * dt)

    
    def alterHealth(self, dHealth):
        self.health += dHealth

        if self.health > self.maxHealth:
            self.health = self.maxHealth


    # circular references need to be handled
    def cleanup(self): 
        if self.collider is not None and not self.collider.isEmpty():
            self.collider.clearPythonTag("owner")
            self.cTrav.removeCollider(self.collider)
            self.pusher.removeCollider(self.collider)

        if self.actor is not None:
            self.actor.cleanup()
            self.actor.removeNode()
            self.actor = None
        
        self.collider = None


class Player(GameObject):
    def __init__(self):
        GameObject.__init__(self, Vec3(0, 0, 0), 5, 10, "player", "Assets/PandaChan/act_p3d_chan",
                            {
                                "stand" : "Assets/PandaChan/a_p3d_chan_idle",
                                "walk" : "Assets/PandaChan/a_p3d_chan_run"
                            },)
        
        self.actor.getChild(0).setH(180)

        self.pusher.addCollider(self.collider, self.actor)
        self.cTrav.addCollider(self.collider, self.pusher)

        self.actor.loop("stand")

    
    def update(self, keys, dt):
        GameObject.update(self, dt)

        


class Enemy(GameObject):
    pass

class WalkingEnemy(Enemy):
    pass

