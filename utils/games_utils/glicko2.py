from datetime import datetime
import math

from utils.games_utils import typeracer_dboperations

class Player:
    #System constant, τ (works best between 0.3 and 0.12) lower reduces impact of upsets
    tau = 0.5
    #Default rating for an unrated player
    default_rating = 1500
    #Default Rating Deviation, is 95% confident that the player's rating is between [rating - (RD * 2), rating + (RD * 2)]
    default_RD = 350
    #Default volatility of a player, indicates degree of expected fluctuation in the player's rating
    default_vol = 0.06

    def __init__(self, user):
        self.connection = typeracer_dboperations.connection()
        #Initialize the information of a player to their database data or default values
        self.userid = typeracer_dboperations.get_rating(self.connection, user.id)[0][1] if typeracer_dboperations.get_rating(self.connection, user.id) != "Nope" else user.id
        self.name = typeracer_dboperations.get_rating(self.connection, user.id)[0][2] if typeracer_dboperations.get_rating(self.connection, user.id) != "Nope" else user.name
        self.rating = typeracer_dboperations.get_rating(self.connection, user.id)[0][3] if typeracer_dboperations.get_rating(self.connection, user.id) != "Nope" else Player.default_rating
        self.RD = typeracer_dboperations.get_rating(self.connection, user.id)[0][4] if typeracer_dboperations.get_rating(self.connection, user.id) != "Nope" else Player.default_RD
        self.vol = typeracer_dboperations.get_rating(self.connection, user.id)[0][5] if typeracer_dboperations.get_rating(self.connection, user.id) != "Nope" else Player.default_vol
        self.matchcount = typeracer_dboperations.get_rating(self.connection, user.id)[0][6] if typeracer_dboperations.get_rating(self.connection, user.id) != "Nope" else 0
        self.lastmatch = typeracer_dboperations.get_rating(self.connection, user.id)[0][7] if typeracer_dboperations.get_rating(self.connection, user.id) != "Nope" else datetime.now().strftime("%Y-%m-%d %X")
        #If player isn't in database, add them to the database
        if typeracer_dboperations.get_rating(self.connection, user.id) == "Nope":
            typeracer_dboperations.insert_rating(self.connection, self.userid, self.name, self.rating, self.RD, self.vol, self.matchcount, self.lastmatch)

    #Updates both players' ratings in the database and return a message based on the result
    def update_players(member1, member2, result) -> str:
        player1 = Player(member1)
        player2 = Player(member2)
        player1_current_rating, player2_current_rating = player1.rating, player2.rating
        player1_current_RD, player2_current_RD = player1.RD, player2.RD
        player1.update_rating([player2_current_rating], [player2_current_RD], [result])
        player2.update_rating([player1_current_rating], [player1_current_RD], [1 - result])
        player1_new_rating, player2_new_rating = player1.rating, player2.rating
        typeracer_dboperations.update_rating(player1.connection, player1.rating, player1.RD, player1.vol, player1.matchcount, player1.lastmatch, player1.userid)
        typeracer_dboperations.update_rating(player2.connection, player2.rating, player2.RD, player2.vol, player2.matchcount, player2.lastmatch, player2.userid)
        if result == 1:
            win_message = f"{member1.mention} wins the match!\n\
                            {member1.display_name}'s rating change: **{round(player1_current_rating)} -> {round(player1_new_rating)}** (+{round(player1_new_rating) - round(player1_current_rating)})\n\
                            {member2.display_name}'s rating change: **{round(player2_current_rating)} -> {round(player2_new_rating)}** ({round(player2_new_rating) - round(player2_current_rating)})"
        if result == 0:
            win_message = f"{member2.mention} wins the match!\n\
                            {member2.display_name}'s rating change: **{round(player2_current_rating)} -> {round(player2_new_rating)}** (+{round(player2_new_rating) - round(player2_current_rating)})\n\
                            {member1.display_name}'s rating change: **{round(player1_current_rating)} -> {round(player1_new_rating)}** ({round(player1_new_rating) - round(player1_current_rating)})"
        if result == 0.5:
            win_message = f"The match is a tie!\n\
                            {member1.display_name}'s rating change: **{round(player1_current_rating)} -> {round(player1_new_rating)}** (+{round(player1_new_rating) - round(player1_current_rating)})\n\
                            {member2.display_name}'s rating change: **{round(player2_current_rating)} -> {round(player2_new_rating)}** ({round(player2_new_rating) - round(player2_current_rating)})"
        return win_message

    def update_rating(self, rating_list, RD_list, result_list):
        #Convert the player's rating and RD to the Glicko-2 scale
        self.rating = (self.rating - 1500) / 173.7178
        self.RD = self.RD / 173.7178
        #Convert opponents' ratings and RDs to the Glicko-2 scale
        rating_list = [(x - 1500) / 173.7178 for x in rating_list]
        RD_list = [x / 173.7178 for x in RD_list]
        #Computes the quantity v, the estimated variance of player's rating based on results (1 for the moment)
        v = self.v(rating_list, RD_list)
        #New volatility, σ′
        self.vol = self.new_volatility(rating_list, RD_list, result_list, v)
        #Currently increases the RD by 5 for each day of inactivity (inactivity starts at 2 days)
        current_time = datetime.strptime(datetime.now().strftime("%Y-%m-%d %X"), "%Y-%m-%d %X")
        day = 24 * 3600
        time_elapsed = (current_time - datetime.strptime(self.lastmatch, "%Y-%m-%d %X")).total_seconds() / day
        inactivity_RD = time_elapsed * 5
        if time_elapsed * day < (2 * day):
            inactivity_RD == 0
        self.RD += inactivity_RD
        #Update the RD to new pre-rating period value
        self.RD = math.sqrt((self.RD ** 2) + (self.vol ** 2))
        #New RD
        self.RD = 1 / math.sqrt((1 / (self.RD ** 2)) + (1 / v))
        #New rating
        sum = 0
        for x in range(len(rating_list)):
            sum += self.g(RD_list[x]) * (result_list[x] - self.E(rating_list[x], RD_list[x]))
        self.rating += (self.RD ** 2) * sum
        #Convert rating and RD back to original scale
        self.rating = (self.rating * 173.7178) + 1500
        self.RD = self.RD * 173.7178
        #Update the player's match count
        self.matchcount += len(rating_list)
        #Update the player's last match date
        self.lastmatch = datetime.now().strftime("%Y-%m-%d %X")

    #Computes v
    def v(self, rating_list, RD_list):
        sum = 0
        for x in range(len(rating_list)):
            E = self.E(rating_list[x], RD_list[x])
            sum += (self.g(RD_list[x]) ** 2) * E * (1 - E)
        return 1 / sum

    #Glicko-2 g(φ)
    def g(self, RD):
        return 1 / math.sqrt(1 + (3 * (RD ** 2)) / (math.pi ** 2))

    #Glicko-2 E(μ,μⱼ,φⱼ)
    def E(self, rating, RD):
        return 1 / (1 + math.exp(-1 * self.g(RD) * (self.rating - rating)))

    #Computes the quantity Δ, the estimated improvement in rating (compares old rating to performance rating based on results)
    def delta(self, rating_list, RD_list, result_list, v):
        sum = 0
        for x in range(len(rating_list)):
            sum += self.g(RD_list[x]) * (result_list[x] - self.E(rating_list[x], RD_list[x]))
        return v * sum
    
    #New volatility
    def new_volatility(self, rating_list, RD_list, result_list, v):
        #1 Let a = ln(σ^2), and define f(x), define ε = 0.000001
        a = math.log(self.vol ** 2)
        def f(x, delta, v, a, rating):
            ex = math.exp(x)
            numerator = ex * (delta ** 2 - rating ** 2 - v - ex)
            denominator = 2 * ((rating ** 2 + v + ex) ** 2)
            return  (numerator / denominator) - ((x - a) / (Player.tau ** 2))
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
        #4 While |B - A| > ε, carry out the following steps
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
        #5 Once |B - A| <= ε, set σ′ <- e^A/2
        return math.exp(A / 2)