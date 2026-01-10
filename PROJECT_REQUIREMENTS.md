# Senet Project Requirements

## Game Summary
- Ancient Egyptian race game (Kendall's Rules) on a 30-tile S-shaped board (3 rows × 10 columns).
- Each player has 7 pieces placed alternately on tiles 1–14; objective is to move all own pieces off-board first.
- Movement distance determined by throwing four binary sticks: sum of dark faces gives 1–4 steps; four light faces counts as 5 steps. Players may move any own piece by the rolled distance.
- Landing on an opponent swaps positions; if no legal move exists the turn is skipped.
- Special tiles (15, 26–30) enforce the House of Rebirth/Happiness/Water/Three Truths/Re-Atoum/Horus rules for rebirth, mandatory stops, forced returns, and exit permissions.

## Project Deliverables
1. **Problem Representation**
   - Define the game as a search problem: explicit state structure, transition function, cost model, start state, and terminal state. Implement in the chosen language.
2. **Board Rendering**
   - Provide a readable print/display function for the 30-tile board showing both players' pieces.
3. **Chance Modeling**
   - Derive and document the probability of each possible stick throw outcome (1–5 steps) and implement a function to sample or enumerate throws accordingly.
4. **Game Loop**
   - Alternate between human and computer turns; each turn begins with a stick throw that determines available moves.
5. **Computer Player**
   - Use the Expectiminimax algorithm with configurable search depth to choose the computer's move given the current roll. Always evaluate heuristics from the computer's perspective.
6. **Diagnostics Mode**
   - When enabled at game start, output the search trace: node counts, evaluated heuristic values, node types (max/min/chance), and the final chosen action.

## Strategy Expectations
- Develop heuristics that balance advancing own pieces, avoiding swaps, and blocking the opponent. Play-testing to refine strategies can earn bonus credit.

## Administrative Notes
- Group size: 3–5 students; register by 2026-01-08. Submission/interviews on 2025-01-17.
- Deliverables: printed report (no AI-generated text), PDF submission, and a single text file containing the full documented code (named with students' Arabic names and departments).
- Include a photo of the initial design meeting notes and list each student’s contributions in the report.
- Plagiarism or AI-generated code results in penalties (automatic −3 points or zero for severe cases); cite any borrowed code explicitly.
