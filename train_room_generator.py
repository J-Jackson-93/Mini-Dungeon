import torch
import torch.nn.functional as F
import os

from room_generator_model import Room_Generator_Model, save_model, generate

# ─────────────────────────────────────────────
#  SETTINGS
# ─────────────────────────────────────────────

DATA_FILE = "rooms.txt"
WEIGHTS_FILE = "model_weights.pt"

BLOCK_SIZE = 7  # words of context the model looks back
EMBED_DIM = 1 + (BLOCK_SIZE * 3)  # size of each word's embedding vector
input_dim = BLOCK_SIZE * EMBED_DIM
HIDDEN_SIZE = 4 * input_dim # neurons in the hidden layer
EPOCHS = max(10000, HIDDEN_SIZE * 50)
LEARNING_RATE = 0.1
REG_STRENGTH = 0.001

# ─────────────────────────────────────────────
#  1. LOAD DATA
# ─────────────────────────────────────────────

with open(DATA_FILE, "r") as f:
    sentences = f.read().splitlines()
    sentences = [s.strip().lower() for s in sentences if s.strip()]

print(f"Loaded {len(sentences)} training sentences")

# ─────────────────────────────────────────────
#  2. BUILD VOCABULARY
# ─────────────────────────────────────────────

all_tokens = [word for sentence in sentences for word in sentence.split()]
vocab = ["."] + sorted(set(all_tokens))
stoi = {w: i for i, w in enumerate(vocab)}

print(f"Vocab size: {len(vocab)} unique words")

# ─────────────────────────────────────────────
#  3. BUILD DATASET (sliding context window)
# ─────────────────────────────────────────────

xs, ys = [], []

for sentence in sentences:
    context = [0] * BLOCK_SIZE
    for word in sentence.split() + ["."]:
        ix = stoi[word]
        xs.append(context)
        ys.append(ix)
        context = context[1:] + [ix]

xs = torch.tensor(xs)
ys = torch.tensor(ys)
num_examples = xs.shape[0]
print(f"Training examples: {num_examples}")

# ─────────────────────────────────────────────
#  4. INIT MODEL  (or skip if weights exist)
# ─────────────────────────────────────────────

if os.path.exists(WEIGHTS_FILE):
    print(f"\nWeights already exist at '{WEIGHTS_FILE}'.")
    print("Delete that file and re-run to train from scratch.")
    print("Running generate() on the existing model instead...\n")

    from room_generator_model import load_model

    model, losses = load_model(WEIGHTS_FILE)

else:
    print(f"\nTraining from scratch...")

    model = Room_Generator_Model(vocab, BLOCK_SIZE, EMBED_DIM, HIDDEN_SIZE)
    params = model.parameters()
    print(f"Total parameters: {model.num_params()}")

    # ─────────────────────────────────────────────
    #  5. TRAINING LOOP
    # ─────────────────────────────────────────────

    losses = []

    for epoch in range(EPOCHS):

        # Forward
        logits = model.forward(xs)
        loss = F.cross_entropy(logits, ys)
        loss = loss + REG_STRENGTH * sum((p ** 2).mean() for p in [model.W1, model.W2])
        losses.append(loss.item())

        # Backward
        for p in params:
            p.grad = None
        loss.backward()

        # Update — learning rate decays halfway through
        lr = LEARNING_RATE if epoch < EPOCHS // 2 else LEARNING_RATE / 10
        with torch.no_grad():
            for p in params:
                p -= lr * p.grad

        if (epoch + 1) % (EPOCHS // 10) == 0:
            print(f"  Epoch {epoch + 1:>6} / {EPOCHS}   loss = {loss.item():.4f}")

    print(f"\nFinal loss: {losses[-1]:.4f}")
    save_model(model, losses, WEIGHTS_FILE)

# ─────────────────────────────────────────────
#  6. SAMPLE FROM THE TRAINED MODEL
# ─────────────────────────────────────────────

print("\n── Generated samples ──")
for sentence in generate(model, num_samples=10, temperature=0.8):
    print(" ", sentence)
