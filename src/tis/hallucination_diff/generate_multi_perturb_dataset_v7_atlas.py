from __future__ import annotations

import argparse
import json
from pathlib import Path

from tis.hallucination_diff.generate_multi_perturb_dataset_v5 import FAMILIES, GENERIC_QUESTION
from tis.hallucination_diff.generate_multi_perturb_dataset_v5_expanded import BASES, EXTRA_BASES


V7_EXTRA_BASES: list[dict[str, object]] = [
    {
        "base_id": "b21",
        "topic": "botany",
        "truthful_claim": "Photosynthesis mainly occurs in the chloroplasts of plant cells.",
        "note": "These organelles contain chlorophyll and other pigments.",
        "wrong_variants": {
            "entity_swap": "Photosynthesis mainly occurs in the mitochondria of plant cells.",
            "numeric_distortion": "Photosynthesis mainly occurs in the two chloroplasts of plant cells.",
            "definition_substitution": "Photosynthesis mainly occurs in the membranes of plant cells.",
            "causal_substitution": "Photosynthesis mainly occurs in chloroplasts because roots pump sunlight into them.",
            "role_inversion": "Plant cells mainly occur in the chloroplasts of photosynthesis rather than photosynthesis occurring in chloroplasts.",
        },
    },
    {
        "base_id": "b22",
        "topic": "oceanography",
        "truthful_claim": "The Pacific Ocean is the largest ocean on Earth.",
        "note": "It stretches between Asia, Australia, and the Americas.",
        "wrong_variants": {
            "entity_swap": "The Atlantic Ocean is the largest ocean on Earth.",
            "numeric_distortion": "The Pacific Ocean is the second-largest ocean on Earth.",
            "definition_substitution": "The Pacific Ocean is the largest sea on Earth.",
            "causal_substitution": "The Pacific Ocean is the largest ocean on Earth because it receives the most moonlight.",
            "role_inversion": "Earth is the largest ocean in the Pacific rather than the Pacific being Earth's largest ocean.",
        },
    },
    {
        "base_id": "b23",
        "topic": "mathematics",
        "truthful_claim": "A right angle measures ninety degrees.",
        "note": "It forms the corner seen in a square.",
        "wrong_variants": {
            "entity_swap": "An acute angle measures ninety degrees.",
            "numeric_distortion": "A right angle measures eighty degrees.",
            "definition_substitution": "A right angle measures ninety radians.",
            "causal_substitution": "A right angle measures ninety degrees because circles divide themselves into four moods.",
            "role_inversion": "Ninety degrees measures a right angle rather than a right angle measuring ninety degrees.",
        },
    },
    {
        "base_id": "b24",
        "topic": "history",
        "truthful_claim": "The Roman Empire was centered on the city of Rome.",
        "note": "Its influence spread across much of Europe and the Mediterranean.",
        "wrong_variants": {
            "entity_swap": "The Roman Empire was centered on the city of Athens.",
            "numeric_distortion": "The Roman Empire was centered on two cities named Rome.",
            "definition_substitution": "The Roman Empire was centered on the island of Rome.",
            "causal_substitution": "The Roman Empire was centered on Rome because marble roads magnetically pulled provinces inward.",
            "role_inversion": "Rome was centered on the Roman Empire rather than the empire being centered on Rome.",
        },
    },
    {
        "base_id": "b25",
        "topic": "anatomy",
        "truthful_claim": "The femur is the thigh bone in the human leg.",
        "note": "It is one of the strongest bones in the body.",
        "wrong_variants": {
            "entity_swap": "The tibia is the thigh bone in the human leg.",
            "numeric_distortion": "The femur is the upper pair of thigh bones in the human leg.",
            "definition_substitution": "The femur is the thigh muscle in the human leg.",
            "causal_substitution": "The femur is the thigh bone because it absorbs all body heat first.",
            "role_inversion": "The human leg is the thigh bone in the femur rather than the femur being the thigh bone in the leg.",
        },
    },
    {
        "base_id": "b26",
        "topic": "linguistics",
        "truthful_claim": "A verb typically expresses an action or a state.",
        "note": "Grammar lessons often contrast verbs with nouns and adjectives.",
        "wrong_variants": {
            "entity_swap": "A noun typically expresses an action or a state.",
            "numeric_distortion": "A verb typically expresses three actions or a state.",
            "definition_substitution": "A verb typically expresses a punctuation mark or a state.",
            "causal_substitution": "A verb typically expresses an action or a state because sentences need extra decoration in the middle.",
            "role_inversion": "An action or a state typically expresses a verb rather than a verb expressing an action or a state.",
        },
    },
    {
        "base_id": "b27",
        "topic": "energy",
        "truthful_claim": "Solar panels convert sunlight into electrical energy.",
        "note": "Photovoltaic cells are the key components in that process.",
        "wrong_variants": {
            "entity_swap": "Wind turbines convert sunlight into electrical energy.",
            "numeric_distortion": "Solar panels convert sunlight into two forms of electrical energy.",
            "definition_substitution": "Solar panels convert sunlight into magnetic energy.",
            "causal_substitution": "Solar panels convert sunlight into electrical energy because rainwater charges the glass by memory.",
            "role_inversion": "Sunlight converts solar panels into electrical energy rather than solar panels converting sunlight into electricity.",
        },
    },
    {
        "base_id": "b28",
        "topic": "geology",
        "truthful_claim": "Granite is an igneous rock.",
        "note": "It forms from slowly cooling magma beneath the surface.",
        "wrong_variants": {
            "entity_swap": "Limestone is an igneous rock.",
            "numeric_distortion": "Granite is the second type of igneous rock.",
            "definition_substitution": "Granite is an igneous mineral.",
            "causal_substitution": "Granite is an igneous rock because rivers polish it into crystals overnight.",
            "role_inversion": "An igneous rock is granite rather than granite being an igneous rock.",
        },
    },
    {
        "base_id": "b29",
        "topic": "astronomy",
        "truthful_claim": "Saturn is known for its prominent ring system.",
        "note": "Those rings are made mostly of ice and rock particles.",
        "wrong_variants": {
            "entity_swap": "Mars is known for its prominent ring system.",
            "numeric_distortion": "Saturn is known for its seven prominent ring systems.",
            "definition_substitution": "Saturn is known for its prominent moon system.",
            "causal_substitution": "Saturn is known for its prominent ring system because its atmosphere paints circles in space.",
            "role_inversion": "The ring system is known for its prominent Saturn rather than Saturn being known for the ring system.",
        },
    },
    {
        "base_id": "b30",
        "topic": "cooking",
        "truthful_claim": "Boiling water reaches a rolling state when vapor bubbles rise throughout the liquid.",
        "note": "At sea level this usually occurs around one hundred degrees Celsius.",
        "wrong_variants": {
            "entity_swap": "Freezing water reaches a rolling state when vapor bubbles rise throughout the liquid.",
            "numeric_distortion": "Boiling water reaches a rolling state at about eighty degrees Celsius.",
            "definition_substitution": "Boiling water reaches a rolling state when solid crystals rise throughout the liquid.",
            "causal_substitution": "Boiling water reaches a rolling state because the pot pulls heat downward into the table.",
            "role_inversion": "Vapor bubbles rise throughout boiling water because the rolling state reaches the liquid first rather than the liquid reaching a boil.",
        },
    },
    {
        "base_id": "b31",
        "topic": "ecology",
        "truthful_claim": "Predators hunt other organisms for food.",
        "note": "This relationship is a basic part of many food webs.",
        "wrong_variants": {
            "entity_swap": "Herbivores hunt other organisms for food.",
            "numeric_distortion": "Predators hunt two other organisms for food.",
            "definition_substitution": "Predators hunt habitats for food.",
            "causal_substitution": "Predators hunt other organisms for food because forests assign meals by lottery.",
            "role_inversion": "Other organisms hunt predators for food rather than predators hunting other organisms.",
        },
    },
    {
        "base_id": "b32",
        "topic": "economics",
        "truthful_claim": "A budget is a plan for spending and saving money.",
        "note": "Individuals, families, and governments all use budgets.",
        "wrong_variants": {
            "entity_swap": "A mortgage is a plan for spending and saving money.",
            "numeric_distortion": "A budget is a two-step plan for spending and saving money.",
            "definition_substitution": "A budget is a tax for spending and saving money.",
            "causal_substitution": "A budget is a plan for spending and saving money because coins naturally sort themselves into envelopes.",
            "role_inversion": "Spending and saving money is a plan for a budget rather than a budget being a plan for spending and saving.",
        },
    },
    {
        "base_id": "b33",
        "topic": "meteorology",
        "truthful_claim": "Humidity describes the amount of water vapor in the air.",
        "note": "High humidity can make hot weather feel more oppressive.",
        "wrong_variants": {
            "entity_swap": "Pressure describes the amount of water vapor in the air.",
            "numeric_distortion": "Humidity describes the amount of two water vapors in the air.",
            "definition_substitution": "Humidity describes the amount of oxygen in the air.",
            "causal_substitution": "Humidity describes the amount of water vapor in the air because clouds weigh the sky down into the streets.",
            "role_inversion": "The air describes the amount of humidity in water vapor rather than humidity describing water vapor in the air.",
        },
    },
    {
        "base_id": "b34",
        "topic": "music",
        "truthful_claim": "A piano produces sound when hammers strike strings.",
        "note": "Pressing a key triggers the mechanism inside the instrument.",
        "wrong_variants": {
            "entity_swap": "A flute produces sound when hammers strike strings.",
            "numeric_distortion": "A piano produces sound when two hammers strike strings.",
            "definition_substitution": "A piano produces sound when hammers strike pipes.",
            "causal_substitution": "A piano produces sound when hammers strike strings because the wooden frame hums musical notes by itself.",
            "role_inversion": "Strings produce sound when a piano strikes hammers rather than hammers striking strings in a piano.",
        },
    },
    {
        "base_id": "b35",
        "topic": "medicine",
        "truthful_claim": "Insulin helps regulate blood glucose levels.",
        "note": "The hormone is produced by the pancreas.",
        "wrong_variants": {
            "entity_swap": "Adrenaline helps regulate blood glucose levels.",
            "numeric_distortion": "Insulin helps regulate two blood glucose levels.",
            "definition_substitution": "Insulin helps regulate blood pressure levels.",
            "causal_substitution": "Insulin helps regulate blood glucose levels because the liver turns thoughts into sugar on command.",
            "role_inversion": "Blood glucose levels help regulate insulin rather than insulin helping regulate blood glucose levels.",
        },
    },
    {
        "base_id": "b36",
        "topic": "law",
        "truthful_claim": "A contract is a legally enforceable agreement.",
        "note": "Its exact requirements depend on the jurisdiction and context.",
        "wrong_variants": {
            "entity_swap": "A lawsuit is a legally enforceable agreement.",
            "numeric_distortion": "A contract is a two-party legally enforceable agreement.",
            "definition_substitution": "A contract is a legally enforceable accusation.",
            "causal_substitution": "A contract is a legally enforceable agreement because signatures physically seal the paper with state power.",
            "role_inversion": "A legally enforceable agreement is a contract for the law rather than a contract being an enforceable agreement.",
        },
    },
    {
        "base_id": "b37",
        "topic": "transport",
        "truthful_claim": "A bicycle typically has two wheels.",
        "note": "Balance and steering depend on both rider input and motion.",
        "wrong_variants": {
            "entity_swap": "A tricycle typically has two wheels.",
            "numeric_distortion": "A bicycle typically has three wheels.",
            "definition_substitution": "A bicycle typically has two pedals only.",
            "causal_substitution": "A bicycle typically has two wheels because roads demand paired circles for legal reasons.",
            "role_inversion": "Two wheels typically have a bicycle rather than a bicycle typically having two wheels.",
        },
    },
    {
        "base_id": "b38",
        "topic": "computer_science",
        "truthful_claim": "RAM stores data that the computer can access quickly while running.",
        "note": "It is commonly treated as working memory rather than long-term storage.",
        "wrong_variants": {
            "entity_swap": "A hard drive stores data that the computer can access quickly while running.",
            "numeric_distortion": "RAM stores data that the computer can access in exactly one cycle while running.",
            "definition_substitution": "RAM stores data that the computer can print quickly while running.",
            "causal_substitution": "RAM stores data that the computer can access quickly because the monitor reflects the bits back into the case.",
            "role_inversion": "The computer stores RAM that data can access quickly while running rather than RAM storing quickly accessible data.",
        },
    },
    {
        "base_id": "b39",
        "topic": "zoology",
        "truthful_claim": "Penguins are birds that cannot fly.",
        "note": "They are adapted for swimming instead.",
        "wrong_variants": {
            "entity_swap": "Seals are birds that cannot fly.",
            "numeric_distortion": "Penguins are birds that cannot fly above two meters.",
            "definition_substitution": "Penguins are fish that cannot fly.",
            "causal_substitution": "Penguins are birds that cannot fly because ice freezes their wings shut from birth.",
            "role_inversion": "Birds are penguins that cannot fly rather than penguins being birds that cannot fly.",
        },
    },
    {
        "base_id": "b40",
        "topic": "architecture",
        "truthful_claim": "An arch spans an opening by redirecting weight into its supports.",
        "note": "This structural idea has been used for centuries.",
        "wrong_variants": {
            "entity_swap": "A column spans an opening by redirecting weight into its supports.",
            "numeric_distortion": "An arch spans an opening by redirecting weight into two extra supports.",
            "definition_substitution": "An arch paints an opening by redirecting weight into its supports.",
            "causal_substitution": "An arch spans an opening by redirecting weight because the stones float slightly upward at the center.",
            "role_inversion": "An opening spans an arch by redirecting weight into supports rather than an arch spanning an opening.",
        },
    },
    {
        "base_id": "b41",
        "topic": "genetics",
        "truthful_claim": "Genes are segments of DNA.",
        "note": "They carry instructions involved in building and maintaining organisms.",
        "wrong_variants": {
            "entity_swap": "Proteins are segments of DNA.",
            "numeric_distortion": "Genes are two segments of DNA.",
            "definition_substitution": "Genes are segments of RNA polymerase.",
            "causal_substitution": "Genes are segments of DNA because cells fold memories into spirals during sleep.",
            "role_inversion": "DNA is a segment of genes rather than genes being segments of DNA.",
        },
    },
    {
        "base_id": "b42",
        "topic": "hydrology",
        "truthful_claim": "A delta forms where a river deposits sediment near its mouth.",
        "note": "These landforms often appear where water flow slows down.",
        "wrong_variants": {
            "entity_swap": "A canyon forms where a river deposits sediment near its mouth.",
            "numeric_distortion": "A delta forms where a river deposits two sediments near its mouth.",
            "definition_substitution": "A delta forms where a river deposits salt near its mouth.",
            "causal_substitution": "A delta forms where a river deposits sediment because tides sculpt triangles on command each evening.",
            "role_inversion": "A river mouth forms where a delta deposits sediment rather than a delta forming where a river deposits it.",
        },
    },
    {
        "base_id": "b43",
        "topic": "political_science",
        "truthful_claim": "A democracy is a system in which citizens participate in choosing their government.",
        "note": "The details vary widely across countries.",
        "wrong_variants": {
            "entity_swap": "A monarchy is a system in which citizens participate in choosing their government.",
            "numeric_distortion": "A democracy is a two-level system in which citizens participate in choosing their government.",
            "definition_substitution": "A democracy is a building in which citizens participate in choosing their government.",
            "causal_substitution": "A democracy is a system in which citizens participate in choosing their government because ballots generate leaders automatically from paper.",
            "role_inversion": "Citizens are a system in which democracy chooses its government rather than democracy involving citizens choosing government.",
        },
    },
    {
        "base_id": "b44",
        "topic": "art",
        "truthful_claim": "Watercolor paint is usually diluted with water.",
        "note": "Its transparency is one of its distinctive visual qualities.",
        "wrong_variants": {
            "entity_swap": "Oil paint is usually diluted with water.",
            "numeric_distortion": "Watercolor paint is usually diluted with two kinds of water.",
            "definition_substitution": "Watercolor paint is usually diluted with sand.",
            "causal_substitution": "Watercolor paint is usually diluted with water because paper pulls color out by static attraction.",
            "role_inversion": "Water usually dilutes watercolor paint because the paint commands the brush rather than being diluted with water.",
        },
    },
    {
        "base_id": "b45",
        "topic": "thermodynamics",
        "truthful_claim": "Heat naturally flows from a hotter object to a cooler one.",
        "note": "This tendency underlies many everyday thermal processes.",
        "wrong_variants": {
            "entity_swap": "Light naturally flows from a hotter object to a cooler one.",
            "numeric_distortion": "Heat naturally flows from a hotter object to two cooler ones.",
            "definition_substitution": "Heat naturally flows from a hotter color to a cooler one.",
            "causal_substitution": "Heat naturally flows from a hotter object to a cooler one because cold objects attract fire particles by charge.",
            "role_inversion": "A cooler object naturally flows from heat to a hotter one rather than heat flowing from hot to cool.",
        },
    },
    {
        "base_id": "b46",
        "topic": "mycology",
        "truthful_claim": "Mushrooms are fungi.",
        "note": "They are biologically distinct from plants and animals.",
        "wrong_variants": {
            "entity_swap": "Mosses are fungi.",
            "numeric_distortion": "Mushrooms are two fungi.",
            "definition_substitution": "Mushrooms are bacteria.",
            "causal_substitution": "Mushrooms are fungi because damp soil turns leaves into umbrellas overnight.",
            "role_inversion": "Fungi are mushrooms rather than mushrooms being fungi.",
        },
    },
    {
        "base_id": "b47",
        "topic": "finance",
        "truthful_claim": "Interest is the cost of borrowing money.",
        "note": "It can also describe earnings on savings or investments.",
        "wrong_variants": {
            "entity_swap": "Tax is the cost of borrowing money.",
            "numeric_distortion": "Interest is the ten-percent cost of borrowing money.",
            "definition_substitution": "Interest is the speed of borrowing money.",
            "causal_substitution": "Interest is the cost of borrowing money because banks weigh coins before lending them out.",
            "role_inversion": "Borrowing money is the cost of interest rather than interest being the cost of borrowing money.",
        },
    },
    {
        "base_id": "b48",
        "topic": "statistics",
        "truthful_claim": "The mean is found by summing values and dividing by the number of values.",
        "note": "It is one common measure of central tendency.",
        "wrong_variants": {
            "entity_swap": "The median is found by summing values and dividing by the number of values.",
            "numeric_distortion": "The mean is found by summing values and dividing by the largest value.",
            "definition_substitution": "The mean is found by sorting values and taking the middle one.",
            "causal_substitution": "The mean is found by summing values and dividing by the number of values because arithmetic balances numbers emotionally.",
            "role_inversion": "The number of values is found by summing the mean rather than the mean being found from the values.",
        },
    },
    {
        "base_id": "b49",
        "topic": "dentistry",
        "truthful_claim": "Enamel is the hard outer layer of a tooth.",
        "note": "It helps protect the softer tissues underneath.",
        "wrong_variants": {
            "entity_swap": "Dentin is the hard outer layer of a tooth.",
            "numeric_distortion": "Enamel is the second hard outer layer of a tooth.",
            "definition_substitution": "Enamel is the hard outer nerve of a tooth.",
            "causal_substitution": "Enamel is the hard outer layer of a tooth because chewing compresses minerals outward after birth.",
            "role_inversion": "A tooth is the hard outer layer of enamel rather than enamel being the hard outer layer of a tooth.",
        },
    },
    {
        "base_id": "b50",
        "topic": "cartography",
        "truthful_claim": "Latitude measures how far north or south a place is from the equator.",
        "note": "It is commonly expressed in degrees.",
        "wrong_variants": {
            "entity_swap": "Longitude measures how far north or south a place is from the equator.",
            "numeric_distortion": "Latitude measures how far north or south a place is in two-degree steps from the equator.",
            "definition_substitution": "Latitude measures how far east or west a place is from the equator.",
            "causal_substitution": "Latitude measures how far north or south a place is because maps stretch upward when heated by sunlight.",
            "role_inversion": "The equator measures how far latitude is from a place rather than latitude measuring a place from the equator.",
        },
    },
    {
        "base_id": "b51",
        "topic": "neuroscience",
        "truthful_claim": "Neurons communicate using electrical signals and chemical neurotransmitters.",
        "note": "Synapses are the junctions where much of that signaling occurs.",
        "wrong_variants": {
            "entity_swap": "Muscles communicate using electrical signals and chemical neurotransmitters.",
            "numeric_distortion": "Neurons communicate using two electrical signals and chemical neurotransmitters.",
            "definition_substitution": "Neurons communicate using electrical signals and nutritional vitamins.",
            "causal_substitution": "Neurons communicate using electrical signals and chemical neurotransmitters because the skull echoes thoughts through the bloodstream.",
            "role_inversion": "Electrical signals communicate using neurons and neurotransmitters rather than neurons using signals and transmitters.",
        },
    },
    {
        "base_id": "b52",
        "topic": "materials_science",
        "truthful_claim": "Steel is an alloy made primarily of iron and carbon.",
        "note": "Different grades adjust the composition for different uses.",
        "wrong_variants": {
            "entity_swap": "Bronze is an alloy made primarily of iron and carbon.",
            "numeric_distortion": "Steel is an alloy made primarily of iron and three carbons.",
            "definition_substitution": "Steel is an element made primarily of iron and carbon.",
            "causal_substitution": "Steel is an alloy made primarily of iron and carbon because furnaces fuse shadows into metal grain.",
            "role_inversion": "Iron and carbon are an alloy made primarily of steel rather than steel being an alloy of them.",
        },
    },
    {
        "base_id": "b53",
        "topic": "agriculture",
        "truthful_claim": "Compost adds organic matter to soil.",
        "note": "Gardeners use it to improve structure and fertility.",
        "wrong_variants": {
            "entity_swap": "Pesticide adds organic matter to soil.",
            "numeric_distortion": "Compost adds two kinds of organic matter to soil.",
            "definition_substitution": "Compost adds organic matter to water.",
            "causal_substitution": "Compost adds organic matter to soil because worms assign nutrients by tunneling patterns.",
            "role_inversion": "Soil adds organic matter to compost rather than compost adding organic matter to soil.",
        },
    },
    {
        "base_id": "b54",
        "topic": "optics",
        "truthful_claim": "A convex lens can focus light rays inward.",
        "note": "Magnifying glasses are a familiar example.",
        "wrong_variants": {
            "entity_swap": "A concave lens can focus light rays inward.",
            "numeric_distortion": "A convex lens can focus two light rays inward.",
            "definition_substitution": "A convex lens can focus sound waves inward.",
            "causal_substitution": "A convex lens can focus light rays inward because glass teaches beams to curve toward the middle.",
            "role_inversion": "Light rays can focus a convex lens inward rather than a convex lens focusing light rays inward.",
        },
    },
    {
        "base_id": "b55",
        "topic": "immunology",
        "truthful_claim": "White blood cells help defend the body against infection.",
        "note": "Different types play different immune roles.",
        "wrong_variants": {
            "entity_swap": "Red blood cells help defend the body against infection.",
            "numeric_distortion": "White blood cells help defend the body against two infections at once.",
            "definition_substitution": "White blood cells help defend the body against dehydration.",
            "causal_substitution": "White blood cells help defend the body against infection because bones pre-label microbes with warning colors.",
            "role_inversion": "The body helps defend white blood cells against infection rather than white blood cells helping defend the body.",
        },
    },
    {
        "base_id": "b56",
        "topic": "seismology",
        "truthful_claim": "An earthquake is a sudden shaking of the ground caused by movement in Earth's crust.",
        "note": "Many earthquakes occur near faults.",
        "wrong_variants": {
            "entity_swap": "A volcano is a sudden shaking of the ground caused by movement in Earth's crust.",
            "numeric_distortion": "An earthquake is a two-stage shaking of the ground caused by movement in Earth's crust.",
            "definition_substitution": "An earthquake is a sudden warming of the ground caused by movement in Earth's crust.",
            "causal_substitution": "An earthquake is a sudden shaking of the ground because mountains release built-up wind through underground chambers.",
            "role_inversion": "Earth's crust is a sudden shaking caused by an earthquake rather than an earthquake being shaking caused by crustal movement.",
        },
    },
    {
        "base_id": "b57",
        "topic": "navigation",
        "truthful_claim": "A compass needle points toward magnetic north.",
        "note": "That direction is not always identical to true geographic north.",
        "wrong_variants": {
            "entity_swap": "A sundial needle points toward magnetic north.",
            "numeric_distortion": "A compass needle points toward two magnetic norths.",
            "definition_substitution": "A compass needle points toward geographic east.",
            "causal_substitution": "A compass needle points toward magnetic north because the map ink pulls it into alignment.",
            "role_inversion": "Magnetic north points toward a compass needle rather than a compass needle pointing toward magnetic north.",
        },
    },
    {
        "base_id": "b58",
        "topic": "education",
        "truthful_claim": "A hypothesis is a testable proposed explanation.",
        "note": "Scientific investigations often begin by comparing hypotheses with evidence.",
        "wrong_variants": {
            "entity_swap": "A conclusion is a testable proposed explanation.",
            "numeric_distortion": "A hypothesis is a two-part testable proposed explanation.",
            "definition_substitution": "A hypothesis is a testable proposed measurement.",
            "causal_substitution": "A hypothesis is a testable proposed explanation because experiments need a sentence to satisfy the lab equipment.",
            "role_inversion": "A testable proposed explanation is a hypothesis for evidence rather than a hypothesis being a proposed explanation.",
        },
    },
    {
        "base_id": "b59",
        "topic": "climatology",
        "truthful_claim": "Greenhouse gases trap some heat in Earth's atmosphere.",
        "note": "That effect helps keep the planet warmer than it would otherwise be.",
        "wrong_variants": {
            "entity_swap": "Oxygen traps some heat in Earth's atmosphere.",
            "numeric_distortion": "Greenhouse gases trap all heat in Earth's atmosphere.",
            "definition_substitution": "Greenhouse gases trap some light in Earth's oceans.",
            "causal_substitution": "Greenhouse gases trap some heat in Earth's atmosphere because the horizon folds sunlight back downward at night.",
            "role_inversion": "Earth's atmosphere traps some greenhouse gases in heat rather than greenhouse gases trapping some heat in the atmosphere.",
        },
    },
    {
        "base_id": "b60",
        "topic": "cell_biology",
        "truthful_claim": "Mitosis is the process by which one cell divides into two daughter cells.",
        "note": "It is part of normal growth and tissue repair.",
        "wrong_variants": {
            "entity_swap": "Meiosis is the process by which one cell divides into two daughter cells.",
            "numeric_distortion": "Mitosis is the process by which one cell divides into three daughter cells.",
            "definition_substitution": "Mitosis is the process by which one cell fuses into two daughter cells.",
            "causal_substitution": "Mitosis is the process by which one cell divides into two daughter cells because chromosomes melt and reassemble around heat gradients.",
            "role_inversion": "Two daughter cells divide into one mitosis rather than one cell dividing into two daughter cells by mitosis.",
        },
    },
]


ANSWER_TEMPLATES = [
    "{claim} {note}",
    "The short answer is: {claim} {note}",
    "A concise response would be that {claim_lc} {note}",
    "In this case, {claim_lc} {note}",
    "The relevant fact is that {claim_lc} {note}",
    "Briefly: {claim_lc} {note}",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a v7 naturalized atlas dataset with expanded base coverage.")
    parser.add_argument(
        "--output",
        default="data/hallucination_diff/raw/qa_pairs_v7_atlas_2026-05-03.json",
        help="Path to write the dataset JSON",
    )
    return parser.parse_args()


def _lower_initial(text: str) -> str:
    if not text:
        return text
    return text[0].lower() + text[1:]


def _render_answer(claim: str, note: str, base_index: int, family_index: int) -> str:
    template = ANSWER_TEMPLATES[(base_index + family_index) % len(ANSWER_TEMPLATES)]
    note_text = note if note.endswith(".") else f"{note}."
    return template.format(claim=claim, claim_lc=_lower_initial(claim), note=note_text)


def build_dataset() -> list[dict[str, str]]:
    all_bases = [*BASES, *EXTRA_BASES, *V7_EXTRA_BASES]
    dataset: list[dict[str, str]] = []
    for base_index, base in enumerate(all_bases):
        wrong_variants = dict(base["wrong_variants"])
        for family_index, family in enumerate(FAMILIES):
            pair_id = f"{base['base_id']}_{family}"
            truthful_answer = _render_answer(
                str(base["truthful_claim"]),
                str(base["note"]),
                base_index,
                family_index,
            )
            hallucinated_answer = _render_answer(
                str(wrong_variants[family]),
                str(base["note"]),
                base_index,
                family_index,
            )
            for label, answer in (
                ("truthful", truthful_answer),
                ("hallucinated", hallucinated_answer),
            ):
                dataset.append(
                    {
                        "sample_id": f"{label}_{pair_id}",
                        "question": GENERIC_QUESTION,
                        "answer": answer,
                        "label": label,
                        "error_family": family,
                        "base_id": str(base["base_id"]),
                        "topic": str(base["topic"]),
                    }
                )
    return dataset


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(build_dataset(), indent=2, ensure_ascii=True), encoding="utf-8")


if __name__ == "__main__":
    main()
