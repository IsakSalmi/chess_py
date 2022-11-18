from stockfish import Stockfish



class StockFish():
    def __init__(self):
        stockfish = Stockfish(path = 'Lib/stockfish_15_win_x64_avx2/stockfish_15_x64_avx2.exe')
        stockfish.set_depth(10);
        stockfish.set_skill_level(20)
        








