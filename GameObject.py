from panda3d.core import (
    CollisionNode,
    CollisionSphere,
    Vec2,
    Vec3
)

from direct.actor.Actor import Actor

from constants import *

import math

# Common elements for the Player and Enemy Subclasses
class GameObject():
    def __init__(self, pos, modelName, modelAnimations, maxHealth, maxSpeed, colliderName):
        self.actor = Actor(modelName, modelAnimations)
        self.actor.reparentTo(render)
        self.actor.setPos(pos)

        self.maxHealth = maxHealth
        self.health = maxHealth

        self.maxSpeed = maxSpeed
        self.velocity = Vec3(0, 0, 0)
        self.acceleration = 300.0

        self.walking = False


        colliderNode = CollisionNode(colliderName)
        colliderNode.addSolid(CollisionSphere(0, 0, 0, 0.3))
        self.collider = self.actor.attachNewNode(colliderNode)
        # stores a reference to the GameObject in the collider s.t.
        # when a collision happens, you can access the colliders 
        # as well as the associated GameObject.
        self.collider.setPythonTag("owner", self)


    def update(self, dt):
        speed = self.velocity.length()
        if speed > self.maxSpeed:
            self.velocity.normalize()
            self.velocity *= self.maxSpeed
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

        self.actor.setPos(self.actor.getPos() + self.velocity * dt)

    
    def alterHealth(self, dHealth):
        self.health += dHealth

        if self.health > self.maxHealth:
            self.health = self.maxHealth

    
    # def 

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
        GameObject.__init__(self, Vec3(0, 0, 0), "Assets/PandaChan/act_p3d_chan",
                            {
                                "stand" : "Assets/PandaChan/a_p3d_chan_idle",
                                "walk"  : "Assets/PandaChan/a_p3d_chan_run"
                            }, 5, 10, "player")
        
        self.actor.getChild(0).setH(180)

        base.pusher.addCollider(self.collider, self.actor)
        base.cTrav.addCollider(self.collider, base.pusher)

        self.actor.loop("stand")

    
    def update(self, keys, dt):
        GameObject.update(self, dt)

        self.walking = False

        if keys[ACTION_UP]:
            self.walking = True
            self.velocity.addY(self.acceleration*dt)
        if keys[ACTION_DOWN]:
            self.walking = True
            self.velocity.addY(-self.acceleration*dt)
        if keys[ACTION_LEFT]:
            self.walking = True
            self.velocity.addX(-self.acceleration*dt)
        if keys[ACTION_RIGHT]:
            self.walking = True
            self.velocity.addX(self.acceleration*dt)
        

        # Run the correct animation based on our current state
        if self.walking:
            standControl = self.actor.getAnimControl("stand")
            if standControl.isPlaying():
                standControl.stop()
            
            walkControl = self.actor.getAnimControl("walk")
            # believe this line is because calling .loop restarts the animation
            # from the first keyframe (could rewrite with panda statemachine class)
            if not walkControl.isPlaying():
                self.actor.loop("walk")
        else:
            standControl = self.actor.getAnimControl("stand")
            if not standControl.isPlaying():
                self.actor.stop("walk")
                self.actor.loop("stand")



class Enemy(GameObject):
    def __init__(self, pos, modelName, modelAnimations, maxHealth, maxSpeed, colliderName) :
        GameObject.__init__(self, pos, modelName, modelAnimations, maxHealth, maxSpeed, colliderName)

        self.scoreValue = 1
    

    def update(self, player, dt):
        GameObject.update(self, dt)

        self.runLogic(player, dt)

        if self.walking:
            walkControl = self.actor.getAnimControl("walk")
            if not walkControl.isPlaying():
                self.actor.loop("walk")
        else:
            spawnControl = self.actor.getAnimControl("spawn")
            if spawnControl is None or not spawnControl.isPlaying():
                attackControl = self.actor.getAnimControl("attack")
                if attackControl is None or not attackControl.isPlaying():
                    standControl = self.actor.getAnimControl("stand")
                    if not standControl.isPlaying():
                        self.actor.loop("stand")

    # probably make a more descriptive name for this in the future
    def runLogic(self, player, dt):
        pass


class WalkingEnemy(Enemy):
    def __init__(self, pos):
        Enemy.__init__(self, pos, "Assets/SimpleEnemy/simpleEnemy",
                       {
                       "stand"  : "Assets/SimpleEnemy/simpleEnemy-stand",
                       "walk"   : "Assets/SimpleEnemy/simpleEnemy-walk",
                       "attack" : "Assets/SimpleEnemy/simpleEnemy-attack",
                       "die"    : "Assets/SimpleEnemy/simpleEnemy-die",
                       "spawn"  : "Assets/SimpleEnemy/simpleEnemy-spawn"
                       },
                       3.0, 7.0, "walkingEnemy")
        
        self.attackDistance = 0.75
        self.acceleration = 100.0
        # a reference vector of where the Actor is facing
        self.yVector = Vec2(0, 1)
    
    # Calculate the vector between the enemy and the player
    # If enemy far from player: use vector to move towards player
    # Else: stop
    # Face the player
    def runLogic(self, player, dt):
        # from my understanding this needs to be changed when we moved to third person
        vectorToPlayer = player.actor.getPos() - self.actor.getPos()
        vectorToPlayer2D = vectorToPlayer.getXy()
        distanceToPlayer = vectorToPlayer2D.length()
        vectorToPlayer2D.normalize()

        heading = self.yVector.signedAngleDeg(vectorToPlayer2D)

        if distanceToPlayer > self.attackDistance*0.9:
            self.walking = True
            vectorToPlayer.setZ(0)
            vectorToPlayer.normalize()
            self.velocity += vectorToPlayer * self.acceleration * dt
        else:
            self.walking = False
            self.velocity.set(0, 0, 0)
        
        self.actor.setH(heading)


class TrapEnemy(Enemy):
    def __init__(self, pos):
        Enemy.__init__(self, pos, "Assets/SlidingTrap/trap",
                       {
                        "stand" : "Assets/SlidingTrap/trap-stand",
                        "walk"  : "Assets/SlidingTrap/trap-walk"
                       }, 
                       100.0, 10.0, "trapEnemy")
        
        base.pusher.addCollider(self.collider, self.actor)
        base.cTrav.addCollider(self.collider, base.pusher)

        self.moveInX = False

        self.moveDirection = 0

        # for ignoring multiple collisions with the player
        self.ignorePlayer = False

    
    def runLogic(self, player, dt):
        if self.moveDirection != 0:
            self.walking = True
            if self.moveInX:
                self.velocity.addX(self.moveDirection * self.acceleration * dt)
            else:
                self.velocity.addY(self.moveDirection * self.acceleration * dt)
        else:
            self.walking = False
            diff = player.actor.getPos() - self.actor.getPos()
            if self.moveInX:
                detector = diff.y
                movement = diff.x
            else:
                detector = diff.x
                movement = diff.y

            if abs(detector) < 0.5:
                self.moveDirection = math.copysign(1, movement)
        

    def alterHealth(self, dHealth):
        # return super().alterHealth(dHealth)
        pass

