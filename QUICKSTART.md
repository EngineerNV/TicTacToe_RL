# Quick Start Guide

Get up and running with TicTacToe_RL in under 2 minutes!

## 1. Clone the Repository

```bash
git clone https://github.com/EngineerNV/TicTacToe_RL.git
cd TicTacToe_RL
```

## 2. Test the Pre-trained AI

The repository includes a pre-trained AI model (`table.json`). Test it immediately:

```bash
python3 main.py -test table.json 100
```

Expected output:
```
Tic Tac Stats ---> 100 games
Win percent: ~56-65%
Tie percent: ~35-44%
Lose percent: 0.0%
```

## 3. Play Against the AI

Challenge the AI yourself:

```bash
python3 main.py -p table.json
```

- You are 'O' and move first
- Enter row (0-2) and column (0-2) when prompted
- Try to beat the AI! (Good luck! 😄)

## 4. Train Your Own AI

Create a new AI from scratch:

```bash
python3 main.py -train my_ai.json 10000 0.6 0.8
```

This will:
- Train for 10,000 games
- Use learning rate of 0.6
- Use discount factor of 0.8
- Save the trained model to `my_ai.json`

Training takes 1-2 minutes for 10,000 episodes.

## 5. Test Your Trained AI

```bash
python3 main.py -test my_ai.json 100
```

## Next Steps

- Read the full [README.md](README.md) for detailed explanations
- Experiment with different alpha/gamma values
- Try training for 50,000+ episodes for better performance
- Modify the code to implement your own improvements!

## Troubleshooting

**Issue:** `python3: command not found`  
**Solution:** Try `python` instead of `python3`

**Issue:** Game won't accept my input  
**Solution:** Make sure to enter numbers 0-2 only

**Issue:** Want to train longer  
**Solution:** Increase the episode count (e.g., 50000 instead of 10000)

---

Happy Learning! 🎮🤖
