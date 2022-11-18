from stockfish import Stockfish



class ChessAI_S():
    def __init__(self):
        self.stockfish = Stockfish(path = 'Lib/stockfish_15_win_x64_avx2/stockfish_15_x64_avx2.exe')
        self.stockfish.set_depth(10);
        self.stockfish.set_skill_level(20)
    def getBestMove(self):
        print(self.stockfish.get_best_move())








