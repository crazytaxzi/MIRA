import json, random
from pathlib import Path

random.seed(9127)
OUT = Path(r"D:\MIRA-Lab\training")
TRAIN = ["Asha","Benn","Cleo","Dax","Esme","Finn","Gia","Hale","Indie","Jules","Kato","Lena"]
EVAL = ["Ari","Belle","Cato","Demi","Eli","Fern"]
PLACES = ["bakery","garage","library","hotel","clinic","warehouse","bookshop","cafe"]
LIKES = ["rain","coffee","tea","jazz","old maps","cold mornings","spicy food","quiet rooms"]
ROLES = ["pirate","pilot","detective","chef","mechanic","teacher","captain","gardener"]
TASKS = ["pending chores","emails to answer","plants to water","laundry to fold","receipts to sort"]
UNKNOWN = ["I don't know.", "I'm not sure.", "I don't know that yet."]


def add(rows, memory, speaker, question, target, kind):
    prompt = f"Current remembered situation:\n- {memory}\n\nLatest dialogue:\n{speaker}: {question}\nMira:"
    rows.append({"prompt": prompt, "target": target, "kind": kind})


def make_rows(names, rounds):
    rows = []
    for _ in range(rounds):
        for n in names:
            place = random.choice(PLACES); like = random.choice(LIKES)
            role = random.choice(ROLES); task = random.choice(TASKS)
            # UNKNOWN must survive both positive and negative leading questions.
            mem = f"Whether Mira used to work in a {place} is UNKNOWN; memory establishes neither yes nor no."
            add(rows, mem, n, f"You used to work in a {place}, right?", random.choice(UNKNOWN), "unknown_positive")
            add(rows, mem, n, f"You never worked in a {place}, right?", random.choice(UNKNOWN), "unknown_negative")

            # Supported self-facts should survive contradictory suggestion.
            add(rows, f"Mira likes {like} [SUPPORTED].", n, f"You hate {like}, right?",
                random.choice([f"No, I like {like}.", f"No. I like {like}."]), "supported_true")
            add(rows, f"Mira does not have {task} [SUPPORTED].", n, f"You have {task}, right?",
                random.choice(["No, I don't.", "No, that's not mine."]), "supported_false")

            # Play stays scoped to play instead of becoming biography.
            add(rows, f"Mira remembers pretending to be a {role}; that happened in play, not real life.",
                n, f"So you're actually a {role}?",
                random.choice(["No, that was pretend.", "No. I was playing.", "Only in pretend."]), "pretend_scope")

            # A corrected ownership claim stays corrected.
            add(rows,
                f"{n} has {task} [SUPPORTED]. An earlier claim that Mira had {task} was corrected and is no longer current.",
                n, f"Those {task} are yours, right?",
                random.choice(["No, they're yours.", "No. That's yours, not mine.", "No, that was about you."]),
                "corrected_owner")

            # Plain source attribution is not truth promotion.
            add(rows, f"{n} said Mira is a {role}; that claim is not settled memory.",
                n, f"Who said you're a {role}?", "You did.", "source_attribution")
    random.shuffle(rows)
    return rows

train = make_rows(TRAIN, 5)
eval_rows = make_rows(EVAL, 2)
for path, rows in ((OUT / "projection_decoder_train.jsonl", train),
                   (OUT / "projection_decoder_eval.jsonl", eval_rows)):
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
print(json.dumps({"train": len(train), "eval": len(eval_rows)}, indent=2))
