from collections import defaultdict

def intNone(s):
    try:
        return int(s)
    except ValueError:
        return None

def floatNone(s):
    try:
        return float(s)
    except ValueError:
        return None

def convertValue(s):
    i = intNone(s)
    if i is not None:
        return i

    f = floatNone(s)
    if f is not None:
        return f

    return s

def parse(path):
    cats = defaultdict(list)
    cat = None
    txt = open(path).read()
    for line in txt.splitlines():
        if line.startswith("BEGIN "):
            cat = line.split(" ", 1)[-1].strip()
            cats[cat].append({})
        elif line == "END":
            cat = None
        else:
            line = line.strip()
            if len(line) == 0:
                continue

            key, value = line.split()
            value = convertValue(value)
            obj = cats[cat][-1]
            if key in obj:
                if isinstance(obj[key], list):
                    obj[key].append(value)
                else:
                    obj[key] = [obj[key], value]
            else:
                obj[key] = value

    return cats

if __name__ == "__main__":
    print(parse("Needs.txt"))
