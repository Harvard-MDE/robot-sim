'''Sprite class implements basic Sprite functionality
for display in a PyGame Arena'''

import pygame, math
from pygame.locals import *
import RepulsorNav as rpn # Goal Seeking and Obstacle Avoidance Class
import time

# Define constants

HDG_MARKER_LENGTH = 40 # length of heading marker to plot on screen
ROBOT_SAFETY_RADIUS = 50 # Safety circle around the robot
RANGE_REDUCTION = 4 # If trapped, reduce the detection range to avoid getting lost
#Define global functions

def PlotBearing(pos1, pos2):
        '''Returns the bearing in degrees of pos2 [x2, y2]
        from pos1 [x1, y1] on an equal scale plot'''
        dx = float(pos2[0] - pos1[0])
        dy = float(pos2[1] - pos1[1])
        b = math.atan2(dy,dx)

        if b <=0:
            final = math.pi/2 + abs(b)
        elif b > 0:
            final = (math.pi/2 - b)%(math.pi * 2)

        return final

def FindCentreBearing(hdg, rec):
    '''Given two bearing lines, find the central bearing'''

    h = (math.sin(hdg), math.cos(hdg))
    r = (math.sin(rec), math.cos(rec))

    f = (h[0] + r[0], h[1] + r[1])

    theta = math.atan2(f[1], f[0])

    if theta <=0:
        final = (math.pi/2 + abs(theta))
    elif theta > 0:
        final = (math.pi/2 - theta)%(math.pi * 2)   
    return final


def Distance2D(p1, p2):
    '''Returns the 2D distance between two points'''
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    d = math.sqrt(math.pow(x1 - x2,2) + math.pow(y1 - y2,2))
    return d

class Sprite:
    '''Parent class for all plotting objects'''
    def __init__(self, ID, pos, radius = 20, lineThick = 3, color = "Black"):
        self.ID = ID
        self.pos = pos
        self.color = color
        self.radius = radius
        self.lineThickness = lineThick
        self.hasImage = False # By default, sprites are not associated with any image

    def __str__(self):
        txt = "Sprite, ID={i}, Pos={p}, color = {c}".format(i=self.ID,p=self.pos, c= self.color)
        return txt
    
    def SetImage(self, imgFile):
        '''Assign an image to this sprite'''
        try:
            self.image = pygame.image.load(imgFile) # Load an image
            self.hasImage = True
        except:
            print("Error Loading Image for Sprite ID {i}".format(i=self.ID))
            raise
            self.hasImage = False
    
    def GetPos(self):
        '''Returns the position tuple of the Sprite'''
        return self.pos

    def XY2WH(self, cx, cy, plotXY):
        '''Convert a normal XY coordinate tuple to Pygame's WH so that
        it fits nicely on the Corrdinate Axis'''

        return (cx + plotXY[0], cy - plotXY[1])

    def SetPos(self, pos):
        '''Set a new position for this sprite'''
        self.pos = pos

    def Update(self, obstacles):
        '''If anything needs to be updated at regular intervals,
        put it here...
        Arguments: counter value, counter increment delay (milliseconds)
        Dead sprites usually dont need to update anything at all.
        Active Sprites can overload this Update() method and do whatever they
        need to at each update.'''

        pass

    def PygameDraw(self, screen, hdg = 0):
        '''Draw itself onto the screen argument. Child Classes can implement
        overloaded PygameDraw() methods for more complex drawing operations
        
        Hdg (degrees) argument is used to rotate the image CCW before drawing '''
        cx, cy = screen.get_height()//2, screen.get_width()//2

        drawPos = self.XY2WH(cx, cy, self.pos)
        
        if self.hasImage: # Draw the sprite's image
            
            img = pygame.transform.rotate(self.image, -hdg)
            imgSize = img.get_size()[0]//2
            screen.blit(img, ((self.XY2WH(cx,cy,self.pos))[0] - imgSize, 
                (self.XY2WH(cx, cy, self.pos)[1] - imgSize))) # draw image

        else: # Draw a circle shape

            pygame.draw.circle(screen, 
                    pygame.Color(self.color), 
                    drawPos, 
                    self.radius, 
                    self.lineThickness)

#Define Robot Class

class Robot(Sprite): # 
    def __init__(self, ID, pos, goal = (0,0), color = pygame.Color("Black")):
        '''Create instance of robot class'''
        #Initialise attirbutes of Parent Sprite Classs
        Sprite.__init__(self, ID, pos, color)
        self.SetHeading(math.radians(0)) # Internal to this class, heading is in radians 
        self.stepTaken = False # just a flag to help with keyboard control see pygame.K_UP

        self.trail = [] # A record of robot's position
        self.TIME_COUNT = 0 # counter to keep track of life time elapsed

    def __str__(self):
        t = "Robot Pos {p1}, Going to {g}, heading {c}, speed {s}".format(p1 = self.pos, g = self.repulsorNav.goalPos, c = math.degrees(self.hdg), s = self.spd)

        return t

    def PygameDraw(self, screen):
        '''Overloaded function of the Parent Sprite class
        PygameDraw() Function. The robot needs to draw all its 
        extra items like heading marker, visible obstacles etc. and then 
        finally call the parent class PygameDraw function to draw its
        body/ image'''

        # Draw the heading marker
        cx, cy = screen.get_height()//2, screen.get_width()//2
        p1 = self.XY2WH(cx, cy, self.marker[0])
        p2 = self.XY2WH(cx, cy, self.marker[1])
        pygame.draw.lines(screen, pygame.Color("Black"), False, (p1, p2)) # Robot's heading marker

        #TO DO Draw the Robot's Trail
        for pos in self.trail:
            if self.runMode == "Finished":
                pygame.draw.circle(screen, pygame.Color("Green"), self.XY2WH(cx, cy, pos), 2, 1)
            else:
                pygame.draw.circle(screen, pygame.Color(self.color), self.XY2WH(cx, cy, pos), 2, 1)


        # Draw the robot's body by calling PygameDraw in the parent class
        super().PygameDraw(screen, math.degrees(self.hdg)) # pygame takes rotation angle in degrees
   
    def SetSpeed(self, speed):
        '''Set the robot's speed'''
        self.spd = speed

    def SetHeading(self, hdg):
        '''Set the robot's heading. Heading Agument is in radians!!!'''
        self.hdg = hdg
        self.ResetHeadingMarker()

    def ResetHeadingMarker(self):
        '''Recalculate the heading marker'''
        
        self.marker = (self.pos, (self.pos[0] + HDG_MARKER_LENGTH * math.sin(self.hdg), self.pos[1] + HDG_MARKER_LENGTH * math.cos(self.hdg)))

    def ResetStepFlag(self):
        '''Flip the value of stepTaken Flag'''
        self.stepTaken = False
       
    def GetHeadingMarker(self):
        '''Returns the heading marker tuple'''
        return self.marker

    def SetSensor(self, r1, a1):
        '''Set the parameters of the Robot's Sensor'''
        self.sensor_range = r1
        self.sensor_angle = a1
    
    def StepForward(self, nSteps = 1):
        '''The robot steps 
        forward nSteps at a time'''
        sx = self.pos[0] + nSteps * self.spd * math.sin(self.hdg)
        sy = self.pos[1] + nSteps * self.spd * math.cos(self.hdg)
        self.pos = (int(sx),int(sy))
        #print("Step Taken:{s}".format(s=self.pos))
        self.stepTaken = True
        self.ResetHeadingMarker()
        self.trail.append(self.pos) # add position to trail

    def StepBackward(self, n):
        '''The robot steps backwards'''
        self.spd *= -1 # reverse the speed
        self.StepForward(nSteps = n) # take a step forward (with negative speed)
        self.spd *= -1 # set the speed to its orginal value
        self.stepTaken = True
        self.ResetHeadingMarker()
        self.trail.append(self.pos) # add position to trail

    def ResetStepFlag(self):
        '''Flip the value of stepTaken Flag'''
        self.stepTaken = False
    
    def TurnRight(self, angle = 10):
        '''The robot turns clockwise'''
        self.hdg = (self.hdg + 0.01745 * angle) % (math.pi * 2) # default is turn 5 degrees at a time
        self.ResetHeadingMarker()
    
    def TurnLeft(self, angle = 10):
        ''' turns anti-clockwise'''
        self.TurnRight(angle * -1) # turn right, but with a negative angle
        self.ResetHeadingMarker()

    def ToggleAutoControl(self):
        '''Set whether the robot will navigate in Automatic mode or manual control'''
        self.autoControl = not(self.autoControl)


#Define GoalSeeker Class

class GoalSeeker(Robot):
    def __init__(self, ID, pos, goal = (0,0), color = pygame.Color("Black")):
        Robot.__init__(self, ID, pos, color)
        self.size = ROBOT_SAFETY_RADIUS
        self.goal = goal
        self.repulsorNav = rpn.RepulsorNav(self.pos, self.goal,
                rSafe = self.size) # create a repulsor algorithm
        self.visible_obstacles = [] # list of currently visible obstacles
        self.runMode = "GoalSeek" # Start off in goal seeking mode
        self.runState = "Clear" # Start off with no obstacles in "sight"
        self.autoControl = False # Run in manual mode
        self.trapHistory = [] # List of flags showing if last ten steps were 'trapped' or not
        self.maxEdgeHoldTime = 150 # How long to continue edheholding if goal is not reached

    def __str__(self):
        '''Default print'''
        return "Not coded yet"

    def PygameDraw(self, screen):
        '''Overloaded function of parent class. Draw only the factors affecting
        the Repulsor Algorithm'''
        
        cx, cy = screen.get_height()//2, screen.get_width()//2

        # Draw visible obstacles
        for obs in self.visible_obstacles:
            pygame.draw.circle(screen, pygame.Color("Red"), self.XY2WH(cx, cy, obs.pos), 20, 5)
         
        #Call parent class and draw robot related everything else
        super().PygameDraw(screen)

    def SetGoal(self, goal):
        '''Set the Goal for the seeking algorithm'''
        self.goal = goal
        self.repulsorNav.SetGoal(self.goal)
        self.runMode = "GoalSeek" # Start Seeking the goal
        self.trapHistory = [] # Clear the trap history

    def ClearOfTrap(self):
        '''Check if the robot is clear of trap'''
         
        f1 = self.trapTrack > 3 * self.size # Walked enough from trap
        f2 = abs(PlotBearing(self.pos, self.goal) - self.goalBrgFromTrap)%360 < math.radians(40) # returned to goal line
        f3 = Distance2D(self.goal, self.pos) < self.goalDistFromTrap # Closer to goal than at trap point
        f4 = not(f3) and len(self.visible_obstacles) == 0 # We cleared the trap from the opposite side
        
        # print('ClearOfTrap:', f1, f2, f3)

        if (f1 * f2 * f3) or f4: # If all three conditions are met.....
            self.trapHistory = [] # we are no longer trapped
            return True
        else:
            return False

    def IsTrapped(self):
        '''Returns True if the robot thinks it is trapped behind an obstacle(s)'''
    
        if len(self.trail) > 30: # Go at least 20 steps before chekcing if trapped or not
            d =  Distance2D(self.trail[-1], self.trail[-20]) 
            if d < self.size: #if robot is not making headway
        
                self.trapHistory.append(True) # record the 'trap'
                if len(self.trapHistory) > 10: # start checking after 10 steps
                    # print(self.trapHistory)
                    self.trapHistory.pop(0) # get rid of the earliest flag
                
                    sum = 0
                    #print(self.trapHistory)
                    for i in range(len(self.trapHistory)):
                        sum += self.trapHistory[i]
                    if sum > 5: # if more than 5 entries are 'true'
                        #we are trapped. Record the necessary trap parameters and return True
                        self.trapPoint = self.pos
                        self.goalBrgFromTrap = PlotBearing(self.trapPoint, self.goal)
                        self.goalDistFromTrap = Distance2D(self.pos, self.goal)
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
   
    def Update(self, obstacles):
  
        '''Update the robot's status'''
        
        # TODO NOT: Print the current state
        # print("ID:{id}, Goal:{g}, Run Mode:{r}, Run State:{s}".format(id = self.ID, g = self.goal, r= self.runMode, s = self.runState))
        # #Refresh the visible obstacles
        
        self.visible_obstacles = [] # Clear the list of visible obstacles for this robot
       
        '''Normally we run in simple "GoalSeek" mode. If the Robot gets trapped,
        then it records the Goal Vector Lien and changes to "EdgeHold" mode.
        It does not return to "GoalSeek" until it re-joins the original Goal Vector Line'''

        if Distance2D(self.pos, self.goal) >= self.size/2: # Robot still needs to go closer to goal
            
            if self.runMode == "GoalSeek":
                # print("IsTrapped returned:", self.IsTrapped())
                if self.IsTrapped():# Trapped in Goal Seek Mode
                    self.runState = "Trapped" # Record the change of Running State 
                    v1,v2 = self.pos, self.goal
                    self.savedGoalVector = rpn.NormaliseVector([v1[0] - v2[0],v1[1] - v2[1]])
                    self.runMode = "EdgeHold" #Change to Edge Holding Mode of Operation
                    self.trapTrack = 0 # Reset the length of track stepped record from this trap
                    self.trapTime = time.time() # record the time when the robot started Edgeholding
                    self.trapHistory = [] # Reset the trap history
                    self.Update(obstacles) # REDO this step after setting mode to EdgeHold

                else: # In GoalSeek Mode, but not trapped
                    #Update visible obstacles
                    for obs in obstacles:
                        if Distance2D(self.pos, obs.pos) <= self.sensor_range: # if the robot can 'see' the obstacle
                            dOG = Distance2D(obs.pos, self.goal)
                            dG = Distance2D(self.pos, self.goal)
                            if dOG <= dG: # if the obstacle is closer to the goal than the robot...
                                self.visible_obstacles.append(obs)


                    if len(self.visible_obstacles) > 0:
                        self.runState = "Evade"
                    else:
                        self.runState = "Clear"
       

                    #Update Navigator and Calculate Recommended Steering Vector
                    self.repulsorNav.SetOwnPos(self.pos) # update own position to navigation algorithm
                    self.repulsorNav.UpdateObstacles([i.pos for i in self.visible_obstacles])
                    recVector, recHdg = self.repulsorNav.Navigate() # Recommended vector to steer
                    self.SetHeading(FindCentreBearing(self.hdg, recHdg)) #Turn halfway to recommended heading

            elif self.runMode == "EdgeHold":
                
                #Update visble Obstacles. Reduce sensor range to cut out excess clutter

                if time.time() - self.trapTime > self.maxEdgeHoldTime:
                    self.runMode = "GoalSeek" # After two minutes of Edgeholding, and we have still not rached the goal, try "GoalSeeking"again

                for obs in obstacles:
      
                    if Distance2D(self.pos, obs.pos) <= self.sensor_range/RANGE_REDUCTION:
                        self.visible_obstacles.append(obs)
                
                #Steer by Repulsion without including the goal direction
                #Determine the current goal vector
                #if CurGoalVec X savedGoalVec is almost = 0, we areback on the line
                #so, change back to "GoalSeek" Mode

                if self.ClearOfTrap(): # Clear of Trap. Go back to Goalseeking mode
                    self.runMode = "GoalSeek"
                    self.Update(obstacles) # REDO this step after setting mode to GoalSeek

                else: # Still in trap, continue edgeholding

                    self.trapTrack += self.spd # increment the track stepped from this trap                    
                    self.repulsorNav.SetOwnPos(self.pos) # update own position to navigation algorithm
            
                    if len(self.visible_obstacles) > 0:
                        self.repulsorNav.UpdateObstacles([i.pos for i in self.visible_obstacles])
                        recVector, recHdg = self.repulsorNav.Navigate(edgeholding = True) # Tell navigator we are edgeholding
                        self.SetHeading(recHdg + math.pi/2.1) # turn right and head out of trap
                   
        else: # we are close enough to the goal to stop
            self.runMode = "Finished"
            self.hdg = 0
            self.spd = 0
                
        #If in AUTO control, Step Forward

        if self.autoControl == True:
            self.StepForward() 
      
