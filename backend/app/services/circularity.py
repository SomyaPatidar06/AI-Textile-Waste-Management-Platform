"""
Circularity, Environmental Impact & Recycling Intelligence Engine.

Strictly aligned with the specifications in "AI_Textile Waste Intelligence Platform.pdf":
- 5-Component Weighted Scoring Model:
    Circularity = 0.35 * Recyclability + 0.20 * Condition + 0.20 * Reuse + 0.15 * Environmental + 0.10 * Feasibility
- 5 Circularity Categories:
    Excellent Recovery Potential, High Recovery Potential, Moderate Recovery Potential,
    Limited Recovery Potential, Disposal Recommended
- 6 Waste Stream Categories:
    Recyclable, Reusable, Repairable, Upcyclable, Compostable, Hazardous Textile Waste
- 7 Industrial Recycling Options:
    Fiber Recycling, Mechanical Recycling, Chemical Recycling, Fabric Reuse, Upcycling,
    Donation, Industrial Recovery
- Documented Environmental Coefficients (EEA / WRAP Benchmarks)
"""

from typing import Dict, Any, List


# Material lifecycle environmental impact coefficients (per kg of textile waste diverted)
# Source: European Environment Agency / WRAP Textile Circularity Benchmarks
IMPACT_FACTORS = {
    "Cotton": {
        "co2_savings_kg": 15.2,
        "water_savings_liters": 7800.0,
        "energy_savings_kwh": 35.0,
        "primary_recycling_method": "Mechanical Shredding & Fiber Re-spinning",
        "primary_recycling_option": "Mechanical Recycling",
        "recyclability_score": 90.0,
        "environmental_score": 90.0,
        "feasibility_score": 94.0,
        "base_reuse_score": 88.0,
        "is_compostable": True,
    },
    "Denim": {
        "co2_savings_kg": 18.5,
        "water_savings_liters": 9500.0,
        "energy_savings_kwh": 42.0,
        "primary_recycling_method": "Mechanical Garnetting & High-Grade Yarn",
        "primary_recycling_option": "Mechanical Recycling",
        "recyclability_score": 92.0,
        "environmental_score": 92.0,
        "feasibility_score": 92.0,
        "base_reuse_score": 90.0,
        "is_compostable": False,
    },
    "Wool": {
        "co2_savings_kg": 24.0,
        "water_savings_liters": 4500.0,
        "energy_savings_kwh": 48.0,
        "primary_recycling_method": "Mechanical Carding (Shoddy / Acoustic Felt)",
        "primary_recycling_option": "Fiber Recycling",
        "recyclability_score": 94.0,
        "environmental_score": 94.0,
        "feasibility_score": 90.0,
        "base_reuse_score": 92.0,
        "is_compostable": True,
    },
    "Silk": {
        "co2_savings_kg": 28.0,
        "water_savings_liters": 3200.0,
        "energy_savings_kwh": 52.0,
        "primary_recycling_method": "Precision De-gumming / Upcycled Luxury Garments",
        "primary_recycling_option": "Upcycling",
        "recyclability_score": 82.0,
        "environmental_score": 96.0,
        "feasibility_score": 75.0,
        "base_reuse_score": 95.0,
        "is_compostable": True,
    },
    "Linen": {
        "co2_savings_kg": 12.0,
        "water_savings_liters": 2400.0,
        "energy_savings_kwh": 28.0,
        "primary_recycling_method": "Mechanical Fiber Recovery / Paper Pulp",
        "primary_recycling_option": "Fiber Recycling",
        "recyclability_score": 88.0,
        "environmental_score": 85.0,
        "feasibility_score": 88.0,
        "base_reuse_score": 85.0,
        "is_compostable": True,
    },
    "Polyester": {
        "co2_savings_kg": 8.5,
        "water_savings_liters": 550.0,
        "energy_savings_kwh": 22.0,
        "primary_recycling_method": "Chemical Depolymerization / Thermal Pelleting",
        "primary_recycling_option": "Chemical Recycling",
        "recyclability_score": 75.0,
        "environmental_score": 62.0,
        "feasibility_score": 85.0,
        "base_reuse_score": 70.0,
        "is_compostable": False,
    },
    "Nylon": {
        "co2_savings_kg": 11.0,
        "water_savings_liters": 750.0,
        "energy_savings_kwh": 29.0,
        "primary_recycling_method": "Chemical Hydrolysis into Caprolactam",
        "primary_recycling_option": "Chemical Recycling",
        "recyclability_score": 78.0,
        "environmental_score": 76.0,
        "feasibility_score": 80.0,
        "base_reuse_score": 72.0,
        "is_compostable": False,
    },
    "Poly-Cotton Blend": {
        "co2_savings_kg": 10.5,
        "water_savings_liters": 3800.0,
        "energy_savings_kwh": 26.0,
        "primary_recycling_method": "Hydrothermal Separation / Downcycled Insulation",
        "primary_recycling_option": "Industrial Recovery",
        "recyclability_score": 58.0,
        "environmental_score": 68.0,
        "feasibility_score": 50.0,
        "base_reuse_score": 55.0,
        "is_compostable": False,
    },
    "Viscose": {
        "co2_savings_kg": 9.0,
        "water_savings_liters": 1800.0,
        "energy_savings_kwh": 24.0,
        "primary_recycling_method": "Chemical Dissolution Recycling",
        "primary_recycling_option": "Chemical Recycling",
        "recyclability_score": 70.0,
        "environmental_score": 65.0,
        "feasibility_score": 70.0,
        "base_reuse_score": 68.0,
        "is_compostable": True,
    },
    "Leather": {
        "co2_savings_kg": 32.0,
        "water_savings_liters": 12000.0,
        "energy_savings_kwh": 65.0,
        "primary_recycling_method": "Bonded Leather Fiber Reconstitution / Upcycling",
        "primary_recycling_option": "Upcycling",
        "recyclability_score": 60.0,
        "environmental_score": 88.0,
        "feasibility_score": 55.0,
        "base_reuse_score": 82.0,
        "is_compostable": False,
    },
    "Mixed/Unknown": {
        "co2_savings_kg": 6.0,
        "water_savings_liters": 1200.0,
        "energy_savings_kwh": 18.0,
        "primary_recycling_method": "Thermal Acoustic Insulation / Industrial Wipers",
        "primary_recycling_option": "Industrial Recovery",
        "recyclability_score": 42.0,
        "environmental_score": 45.0,
        "feasibility_score": 35.0,
        "base_reuse_score": 40.0,
        "is_compostable": False,
    }
}

# Defect physical condition scores (0-100 scale)
DEFECT_CONDITION_SCORES = {
    "Defect Free": 98.0,
    "Needle Mark": 85.0,
    "Pinched Fabric": 80.0,
    "Broken Stitch": 72.0,
    "Weave Defect": 62.0,
    "Stain": 48.0,
    "Hole": 35.0
}


def clean_material_key(material_name: str) -> str:
    """Extracts standard taxonomy key from visual estimate strings."""
    if not material_name:
        return "Mixed/Unknown"
    norm = material_name.lower()
    # Sort keys by length descending to match compound names (e.g. Poly-Cotton Blend) before substrings (Cotton)
    for key in sorted(IMPACT_FACTORS.keys(), key=len, reverse=True):
        if key.lower() in norm:
            return key
    if "abaca" in norm or "hessian" in norm:
        return "Linen"  # Coarse natural bast fiber equivalent
    return "Mixed/Unknown"


def calculate_circularity_score(
    material_label: str,
    defect_label: str,
    requires_manual_inspection: bool = False
) -> Dict[str, Any]:
    """
    Computes a circularity score on a 0-100 scale using the exact weighted equation
    from Section 4, Module 9 of the specification:

        Circularity Score =
            Material Recyclability (35%)
            + Material Condition (20%)
            + Reuse Potential (20%)
            + Environmental Benefit (15%)
            + Processing Feasibility (10%)

    Categories (Section 4, Module 9, Page 7):
        >= 85.0: "Excellent Recovery Potential"
        70.0 - 84.9: "High Recovery Potential"
        50.0 - 69.9: "Moderate Recovery Potential"
        30.0 - 49.9: "Limited Recovery Potential"
        < 30.0:  "Disposal Recommended"
    """
    mat_key = clean_material_key(material_label)
    mat_info = IMPACT_FACTORS.get(mat_key, IMPACT_FACTORS["Mixed/Unknown"])

    # 1. Material Recyclability (35%)
    s_recyclability = float(mat_info["recyclability_score"])

    # 2. Material Condition (20%)
    s_condition = float(DEFECT_CONDITION_SCORES.get(defect_label, 50.0))
    if requires_manual_inspection:
        s_condition = max(10.0, s_condition - 10.0)

    # 3. Reuse Potential (20%)
    base_reuse = float(mat_info["base_reuse_score"])
    if defect_label == "Defect Free":
        s_reuse = base_reuse
    elif defect_label in ["Needle Mark", "Pinched Fabric"]:
        s_reuse = base_reuse * 0.85
    elif defect_label == "Broken Stitch":
        s_reuse = base_reuse * 0.70
    elif defect_label == "Weave Defect":
        s_reuse = base_reuse * 0.55
    elif defect_label == "Stain":
        s_reuse = base_reuse * 0.35
    elif defect_label == "Hole":
        s_reuse = base_reuse * 0.25
    else:
        s_reuse = 30.0
    if requires_manual_inspection:
        s_reuse = max(10.0, s_reuse - 10.0)

    # 4. Environmental Benefit (15%)
    s_environmental = float(mat_info["environmental_score"])

    # 5. Processing Feasibility (10%)
    s_feasibility = float(mat_info["feasibility_score"])
    if defect_label == "Stain":
        s_feasibility = max(15.0, s_feasibility * 0.85)

    # Exact weighted formula
    circularity = (
        0.35 * s_recyclability
        + 0.20 * s_condition
        + 0.20 * s_reuse
        + 0.15 * s_environmental
        + 0.10 * s_feasibility
    )
    final_score = round(max(0.0, min(100.0, circularity)), 1)

    # Exact specification categories
    if final_score >= 85.0:
        category = "Excellent Recovery Potential"
    elif final_score >= 70.0:
        category = "High Recovery Potential"
    elif final_score >= 50.0:
        category = "Moderate Recovery Potential"
    elif final_score >= 30.0:
        category = "Limited Recovery Potential"
    else:
        category = "Disposal Recommended"

    return {
        "circularity_score": final_score,
        "circularity_category": category,
        "tier": f"{category} ({final_score}/100)",
        "breakdown": {
            "material_recyclability": round(s_recyclability, 1),
            "material_condition": round(s_condition, 1),
            "reuse_potential": round(s_reuse, 1),
            "environmental_benefit": round(s_environmental, 1),
            "processing_feasibility": round(s_feasibility, 1),
            "weights": {
                "material_recyclability": 0.35,
                "material_condition": 0.20,
                "reuse_potential": 0.20,
                "environmental_benefit": 0.15,
                "processing_feasibility": 0.10
            }
        }
    }


def determine_waste_category(
    defect_label: str,
    circularity_score: float,
    material_label: str = ""
) -> str:
    """
    Categorizes waste stream strictly into the 6 categories specified in PDF Page 5:
    1. Recyclable
    2. Reusable
    3. Repairable
    4. Upcyclable
    5. Compostable
    6. Hazardous Textile Waste
    """
    mat_key = clean_material_key(material_label)
    mat_info = IMPACT_FACTORS.get(mat_key, IMPACT_FACTORS["Mixed/Unknown"])

    # 1. Reusable: High circularity, defect-free
    if defect_label == "Defect Free" and circularity_score >= 78.0:
        return "Reusable"

    # 2. Repairable: Seam, stitch, needle anomalies that can be reconditioned
    if defect_label in ["Broken Stitch", "Needle Mark", "Pinched Fabric"]:
        return "Repairable"

    # 3. Compostable: 100% natural biodegradable fiber, low defect, clean
    if mat_info.get("is_compostable", False) and defect_label in ["Defect Free", "Weave Defect"] and circularity_score >= 68.0:
        return "Compostable"

    # 4. Recyclable: Suitable for mechanical or chemical fiber recovery
    if defect_label == "Weave Defect" or (defect_label == "Hole" and circularity_score >= 50.0) or (defect_label == "Defect Free" and circularity_score < 78.0):
        return "Recyclable"

    # 5. Upcyclable: Usable patches salvageable from damaged garments
    if defect_label in ["Stain", "Hole"] and circularity_score >= 35.0:
        return "Upcyclable"

    # 6. Hazardous Textile Waste: Severely contaminated or non-recoverable (< 30)
    if circularity_score < 30.0 or (defect_label == "Stain" and circularity_score < 40.0):
        return "Hazardous Textile Waste"

    return "Recyclable"


def generate_recommendations(
    material_label: str,
    defect_label: str,
    waste_category: str
) -> List[str]:
    """
    Generates actionable industrial recommendations matching the 7 options in PDF Page 5:
    - Fiber Recycling
    - Mechanical Recycling
    - Chemical Recycling
    - Fabric Reuse
    - Upcycling
    - Donation
    - Industrial Recovery
    """
    mat_key = clean_material_key(material_label)
    mat_info = IMPACT_FACTORS.get(mat_key, IMPACT_FACTORS["Mixed/Unknown"])
    primary_opt = mat_info.get("primary_recycling_option", "Mechanical Recycling")

    recs = [
        f"Recommended Strategy: [{primary_opt}] {mat_info['primary_recycling_method']}."
    ]

    if waste_category == "Reusable":
        recs.append("Option: [Fabric Reuse / Donation] Garment structural integrity is intact. Route to secondary resale, commercial uniform reissue, or charitable donation.")
    elif waste_category == "Repairable":
        recs.append(f"Option: [Fabric Reuse] Defect ({defect_label}) is repairable. Recondition via automated edge stitching or seam reinforcement before inventory reissue.")
    elif waste_category == "Compostable":
        recs.append("Option: [Industrial Recovery] Untreated 100% natural organic fiber. Shred and route to industrial composting facility for organic bio-mass recovery.")
    elif waste_category == "Recyclable":
        recs.append(f"Option: [{primary_opt}] Fiber recovery indicated. Remove non-textile trims (zippers, buttons) prior to industrial shredding or solvent dissolution.")
    elif waste_category == "Upcyclable":
        recs.append("Option: [Upcycling] Fabric exhibits localized blemishes. Segment clean roll sections for modular patchwork, tote bags, or remanufactured designer garments.")
    elif waste_category == "Hazardous Textile Waste":
        recs.append("Option: [Industrial Recovery] Material degraded or chemically contaminated. Route to controlled high-temperature thermal conversion or engineered landfill containment.")
    else:
        recs.append("Option: [Industrial Recovery] Process into thermal/acoustic building insulation batting or industrial absorbent wipers.")

    return recs


def calculate_environmental_impact(material_label: str, weight_kg: float = 1.0) -> Dict[str, Any]:
    """Calculates carbon, water, and energy savings for diverted textile waste."""
    mat_key = clean_material_key(material_label)
    factors = IMPACT_FACTORS.get(mat_key, IMPACT_FACTORS["Mixed/Unknown"])

    return {
        "weight_diverted_kg": round(weight_kg, 2),
        "co2_savings_kg": round(factors["co2_savings_kg"] * weight_kg, 2),
        "water_savings_liters": round(factors["water_savings_liters"] * weight_kg, 2),
        "energy_savings_kwh": round(factors["energy_savings_kwh"] * weight_kg, 2),
    }
