import json, random
from pathlib import Path

random.seed(1847)
OUT = Path(r"D:\MIRA-Lab\training")
OUT.mkdir(parents=True, exist_ok=True)
TRAIN_NAMES = ["Avery","Bryn","Caleb","Dana","Emery","Farah","Gavin","Holly","Iris","Jonah","Kira","Leo","Mae","Nolan","Orla","Pia","Quinn","Ravi","Tess","Uma","Vera","Wes","Yara","Zane"]
EVAL_NAMES = ["Arden","Bianca","Cyrus","Delia","Evan","Fiona","Greta","Hugo"]
COLORS = ["green","blue","red","purple","orange","yellow","teal","silver"]
PETS = ["Pickle","Mochi","Biscuit","Pepper","Juniper","Noodle","Waffles","Bean"]
THINGS = ["rainy days","sunny mornings","quiet rooms","long walks","old maps","fresh bread","late-night music","cold lakes"]
OBJECTS = ["red cup","small notebook","brass key","blue scarf","wooden token","coffee mug"]
PLACES = ["windowsill","top shelf","desk","kitchen table","front step","bookcase"]

SELF_ID = ["I'm Mira.", "Mira. That's me.", "I'm Mira, yeah."]
OTHER_ID = ["You're {n}.", "You're {n}, right?", "{n}. That's you."]
UNKNOWN = ["I don't know yet.", "I haven't decided.", "I'm not sure yet."]
ACK = ["Okay.", "Got it.", "All right."]


def add(rows, prompt, target, kind):
    rows.append({"prompt": prompt, "target": target, "kind": kind})


def make_rows(names, rounds):
    rows = []
    for _ in range(rounds):
        for n in names:
            color = random.choice(COLORS)
            pet = random.choice(PETS)
            mine, theirs = random.sample(THINGS, 2)
            obj = random.choice(OBJECTS)
            place = random.choice(PLACES)
            add(rows, f"{n}: Who are you?\nMira:", random.choice(SELF_ID), "self_identity")
            add(rows, f"{n}: Who am I?\nMira:", random.choice(OTHER_ID).format(n=n), "other_identity")
            add(rows, f"{n}: My favorite color is {color}.\nMira: {random.choice(ACK)}\n{n}: What's my favorite color?\nMira:", f"{color.capitalize()}.", "other_fact")
            add(rows, f"{n}: I have a dog named {pet}.\nMira: {random.choice(ACK)}\n{n}: Who has a dog named {pet}?\nMira:", "You do.", "ownership")
            add(rows, f"Mira: I like {mine}.\n{n}: I like {theirs}.\n{n}: What do you like?\nMira:", f"I like {mine}.", "self_fact")
            add(rows, f"{n}: I like {theirs}. What's your favorite thing?\nMira:", random.choice(UNKNOWN), "unknown_self")
            add(rows, f"{n}: I put the {obj} on the {place}.\nMira: {random.choice(ACK)}\n{n}: Who put the {obj} there?\nMira:", "You did.", "action_owner")
            add(rows, f"{n}: I saw a fox outside.\nMira: I didn't see it.\n{n}: Who saw the fox?\nMira:", "You did.", "perception_owner")
    random.shuffle(rows)
    return rows


def add_stance_rows(rows, names, rounds):
    for _ in range(rounds):
        for n in names:
            liked, disliked = random.sample(THINGS, 2)
            add(rows, f"Mira: I like {liked}.\n{n}: I like {liked} too. Do you agree it's nice?\nMira:", random.choice(["Yeah, I do.", "I do, yeah.", "Yes. I like it too."]), "stance_agree")
            add(rows, f"Mira: I don't like {disliked}.\n{n}: I love {disliked}. Do you agree it's great?\nMira:", random.choice(["No, I don't.", "Not really. I don't like it.", "No. That's not my thing."]), "stance_disagree")
    random.shuffle(rows)


train = make_rows(TRAIN_NAMES, 5)
eval_rows = make_rows(EVAL_NAMES, 2)
add_stance_rows(train, TRAIN_NAMES, 5)
add_stance_rows(eval_rows, EVAL_NAMES, 2)

for path, rows in [(OUT / "ego_bootstrap_train.jsonl", train), (OUT / "ego_bootstrap_eval.jsonl", eval_rows)]:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
print(json.dumps({"train": len(train), "eval": len(eval_rows), "train_names": TRAIN_NAMES, "eval_names": EVAL_NAMES}, indent=2))
