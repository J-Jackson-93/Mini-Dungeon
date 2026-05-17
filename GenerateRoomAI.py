import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
import os

# ─────────────────────────────────────────────
#  SETTINGS  — tweak these to improve output
# ─────────────────────────────────────────────

LEARNING_RATE  = 50.0
EPOCHS         = 10000       # more epochs = more training; watch the loss flatten out
REG_STRENGTH   = 0.01      # penalises very large weights; keeps model smooth
TEMPERATURE    = 0.8       # sampling: lower (e.g. 0.5) = safer/repetitive,
                           #           higher (e.g. 1.5) = more creative/random
MAX_SEQ_LEN    = 20        # safety cap — stops runaway sequences
WEIGHTS_FILE   = "model_weights.pt"  # trained W is saved/loaded here

# ─────────────────────────────────────────────
#  1. LOAD DATA
#  Each line in the file is one full sentence / statement.
#  We call them "sentences" now, not "words", since tokens are whole words.
# ─────────────────────────────────────────────

# Put each of your 40+ training statements on its own line in this file.
DATA_FILE = "rooms.txt"

with open(DATA_FILE, "r") as f:
    sentences = f.read().splitlines()                        # list of sentence strings
    sentences = [s.strip().lower() for s in sentences if s.strip()]  # clean up

print(f"Loaded {len(sentences)} training sentences")
#print("First 3:", sentences[:3])


# ─────────────────────────────────────────────
#  2. BUILD THE WORD VOCABULARY
#  Flatten all sentences into one big list of words, find the unique set.
#  '.' is still our start/end token (index 0).
# ─────────────────────────────────────────────

# Flatten: [["the cat sat"], ["a dog ran"]] → ["the", "cat", "sat", "a", "dog", "ran"]
all_tokens = [word for sentence in sentences for word in sentence.split()]

vocab = sorted(set(all_tokens))   # unique words, alphabetically sorted
vocab = ["."] + vocab             # prepend the special start/end token

# stoi = "string to int"  (like std::unordered_map<string,int> in C++)
# itos = "int to string"  (the reverse lookup)
stoi = {w: i for i, w in enumerate(vocab)}
itos = {i: w for w, i in stoi.items()}
vocab_size = len(vocab)

#print(f"\nVocab size: {vocab_size} unique words")
#print("First 10 vocab entries:", vocab[:10])


# ═══════════════════════════════════════════════════════════════════
#  PART 1 — STATISTICAL BIGRAM MODEL (counting approach)
# ═══════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────
#  3. BUILD THE BIGRAM COUNT MATRIX
#  N[i][j] = how many times word i was followed by word j.
#  Same structure as before — just words instead of chars.
# ─────────────────────────────────────────────

N = torch.zeros((vocab_size, vocab_size), dtype=torch.int32)

for sentence in sentences:
    # Split sentence into words, then wrap with start/end token
    # e.g. "the cat sat" → [".", "the", "cat", "sat", "."]
    toks = ["."] + sentence.split() + ["."]
    for w1, w2 in zip(toks, toks[1:]):    # zip makes consecutive pairs
        ix1 = stoi[w1]
        ix2 = stoi[w2]
        N[ix1][ix2] += 1

# ─────────────────────────────────────────────
#  4. CONVERT COUNTS TO PROBABILITIES
#  P[i] is the probability distribution over "what comes after char i".
#  We add 1 to every count (model smoothing) to avoid zero probabilities.
# ─────────────────────────────────────────────

P = (N + 1).float()                        # +1 = Laplace / add-one smoothing
P = P / P.sum(dim=1, keepdim=True)         # divide each row by its row sum
                                           # dim=1 means "sum across columns"

# ─────────────────────────────────────────────
#  5. SAMPLE FROM THE STATISTICAL MODEL
# ─────────────────────────────────────────────

def sample_statistical(num_samples=5, seed=None):
    """Generate new word sequences using the bigram probability table."""
    g = torch.Generator()
    if seed is not None:
        g.manual_seed(seed)

    results = []
    for _ in range(num_samples):
        out = []
        ix = 0                             # start at '.' (index 0)
        while True:
            p = P[ix]                      # row = probability dist for this word
            ix = torch.multinomial(p, num_samples=1, replacement=True, generator=g).item()
            if ix == 0:                    # hit the end token → stop
                break
            out.append(itos[ix])
        results.append(" ".join(out))      # join with spaces — it's words now, not chars
    return results

#print("\n── Part 1: Statistical samples ──")
#for s in sample_statistical(5, seed=42):
    #print(" ", s)

# ─────────────────────────────────────────────
#  6. MEASURE QUALITY: NEGATIVE LOG-LIKELIHOOD
#  Lower = better. This is the "loss" for the statistical model.
# ─────────────────────────────────────────────

log_likelihood = 0.0
n_bigrams = 0

for sentence in sentences:
    toks = ["."] + sentence.split() + ["."]
    for w1, w2 in zip(toks, toks[1:]):
        ix1 = stoi[w1]
        ix2 = stoi[w2]
        prob = P[ix1, ix2]
        log_likelihood += torch.log(prob).item()
        n_bigrams += 1

nll_statistical = -log_likelihood / n_bigrams
print(f"\nStatistical model  NLL (avg): {nll_statistical:.4f}")


# ═══════════════════════════════════════════════════════════════════
#  PART 2 — NEURAL NETWORK BIGRAM MODEL
#  Same bigram idea, but we learn a weight matrix W instead of counting.
#  Think of W as a lookup table we improve with gradient descent.
# ═══════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────
#  7. BUILD TRAINING DATASET  (xs = inputs, ys = targets)
#  Each example is one bigram: given word xs[i], predict word ys[i].
# ─────────────────────────────────────────────

xs, ys = [], []

for sentence in sentences:
    toks = ["."] + sentence.split() + ["."]
    for w1, w2 in zip(toks, toks[1:]):
        xs.append(stoi[w1])
        ys.append(stoi[w2])

xs = torch.tensor(xs)   # shape: [num_bigrams]
ys = torch.tensor(ys)   # shape: [num_bigrams]
num_examples = xs.nelement()
print(f"\nNN training set: {num_examples} bigrams")

# ─────────────────────────────────────────────
#  8. INITIALIZE OR LOAD THE WEIGHT MATRIX  W
#  If a saved weights file exists, skip training and load it directly.
#  Otherwise train from scratch and save when done.
#  Think of this like checkpointing in a C++ simulation.
# ─────────────────────────────────────────────

if os.path.exists(WEIGHTS_FILE):
    print(f"\nFound saved weights '{WEIGHTS_FILE}' — skipping training.")
    checkpoint = torch.load(WEIGHTS_FILE)
    W = checkpoint["W"]                    # load the saved matrix
    losses = checkpoint["losses"]          # load the loss history too
    print(f"Loaded W  (shape {W.shape}),  final loss was {losses[-1]:.4f}")

else:
    print(f"\nNo saved weights found — training from scratch.")

    g = torch.Generator().manual_seed(2147483647)
    W = torch.randn((vocab_size, vocab_size), generator=g, requires_grad=True)

    # ─────────────────────────────────────────────
    #  9. TRAINING LOOP
    #  In C++ you'd write the gradient math yourself.
    #  PyTorch does it automatically with .backward().
    # ─────────────────────────────────────────────

    losses = []

    for epoch in range(EPOCHS):

        # ── Forward pass ──────────────────────────────────────────────
        # One-hot encode the inputs: each integer becomes a vector of 0s with a 1.
        xenc = F.one_hot(xs, num_classes=vocab_size).float()  # [N, vocab_size]

        # Matrix multiply to get "logits" (raw unnormalized scores).
        logits = xenc @ W                                     # [N, vocab_size]

        # Softmax turns logits into probabilities; cross_entropy combines
        # softmax + negative log-likelihood in one numerically stable step.
        loss = F.cross_entropy(logits, ys)

        # Regularization: penalize large weights to keep the model smooth.
        loss = loss + REG_STRENGTH * (W ** 2).mean()

        losses.append(loss.item())

        # ── Backward pass (compute gradients) ─────────────────────────
        W.grad = None          # clear old gradients (like resetting accumulators)
        loss.backward()        # PyTorch fills W.grad automatically

        # ── Update weights ────────────────────────────────────────────
        # Gradient descent: move W in the direction that reduces loss.
        with torch.no_grad():  # don't track this operation itself
            W -= LEARNING_RATE * W.grad

        if (epoch + 1) % 100 == 0:
            print(f"  Epoch {epoch+1:>4} / {EPOCHS}   loss = {loss.item():.4f}")

    print(f"\nFinal NN loss: {losses[-1]:.4f}")

    # ── Save weights so next run skips training ────────────────────────
    # torch.save works like writing a struct to a binary file in C++.
    # We detach W so it saves cleanly without gradient metadata.
    torch.save({"W": W.detach(), "losses": losses}, WEIGHTS_FILE)
    print(f"Weights saved to '{WEIGHTS_FILE}'")
    print("(Delete that file any time you want to retrain from scratch.)")


# ─────────────────────────────────────────────
#  10. SAMPLE FROM THE NEURAL NETWORK
#
#  TEMPERATURE controls how "confident" the model is when picking words:
#    Low  (0.5) → always picks the most likely next word → safe but repetitive
#    Med  (0.8) → good balance, recommended starting point
#    High (1.5) → very random, surprising but may be incoherent
#
#  Dividing logits by temperature before softmax is like sharpening or
#  flattening the probability distribution — the same trick used in ChatGPT.
# ─────────────────────────────────────────────

def sample_nn(num_samples=5, seed=2147483647, temperature=TEMPERATURE):
    """Generate new word sequences using the learned weight matrix W."""
    g = torch.Generator().manual_seed(seed)
    results = []

    for _ in range(num_samples):
        out = []
        ix = 0                             # start at '.' token
        for _ in range(MAX_SEQ_LEN):       # cap length — replaces unbounded while True
            xenc = F.one_hot(torch.tensor([ix]), num_classes=vocab_size).float()
            logits = xenc @ W
            logits = logits / temperature  # ← temperature scaling happens here
            p = F.softmax(logits, dim=1)
            ix = torch.multinomial(p, num_samples=1, replacement=True, generator=g).item()
            if ix == 0:                    # hit end token → stop early
                break
            out.append(itos[ix])
        results.append(" ".join(out))
    return results

print("\n── Part 2: Neural network samples ──")
for s in sample_nn(5):
    print(" ", s)