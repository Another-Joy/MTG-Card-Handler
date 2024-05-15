class BOT:
    def __init__(self) -> None:
        self.X = 0
        self.Y = 0
        self.Xoff =
        self.Xstep =
        self.Yoff =
        self.Ystep =
        return
        
    def moveArm(self, X, Y):
        #TODO: move handler from self.X, self.Y to X, Y.
        self.X = X
        self.Y = Y
        return
    
    def grab(self):
        #TODO: get depth from DB based on how many cards the slot has
        #TODO: lower handler to position
        #TODO: Use suction.
        #TODO: lift handler.
        return
    
    def drop(self):
        #TODO: get depth from DB based on how many cards the slot has
        #TODO: lower handler to position slightly above
        #TODO: Drop suction.
        #TODO: lift handler.
        return
    
    def move(self, X1, Y1, X2, Y2):
        self.moveArm(X1, Y1)
        self.grab()
        self.moveArm(X2, Y2)
        self.drop()
        return
