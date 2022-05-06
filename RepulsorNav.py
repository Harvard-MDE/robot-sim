'''Python class that implements Repulsive Obstacle 
Avoidance and Goal Seeking Navigation'''

import math
import pdb

#Define gravitational constants
G_GOAL = 1.0
G_OBS = 1.0 

#Define global functions
def NormaliseVector(v):
    '''Return the normalised vector'''
    d = math.sqrt(v[0]*v[0] + v[1]*v[1])
    return [v[0]/d, v[1]/d]

def ObstacleForce(p1, p2, rSafe):
    '''Determine the gravitational force between two
    points. Returns a vector'''
    d = math.sqrt(float(math.pow((p1[0] - p2[0]),2) + math.pow((p1[1] - p2[1]),2))) # distance
    if d <= rSafe: # if the obstacle is closer than rSafe, make sure dSqr is a valid value
        dSqr = 0.000001 # if inside safety radius, dSqr should be very very small
    else:
        dSqr = math.pow((d - rSafe),2) # Gravity force is maximum when d = rSafe

    F = G_OBS/dSqr # Repulsive force proportional to 1/dSqr
    unit_vec = [(p1[0] - p2[0])/d, (p1[1] - p2[1])/d]
    f_vec = (unit_vec[0] * F, unit_vec[1] * F) 
    return f_vec, unit_vec

class RepulsorNav:
    def __init__(self, p1, p2, rSafe = 2):
        '''Create the instance of this class'''
        self.ownPos = p1
        self.goalPos = p2
        self.safetyRadius = rSafe # introduce a safety radius to cater to robot actual dimensions
        self.obstacles = [] # create an empty list of obstacles

    def __str__(self):
        '''default print function'''
        return "Default Print not defined yet"

    def SetOwnPos(self, p):
        '''Update own position'''
        self.ownPos = p


    def UpdateObstacles(self, obs):
        '''Update the list of obstacles in sight'''
        self.obstacles = obs

    def Navigate(self, edgeholding = False):
        '''Determine the best route to goal and
        return this direction vector
        By default, the navigator will not do edgeholding '''
        
        steerVec = [0,0]
        x1, y1 = self.ownPos
        if edgeholding == False: # If we are not edgeholding, use the vector to goal as the main direction
            steerVec = [self.goalPos[0] - x1, self.goalPos[1] - y1]  #calc direct vector to goal

        if len(self.obstacles) > 0: #if there are obstacles in 'sight'
            for obs in self.obstacles: #iterate through all obstacles
                obsForce, unit_vec = ObstacleForce(self.ownPos, obs, self.safetyRadius)
                #print("OwnPos {op}, Obstacle {ob}, Unit Vec {uv}, ObsForce {obf}".format(op=self.ownPos,ob=obs,uv = unit_vec, obf=obsForce))

                steerVec = [steerVec[0] + obsForce[0] , steerVec[1] + obsForce[1]]
        
        v = NormaliseVector(steerVec) # output the normailised recommended vector
        c1 = ((math.pi/2) - math.atan2(v[1], v[0]))%(2 * math.pi) # Course to Steer
        
        return v,c1

    def SetGoal(self, newGoal):
        '''Go to a new goal'''
        self.goalPos = newGoal


if __name__ == "__main__":
    
    op = [0,0]
    gp = [10,10]

    r1 = RepulsorNav(op,gp)

    obstacles = [[6,2]]#, [6, 4.2], [6,12], [17,8]]

    r1.UpdateObstacles(obstacles)

    r1.Navigate()









    

