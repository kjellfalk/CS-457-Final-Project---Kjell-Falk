Student Name: Kjell Falk

Date: 2026-09-20

Course: CS 457 - Computer Networks

Target Server Domain: server.falk.edu

1.1 Game Overview

Chosen Game: Symmetrical Mastermind

Player Capacity: 2

Game Summary: 

	The classic codebreaking game, Mastermind, but modified so that both players must decode their opponents code string over a series turns, rather than having a player be codemaker and another be codebreaker;

1.2 Core Game Rules & Win/Draw Conditions

Turn Mechanics: 

	At start of round, each player will arrange a four-character code string from a set of six letters {A,E,I,O,U,Y}. A valid code string may include repeat letters;
	
	Turn 1 begins after both players have arranged and committed their code strings;
	
	During a turn, each player will arrange their initial "guess" at their opponent's code string;
	
	From start of Turn 2 through end of round:
	
		Each player will receive a feedback code string that reveals incomplete information about how close their last guess resembled their opponent's code string;
		
	Turns continue until at least one player has successfully guessed their opponent's code string, finishing the round;
	
	When a round finishes, any player who successfully guesses their opponent's code on the winning turn receives one match point. If both players correctly guess their opponent's code on the same turn, both players receive one match point;

Victory Condition:

	A player wins when they have accumulated a score of at least 3 AND have a greater score than their opponent;

	If both players reach or exceed 3 points simultaneously, the match continues into sudden-death rounds. During sudden-death, the first person to establish a positive point difference over their opponent wins the match;

Draw/Tie Condition:

	A round is tied when both players correctly guess their opponent's code on the same turn. Both players receive one match point for a tied round. A tied match continues into sudden-death rounds until one player establishes a positive point difference;

GitHub Public Repository Link:

	https://github.com/kjellfalk/CS-457-Final-Project---Kjell-Falk