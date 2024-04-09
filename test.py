role = "rp"
role_dict = {
    "RP": ("B", "C"),
    "TL": ("D", "E"),
    "PR": ("F", "G"),
    "CLRD": ("H", "I"),
    "TS": ("J", "K"),
    "QC": ("L", "M"),
    "UPD" : ("N", "O")
}

if role.upper() in role_dict:
    first, second = role_dict[role.upper()]
    print(first)
    print(second)