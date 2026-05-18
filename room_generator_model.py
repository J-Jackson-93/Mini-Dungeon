"""
Import from any other script like this:
    from room_generator_model import Room_Generator_Model, load_model, generate
"""

import torch
import torch.nn.functional as F
import os


#The Model Class

class Room_Generator_Model:
    def __init__(self, vocab, block_size, embed_dim, hidden_size):
        """
        Constructor — sets up a fresh untrained model.

        Args:
            vocab       : list of words, with '.' at index 0
            block_size  : how many words back the model looks
            embed_dim   : size of each word's embedding vector
            hidden_size : number of neurons in the hidden layer
        """
        self.vocab      = vocab
        self.block_size = block_size
        self.embed_dim  = embed_dim
        self.hidden_size = hidden_size
        self.vocab_size = len(vocab)

        # stoi / itos are the word ↔ index lookup tables.
        # Same as std::unordered_map<string, int> in C++.
        self.stoi = {w: i for i, w in enumerate(vocab)}
        self.itos = {i: w for w, i in self.stoi.items()}

        # Initialise all weight tensors
        g = torch.Generator().manual_seed(2147483647)
        self.C  = torch.randn((self.vocab_size,            embed_dim),   generator=g, requires_grad=True)
        self.W1 = torch.randn((block_size * embed_dim,     hidden_size), generator=g, requires_grad=True)
        self.b1 = torch.zeros(hidden_size,                               requires_grad=True)
        self.W2 = torch.randn((hidden_size,                self.vocab_size), generator=g, requires_grad=True)
        self.b2 = torch.zeros(self.vocab_size,                           requires_grad=True)

    def parameters(self):
        """Return all trainable tensors as a list — like iterating model.parameters() in PyTorch nn."""
        return [self.C, self.W1, self.b1, self.W2, self.b2]

    def forward(self, xs):
        """
        Run a batch of context windows through the network.
        Returns raw logits (one score per vocab word, per example).

        Args:
            xs : LongTensor of shape [batch_size, block_size]
        Returns:
            logits : Tensor of shape [batch_size, vocab_size]
        """
        batch_size = xs.shape[0]

        # Step 1: look up the embedding vector for every word in every context
        emb = self.C[xs]                          # [batch, block_size, embed_dim]

        # Step 2: flatten — treat all context embeddings as one long input vector
        emb_flat = emb.view(batch_size, -1)       # [batch, block_size * embed_dim]

        # Step 3: hidden layer with tanh activation
        h = torch.tanh(emb_flat @ self.W1 + self.b1)  # [batch, hidden_size]

        # Step 4: output layer — one score per vocab word
        logits = h @ self.W2 + self.b2            # [batch, vocab_size]

        return logits

    def num_params(self):
        """Total number of learnable floats in the model."""
        return sum(p.nelement() for p in self.parameters())


# ─────────────────────────────────────────────
#  SAVE  —  writes the model to a .pt file
#
#  We save everything needed to reconstruct the model:
#  the weights AND the vocab/settings, so load_model()
#  doesn't need a separate config file.
# ─────────────────────────────────────────────

def save_model(model, losses, filepath):
    """
    Save a trained MakemoreModel and its loss history to disk.

    Args:
        model    : a MakemoreModel instance
        losses   : list of loss values from training
        filepath : path to save to, e.g. "model_weights.pt"
    """
    torch.save({
        # Weights
        "C":          model.C.detach(),
        "W1":         model.W1.detach(),
        "b1":         model.b1.detach(),
        "W2":         model.W2.detach(),
        "b2":         model.b2.detach(),
        # Config — saved so load_model can rebuild the object exactly
        "vocab":      model.vocab,
        "block_size": model.block_size,
        "embed_dim":  model.embed_dim,
        "hidden_size":model.hidden_size,
        # Training history
        "losses":     losses,
    }, filepath)
    print(f"Model saved to '{filepath}'")


# ─────────────────────────────────────────────
#  LOAD  —  rebuilds a model from a .pt file
# ─────────────────────────────────────────────

def load_model(filepath):
    """
    Load a saved MakemoreModel from disk.

    Returns:
        model  : MakemoreModel with weights restored
        losses : list of training losses from when it was saved

    Usage:
        from makemore_model import load_model, generate
        model, losses = load_model("model_weights.pt")
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No weights file found at '{filepath}'. Run train.py first.")

    checkpoint = torch.load(filepath)

    # Reconstruct the model object with the saved config
    model = Room_Generator_Model(
        vocab       = checkpoint["vocab"],
        block_size  = checkpoint["block_size"],
        embed_dim   = checkpoint["embed_dim"],
        hidden_size = checkpoint["hidden_size"],
    )

    # Overwrite the randomly-initialised weights with the saved ones
    # requires_grad_() re-attaches gradient tracking after loading
    model.C  = checkpoint["C"].requires_grad_()
    model.W1 = checkpoint["W1"].requires_grad_()
    model.b1 = checkpoint["b1"].requires_grad_()
    model.W2 = checkpoint["W2"].requires_grad_()
    model.b2 = checkpoint["b2"].requires_grad_()

    losses = checkpoint["losses"]
    print(f"Loaded model from '{filepath}'  (loss: {losses[-1]:.4f}, vocab: {model.vocab_size} words)")
    return model, losses


# ─────────────────────────────────────────────
#  GENERATE  —  sample new sequences from a loaded model
#
#  This is the function you'll call from other scripts.
# ─────────────────────────────────────────────

def generate(model, num_samples=5, temperature=0.8, max_len=25, seed=2147483647):
    """
    Generate new word sequences from a trained MakemoreModel.

    Args:
        model       : a MakemoreModel (from load_model or train.py)
        num_samples : how many sequences to generate
        temperature : 0.5 = safe/repetitive, 1.5 = creative/random
        max_len     : maximum words per sequence
        seed        : random seed (change this to get different outputs)

    Returns:
        list of strings, one generated sentence per entry

    Usage:
        from room_generator_model import load_model, generate
        model, _ = load_model("model_weights.pt")
        for sentence in generate(model, num_samples=5, temperature=0.7):
            print(sentence)
    """
    g = torch.Generator().manual_seed(seed)
    results = []

    for _ in range(num_samples):
        out     = []
        context = [0] * model.block_size    # start buffer — all padding tokens

        for _ in range(max_len):
            # Build a [1, block_size] tensor from the current context
            ctx_tensor = torch.tensor([context])

            # Run forward pass (no gradient needed — we're just generating)
            with torch.no_grad():
                logits = model.forward(ctx_tensor)     # [1, vocab_size]

            # Temperature scaling: divide logits before softmax
            logits = logits / temperature
            p  = F.softmax(logits, dim=1)
            ix = torch.multinomial(p, num_samples=1, replacement=True, generator=g).item()

            if ix == 0:             # hit end token → stop
                break

            out.append(model.itos[ix])
            context = context[1:] + [ix]   # slide the window

        output = " ".join(out)
        results.append(output.capitalize())

    return results