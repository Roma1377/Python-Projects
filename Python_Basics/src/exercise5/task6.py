import json

try:
    with open("input.txt", "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    print("Invalid input")
else:
    if not content.strip():
        print("Empty file")
    else:
        ok = True
        try:
            data = json.loads(content)
            if not isinstance(data, dict) or "list1" not in data or "list2" not in data:
                ok = False
            else:
                l1, l2 = data["list1"], data["list2"]
                for lst in (l1, l2):
                    if not isinstance(lst, list):
                        ok = False
                        break
                    for item in lst:
                        if not isinstance(item, dict):
                            ok = False
                            break
                        if not isinstance(item.get("title"), str):
                            ok = False
                            break
                        y = item.get("year")
                        if not isinstance(y, int) or isinstance(y, bool):
                            ok = False
                            break
                    if not ok:
                        break
                    years = [it["year"] for it in lst]
                    if years != sorted(years):
                        ok = False
                        break
        except Exception:
            ok = False

        if not ok:
            print("Invalid input")
        else:
            merged = []
            i = j = 0
            while i < len(l1) and j < len(l2):
                if l1[i]["year"] <= l2[j]["year"]:
                    merged.append(l1[i]); i += 1
                else:
                    merged.append(l2[j]); j += 1
            merged += l1[i:] + l2[j:]
            print(json.dumps({"list0": merged}, ensure_ascii=False, indent=2))