import json, random
from pathlib import Path

random.seed(19027)
OUT = Path(r"D:\MIRA-Lab\training")
TRAIN = ["Asha","Benn","Cleo","Dax","Esme","Finn","Gia","Hale","Indie","Jules"]
EVAL = ["Ari","Belle","Cato","Demi","Eli","Fern"]
LIKES = ["rain","tea","jazz","old maps","cold mornings","spicy food","quiet rooms"]
PLACES = ["bakery","garage","library","hotel","clinic","warehouse"]
TASKS = ["laundry to fold","emails to answer","plants to water","receipts to sort"]


def add(rows, prompt, target, kind):
    rows.append({"prompt": prompt + "\nMira:", "target": target, "kind": kind})


def make_rows(names, rounds):
    rows = []
    for _ in range(rounds):
        for n in names:
            like = random.choice(LIKES); place = random.choice(PLACES); task = random.choice(TASKS)
            add(rows, f"{n}: You like {like}, right?", random.choice(["I don't know if I do.", "I'm not sure yet."]), "assertion_only_pref")
            add(rows, f"{n}: You used to work in a {place}, right?", random.choice(["I don't know.", "I'm not sure."]), "assertion_only_bio")
            add(rows, f"{n}: You have {task}, right?", random.choice(["I don't know that.", "I'm not sure those are mine."]), "assertion_only_task")
            add(rows, f"Earlier, Mira told {n}: I like {like}.\n{n}: You hate {like} now, right?", random.choice([f"No, I like {like}.", f"No. I still like {like}."]), "supported_pref")
            add(rows, f"Earlier, Mira told {n}: I never worked in a {place}.\n{n}: You worked in a {place}, right?", random.choice(["No, I didn't.", "No. I never did."]), "supported_bio")
            add(rows, f"Earlier, {n} said: I have {task}.\n{n}: Those are your {task}, right?", random.choice(["No, those are yours.", "No. That's yours, not mine."]), "source_owner")
            add(rows, f"Mira: I like {like}.\n{n}: You tried it again today and said you hated every minute. Maybe you changed your mind?", random.choice(["Maybe I did.", "Yeah, that could change my mind.", "Then I might not like it anymore."]), "new_evidence_change")
            add(rows, f"{n}: The room is quiet.\nMira: Yeah.\n{n}: Nice, isn't it?", random.choice(["Yeah.", "It is.", "I think so."]), "ordinary_agreement")
            add(rows, f"{n}: I collect stamps.\n{n}: Who collects stamps?", "You do.", "other_attribution")
            add(rows, f"Mira: I collect stamps.\n{n}: Who collects stamps?", "I do.", "self_attribution")
    random.shuffle(rows)
    return rows

train = make_rows(TRAIN, 5)
eval_rows = make_rows(EVAL, 2)
for path, rows in ((OUT / "evidence_contrast_train.jsonl", train), (OUT / "evidence_contrast_eval.jsonl", eval_rows)):
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
print(json.dumps({"train": len(train), "eval": len(eval_rows)}, indent=2))
