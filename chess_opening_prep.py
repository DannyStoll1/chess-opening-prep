#! /usr/bin/env python

import chess
import chess.polyglot
import chess.svg
import chess.engine
from pixcat import Image

import os

import random

import yaml
import os
import os.path
import logging

from pathlib import Path

logger = logging.getLogger(__name__)


def load_config(config_file):
    with open(config_file) as stream:
        try:
            CONFIG = yaml.safe_load(stream)
        except Exception as e:
            logger.error("There appears to be a syntax problem with your config.yml")
            raise e
    return CONFIG

def missing_file_msg(description, filename, type='error'):
    return (f"Unable to locate {description} {filename}. "
            f"Have you set your config.yml properly?")

class OpeningPrep():
    def __init__(self,
            color,
            my_book,
            opp_book,
            engine = "",
            line = "",
            ):
        """
        color: 'w' or 'b', indicating the player's color
        my_book: path to player's book file
        opp_book: path to opponent's book file
        engine: path to engine for postgame analysis
        line: line to starting position; use for focused study.
        """

        self.board = chess.Board()

        try:
            self.player = chess.polyglot.open_reader(my_book)
        except FileNotFoundError as e:
            logger.error(missing_file_msg("player book", my_book))
            raise e
        try:
            self.opponent = chess.polyglot.open_reader(opp_book)
        except FileNotFoundError as e:
            logger.error(missing_file_msg("opponent book", opp_book))
            raise e
        if engine:
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(f"./{engine}")
            except FileNotFoundError as e:
                logger.warning(missing_file_msg("engine", engine))
                self.engine = None

        self.color = chess.WHITE if color=='w' else chess.BLACK
        self.last_move = None

        for san in line:
            self.last_move = self.board.parse_san(san)
            self.board.push(self.last_move)

    def line_to_san(self, moves):
        san_line = ""
        for move in moves[:-1]:
            san_line += self.board.san(move) + ' '
            self.board.push(move)

        san_line += self.board.san(moves[-1])

        for _ in moves[:-1]:
            self.board.pop()

        return san_line

    def analyse(self, depth=20, lines=3, threshold=0.4):
        if self.engine is None:
            return None, None, []

        infos = self.engine.analyse(
                self.board,
                chess.engine.Limit(depth=depth),
                multipv = lines)

        info = infos[0]
        
        self.engine.quit()
        eval = info["score"].white().score()/100
        pvs = [self.line_to_san(i["pv"])
                for i in infos]
        evals = [i["score"].white().score()/100
                for i in infos]
        if abs(eval) < 1:
            top_moves = [info["pv"][0]] + [
                    i["pv"][0] for i in infos[1:]
                    if abs(i["score"].white().score()/100 - eval) < threshold]
        else:
            top_moves = [info["pv"][0]] + [
                    i["pv"][0] for i in infos[1:]
                    if abs(i["score"].white().score()/eval) > 70]
        return evals, pvs, top_moves


    def get_hint(self):
        best = self.player.get(self.board).move
        return str(best)[:2]

    def input_move(self):
        input_str = input("Enter your move: ")
        if input_str in ['h', 'hint']:
            self.get_hint()
            return None
        try:
            move = self.board.parse_san(input_str)
        except ValueError:
            print("Invalid move.")
            return None

        return move

    def display(self, arrows=[]):
        if os.environ['TERM'] == 'xterm-kitty':
            svg = chess.svg.board(
                    self.board,
                    orientation = self.color,
                    lastmove = self.last_move,
                    arrows = arrows)
            from cairosvg import svg2png
            im = svg2png(svg)
            Image(im).show()
        else:
            print(self.board)

    def conclude_game(self):
        if self.engine is None:
            self.display()
            return

        evals, pvs, top_moves = self.analyse()

        print(f"\nEngine evaluation: {evals[0]}")

        for eval,pv in zip(evals,pvs):
            print(f"\n{eval} {pv}")
        

        colors = ['green', 'yellow', 'red', 'blue']
        arrows = [
                chess.svg.Arrow(m.from_square, m.to_square, color=colors[i])
                for i,m in enumerate(top_moves)]
        self.display(arrows=arrows)

    def do_player_move(self):
        self.display()
        moves = {entry.move: entry.weight
                for entry in
                self.player.find_all(self.board, minimum_weight=0)}

        if not moves:
            print("End of line reached!")
            self.conclude_game()
            return False

        while True:
            move = self.input_move()
            if move is None:
                continue
            elif move not in moves.keys() or moves[move] == 0:
                response = input("Move appears to be suboptimal.\nPlay anyway? [yes|no|hint|undo|reset|quit] ")
            else:
                break

            if response in ['y', 'yes']:
                break
            elif response in ['q', 'quit', 'exit']:
                return False
            elif response in ['h', 'hint']:
                print(self.get_hint())
            elif response in ['u', 'undo', 'back']:
                self.board.pop()
                self.board.pop()
                print(self.board)
            elif response in ['r', 'reset']:
                self.board.reset()

        print(f"You played {self.board.san(move)}.")
        self.board.push(move)
        self.last_move = move
        return True

    def do_opponent_move(self):
        try:
            move = self.opponent.weighted_choice(self.board).move
        except IndexError:
            print("End of opponent's book reached!")
            self.conclude_game()
            return False
        print(f"Opponent played {self.board.san(move)}.")
        self.board.push(move)
        self.last_move = move
        return True

    def play(self):
        playing = True
        if self.color == self.board.turn:
            playing = self.do_player_move()
        while playing:
            if self.do_opponent_move():
                playing = self.do_player_move()
            else:
                playing = False

    def close(self):
        for name in {'player', 'opponent', 'engine'} & self.__dict__.keys():
            attr = self.__dict__[name]
            if attr:
                attr.close()

    def __del__(self):
        self.close()

def main():
    config = load_config("config.yml")

    if config['use_lines']:
        lines = config['lines']
        line = random.choice(lines).split(' ')
    else:
        line = ""



    color = input("Select your color [w|b]: ")
    try:
        prep = OpeningPrep(color,
            my_book = config['my_book'],
            opp_book = config['opp_book'],
            engine = config['engine'],
            line = line)
    except FileNotFoundError:
        return

    prep.play()

if __name__ == "__main__":
    main()
