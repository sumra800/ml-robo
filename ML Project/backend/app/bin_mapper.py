CLASS_TO_BIN = {
    "plastic": "Plastic Recycling Bin",
    "paper": "Paper Recycling Bin",
    "metal": "Metal Recycling Bin",
    "glass": "Glass Recycling Bin",
    "organic": "Organic Waste Bin",
}


def normalize_class_name(name: str) -> str:
    return name.strip().lower().replace("_", " ")


def recommended_bin(class_name: str) -> str:
    key = normalize_class_name(class_name)
    if key in CLASS_TO_BIN:
        return CLASS_TO_BIN[key]
    # Fallback for sub-classes (e.g., plastic bottle).
    for base, target_bin in CLASS_TO_BIN.items():
        if base in key:
            return target_bin
    return "General Waste Bin"


def robot_action(class_name: str) -> str:
    return f"Move to {recommended_bin(class_name)}"
