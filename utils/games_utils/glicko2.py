from datetime import datetime
import math

from utils.games_utils import typeracer_dboperations

class Player:

    tau = 0.5
    default_rating = 1500
    default_RD = 350
    default_vol = 0.06

    def __init__(self, user):
        self.connection = typeracer_dboperations.connection()
        self.userid = typeracer_dboperations.get_rating(self.connection, user.id)[0][1] if typeracer_dboperations.get_rating(self.connection, user.id) != "Nope" else user.id
        self.name = typeracer_dboperations.get_rating(self.connection, user.id)[0][2] if typeracer_dboperations.get_rating(self.connection, user.id) != "Nope" else user.name
        self.rating = typeracer_dboperations.get_rating(self.connection, user.id)[0][3] if typeracer_dboperations.get_rating(self.connection, user.id) != "Nope" else Player.default_rating
        self.RD = typeracer_dboperations.get_rating(self.connection, user.id)[0][4] if typeracer_dboperations.get_rating(self.connection, user.id) != "Nope" else Player.default_RD
        self.vol = typeracer_dboperations.get_rating(self.connection, user.id)[0][5] if typeracer_dboperations.get_rating(self.connection, user.id) != "Nope" else Player.default_vol
        self.matchcount = typeracer_dboperations.get_rating(self.connection, user.id)[0][6] if typeracer_dboperations.get_rating(self.connection, user.id) != "Nope" else 0
        self.lastmatch = typeracer_dboperations.get_rating(self.connection, user.id)[0][7] if typeracer_dboperations.get_rating(self.connection, user.id) != "Nope" else datetime.now().strftime("%Y-%m-%d %X")
        if typeracer_dboperations.get_rating(self.connection, user.id) == "Nope":
            typeracer_dboperations.insert_rating(self.connection, self.userid, self.name, self.rating, self.RD, self.vol, self.matchcount, self.lastmatch)

    def update_rating(self, rating_list, RD_list, result_list):
        self.convert_rating(self.rating)
        self.convert_RD(self.RD)
        rating_list = [(x - 1500) / 173.7178 for x in rating_list]
        RD_list = [x / 173.7178 for x in RD_list]
        v = self.v(rating_list, RD_list)
        self.vol = self.new_volatility(rating_list, RD_list, result_list, v)
        self.RD = math.sqrt((self.RD ** 2) + (self.vol ** 2))
        self.RD = 1 / math.sqrt((1 / (self.RD ** 2)) + (1 / v))
        tempSum = 0
        for x in range(len(rating_list)):
            tempSum += self.g(RD_list[x]) * (result_list[x] - self.E(rating_list[x], RD_list[x]))
        self.rating += (self.RD ** 2) * tempSum
        self.convert_back_rating()
        self.convert_back_RD()
        self.matchcount += 1
        self.lastmatch = datetime.now().strftime("%Y-%m-%d %X")

    def convert_rating(self, rating):
        self.rating = (rating - 1500) / 173.7178

    def convert_back_rating(self):
        self.rating = (self.rating * 173.7178) + 1500

    def convert_RD(self, RD):
        self.RD = RD / 173.7178

    def convert_back_RD(self):
        self.RD = self.RD * 173.7178

    def v(self, rating_list, RD_list):
        tempSum = 0
        for x in range(len(rating_list)):
            tempE = self.E(rating_list[x], RD_list[x])
            tempSum += (self.g(RD_list[x]) ** 2) * tempE * (1 - tempE)
        return 1 / tempSum

    def g(self, RD):
        return 1 / math.sqrt(1 + (3 * (RD ** 2)) / (math.pi ** 2))

    def E(self, rating, RD):
        return 1 / (1 + math.exp(-1 * self.g(RD) * (self.rating - rating)))
       
    def delta(self, rating_list, RD_list, result_list, v):
        tempSum = 0
        for x in range(len(rating_list)):
            tempSum += self.g(RD_list[x]) * (result_list[x] - self.E(rating_list[x], RD_list[x]))
        return v * tempSum
              
    def new_volatility(self, rating_list, RD_list, result_list, v):
        #1 Let a = ln(sigma^2), and define f(x), define epsilon = 0.000001
        a = math.log(self.vol ** 2)
        def f(x, delta, v, a, rating):
            ex = math.exp(x)
            num1 = ex * (delta ** 2 - rating ** 2 - v - ex)
            denom1 = 2 * ((rating ** 2 + v + ex)**2)
            return  (num1 / denom1) - ((x - a) / (Player.tau ** 2))
        epsilon = 0.000001
        #2 Set the initial values of the iterative algorithm
        A = a
        B = None
        delta = self.delta(rating_list, RD_list, result_list, v)
        if (delta ** 2) > (self.RD ** 2) + v:
            B = math.log(delta ** 2 - self.RD ** 2 - v)
        else:        
            k = 1
            while f(a - k * math.sqrt(Player.tau ** 2), delta, v, a, self.rating) < 0:
                k = k + 1
            B = a - k * math.sqrt(Player.tau ** 2)
        #3 Let fa = f(A) and fb = f(B)
        fA = f(A, delta, v, a, self.rating)
        fB = f(B, delta, v, a, self.rating)
        #4 While |B - A| > epsilon, carry out the following steps.
        while math.fabs(B - A) > epsilon:
          #a
          C = A + ((A - B) * fA) / (fB - fA)
          fC = f(C, delta, v, a, self.rating)
          #b
          if fC * fB < 0:
            A = B
            fA = fB
          else:
            fA = fA / 2
          #c
          B = C
          fB = fC
        #5 Once |B - A| <= epsilon, set sigma' <- e^A/2
        return math.exp(A / 2)