from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptRecord:
    prompt_id: str
    task_family: str
    difficulty: str
    prompt: str

    def as_dict(self) -> dict:
        return {
            "prompt_id": self.prompt_id,
            "task_family": self.task_family,
            "difficulty": self.difficulty,
            "prompt": self.prompt,
        }


def build_arithmetic_records() -> list[PromptRecord]:
    records: list[PromptRecord] = []

    total_then_return = [
        ("easy", "A class collected 14 cans on Monday and 19 on Tuesday. If 6 were damaged and discarded, how many usable cans remained?"),
        ("easy", "A store sold 23 pencils in the morning and 18 in the afternoon. If 7 were returned, how many pencils stayed sold?"),
        ("medium", "A club raised 125 dollars on Friday and 87 dollars on Saturday. If 36 dollars were spent on supplies, how much money remained?"),
        ("medium", "A library checked out 42 books to adults and 31 to children. If 9 books were returned the same day, how many books stayed checked out?"),
        ("hard", "A warehouse shipped 240 boxes in one batch and 175 in another. If 58 boxes came back due to labeling errors, how many boxes remained delivered?"),
    ]
    inverse_ops = [
        ("easy", "A number is multiplied by 3 and then 5 is added to get 26. What is the original number?"),
        ("easy", "A number is doubled and then 9 is subtracted to get 17. What is the original number?"),
        ("medium", "A number is multiplied by 5 and then 12 is added to get 67. What is the original number?"),
        ("medium", "A number is divided by 4 and then 6 is added to get 14. What is the original number?"),
        ("hard", "A number is multiplied by 7, then 11 is subtracted, and the result is 45. What is the original number?"),
    ]
    rate_avg = [
        ("easy", "A car travels 60 km in 1 hour and then 90 km in 2 hours. What is the average speed over the whole trip?"),
        ("easy", "A runner completes 4 km in 20 minutes and then 2 km in 10 minutes. What is the average speed in km per minute?"),
        ("medium", "A train travels 150 km in 3 hours and then 220 km in 4 hours. What is its average speed across the full trip?"),
        ("medium", "A cyclist rides 18 miles in 1.5 hours and then 12 miles in 1 hour. What is the average speed for the entire ride?"),
        ("hard", "A delivery van travels 84 km in 1.5 hours, stops, then travels 126 km in 2.5 hours. Ignoring the stop time, what is the average speed while moving?"),
        ("easy", "A bus travels 40 km in 1 hour and then 80 km in 2 hours. What is the average speed over the whole route?"),
        ("medium", "A boat moves 24 miles in 2 hours and then 18 miles in 1 hour. What is the average speed for the full trip?"),
        ("medium", "A hiker walks 6 km in 1.5 hours and then 10 km in 2.5 hours. What is the average speed across the hike?"),
        ("hard", "A scooter travels 27 miles in 0.75 hours and then 45 miles in 1.25 hours. What is the average speed across both legs?"),
        ("hard", "A truck covers 132 km in 2 hours and then 198 km in 3 hours. What is the average speed for the total distance?"),
    ]
    prompt_groups = [total_then_return, inverse_ops, rate_avg]

    counter = 1
    for group in prompt_groups:
        for difficulty, body in group:
            records.append(
                PromptRecord(
                    prompt_id=f"arith_{counter:03d}",
                    task_family="arithmetic",
                    difficulty=difficulty,
                    prompt=f"Solve step by step: {body}",
                )
            )
            counter += 1
    return records


def build_logic_records() -> list[PromptRecord]:
    statements = [
        ("easy", "If all glims are bloops and some bloops are razs, can we conclude that some glims are razs? Explain carefully."),
        ("easy", "If no kets are lums, and all lums are nops, what follows about the relationship between kets and nops?"),
        ("medium", "If all tars are mivs, and no mivs are pels, can any tar be a pel? Explain why or why not."),
        ("medium", "If some rens are fads and all fads are jops, what can we conclude about some rens?"),
        ("hard", "If every vep that is a zor is also a lin, and no lin is a dax, what follows about any vep that is a zor with respect to dax?"),
        ("easy", "A machine turns on only if both switch A and switch B are on. Switch A is on, but switch B is off. Does the machine turn on?"),
        ("medium", "If passing the exam is sufficient for receiving a certificate, and Mina received no certificate, what can we infer about whether Mina passed?"),
        ("medium", "If being invited is necessary for entering the hall, and Joon entered the hall, what can we infer?"),
        ("hard", "If condition P is necessary but not sufficient for event Q, and P occurred, can we conclude Q occurred?"),
        ("hard", "If either rule X or rule Y must hold for access, and neither holds, what follows about access?"),
        ("easy", "All flerns are sopts. No sopts are drens. Can any flern be a dren?"),
        ("medium", "Some mils are torps. No torps are haves. What follows about some mils?"),
        ("medium", "If all nels are quars and all quars are brims, what follows about nels and brims?"),
        ("hard", "If no zerts are pons and some zerts are laks, what follows about some laks and pons?"),
        ("hard", "If all crols are vents, some vents are darps, and no darps are mels, can we conclude any crol is a mel?"),
        ("easy", "If all sarns are teps and all teps are vons, what follows about sarns and vons?"),
        ("medium", "If some pels are ronts and all ronts are neds, what can we conclude about some pels?"),
        ("medium", "A door opens only if the code is correct and the battery works. The code is correct, but the battery is dead. Does the door open?"),
        ("hard", "If all drims are plens, no plens are skars, and some drims are yals, what follows about some yals and skars?"),
        ("hard", "If being approved is necessary for publishing, and the paper was published, what must be true?"),
    ]
    return [
        PromptRecord(
            prompt_id=f"logic_{idx:03d}",
            task_family="symbolic_logic",
            difficulty=difficulty,
            prompt=f"Reason step by step: {body}",
        )
        for idx, (difficulty, body) in enumerate(statements, start=1)
    ]


def build_temporal_records() -> list[PromptRecord]:
    items = [
        ("easy", "Mina arrived before Joon. Joon arrived after Sora. Who arrived first?"),
        ("easy", "Event A happened before Event B, and Event B happened before Event C. Which event happened last?"),
        ("medium", "Event A happened after Event B but before Event C. Event D happened before Event B. Order the four events from earliest to latest."),
        ("medium", "A meeting started after breakfast but before lunch. A phone call happened before breakfast. Put the events in order."),
        ("hard", "Task W finished after Task X but before Task Y. Task Z finished before Task X. Order all tasks from earliest to latest."),
        ("easy", "Jisoo left home after Minho but before Ara. Who left earliest?"),
        ("medium", "Chapter 3 was read after Chapter 1 but before Chapter 4. Chapter 2 was read after Chapter 1 and before Chapter 3. Order the chapters."),
        ("medium", "The seed sprouted after planting but before the first leaf appeared. Rain came before planting. Order the events."),
        ("hard", "Machine check happened before startup. Startup happened before warmup. Calibration happened after warmup. Put all four stages in order."),
        ("hard", "Concert rehearsal ended before dinner. Ticket check happened before rehearsal. Cleanup happened after dinner. Order the events."),
        ("easy", "Nari finished before Daeho, and Daeho finished before Sujin. Who finished second?"),
        ("medium", "Package scanning happened after pickup but before sorting. Delivery happened after sorting. Order the package stages."),
        ("medium", "The alarm rang before the lights turned on. Breakfast came after the lights turned on. What was the order?"),
        ("hard", "Inspection happened before repair, repair before testing, and shipping after testing. Place the events in order."),
        ("hard", "Warmup was after registration, the main event was after warmup, and awards were after the main event. Which event was second?"),
        ("easy", "Hana ate lunch after class but before practice. What happened in the middle?"),
        ("medium", "Registration came before orientation, orientation before training, and training before evaluation. Order the events."),
        ("medium", "The bell rang after the students sat down but before the lecture began. What was the order?"),
        ("hard", "Drafting happened before review, review before revision, and submission after revision. Put the writing stages in order."),
        ("hard", "Boarding happened after security, security after check-in, and takeoff after boarding. Which stage was third?"),
    ]
    return [
        PromptRecord(
            prompt_id=f"temporal_{idx:03d}",
            task_family="temporal_ordering",
            difficulty=difficulty,
            prompt=f"Reason step by step: {body}",
        )
        for idx, (difficulty, body) in enumerate(items, start=1)
    ]


def build_causal_records() -> list[PromptRecord]:
    items = [
        ("easy", "In a toy ecosystem, when rainfall drops, plant growth falls. When plant growth falls, rabbit population later falls. If rainfall drops this month, what likely happens next over the following steps?"),
        ("easy", "A circuit's alarm triggers only if both the sensor fails and the backup is off. The sensor failed, but the backup stayed on. Does the alarm trigger?"),
        ("medium", "When road ice increases, vehicle speed decreases. When vehicle speed decreases, traffic delay increases. If overnight temperatures fall below freezing, what chain of effects is likely?"),
        ("medium", "If water temperature rises, dissolved oxygen falls. When dissolved oxygen falls, fish stress rises. What likely happens after a heat spike in the pond?"),
        ("hard", "In a toy market, when supply drops, price rises. When price rises sharply, demand later softens. If a factory shutdown reduces supply, what sequence is most likely?"),
        ("easy", "A lamp turns on only if power is available and the bulb is working. Power is available, but the bulb is broken. What happens?"),
        ("medium", "If the server overheats, processing slows. If processing slows, request backlog grows. If cooling fails, what happens next?"),
        ("medium", "When soil dries, plants wilt. When plants wilt, shade coverage decreases. If a drought continues, what later change is expected?"),
        ("hard", "If upstream contamination rises, downstream filtration load rises. If filtration load rises too far, output purity falls. What follows from a major upstream spill?"),
        ("hard", "In a toy chemistry setup, if reactant A is missing, product B is not formed. If product B is not formed, the indicator stays blue. If reactant A is absent, what happens?"),
        ("easy", "If a freezer loses power, ice begins melting. If ice melts, water collects at the bottom. What is the likely sequence after power loss?"),
        ("medium", "If study time increases, test readiness increases. If test readiness increases, error rate falls. What follows from a sustained increase in study time?"),
        ("medium", "When fuel pressure drops, engine output falls. When engine output falls, climb rate falls. What follows after a fuel line blockage?"),
        ("hard", "If guardrails are removed, accident risk rises. If accident risk rises, insurance cost later rises. What long-term effect is expected after removal?"),
        ("hard", "If incoming packets spike, queue length rises. If queue length rises too much, latency increases. What follows from a sudden burst of traffic?"),
        ("easy", "If the heater stops, room temperature falls. If room temperature falls far enough, pipes may freeze. What follows after heater failure?"),
        ("medium", "If fertilizer is reduced, plant growth slows. If growth slows, harvest size later shrinks. What follows from reduced fertilizer?"),
        ("medium", "If brake pressure leaks, stopping distance grows. If stopping distance grows, collision risk rises. What follows from a brake leak?"),
        ("hard", "If reservoir level drops, turbine output falls. If turbine output falls, regional power shortages may increase. What follows from drought conditions?"),
        ("hard", "If database locks increase, transaction throughput falls. If throughput falls, user wait time rises. What follows from heavy lock contention?"),
    ]
    return [
        PromptRecord(
            prompt_id=f"causal_{idx:03d}",
            task_family="causal_micro_world",
            difficulty=difficulty,
            prompt=f"Reason step by step: {body}",
        )
        for idx, (difficulty, body) in enumerate(items, start=1)
    ]


def build_commonsense_records() -> list[PromptRecord]:
    items = [
        ("easy", "A person left an ice cube on a metal tray under the sun. After an hour, the tray was wet. What most likely happened, and why was the tray wet?"),
        ("easy", "A chef forgot to put dough in the oven but later found it larger in the warm kitchen. Why might it have become larger even though it was not baked?"),
        ("medium", "Someone brought an umbrella outside in the morning and returned with wet shoes but a dry shirt. What likely happened?"),
        ("medium", "A phone was left charging overnight, but in the morning it had little battery. What is a plausible explanation?"),
        ("hard", "A glass bottle taken from the refrigerator became wet on the outside within minutes. Why did that happen even though the inside liquid stayed sealed?"),
        ("easy", "A person put popcorn kernels in hot oil, and later the pot was full of fluffy popcorn. What caused the change?"),
        ("medium", "A cyclist's shadow became shorter as noon approached. Why did the shadow length change?"),
        ("medium", "A wooden spoon placed in soup became warm after a few minutes. How did that happen?"),
        ("hard", "A closed parked car became hotter inside than the outdoor air on a sunny day. Why can that happen?"),
        ("hard", "A wet towel dried faster when spread out than when left folded. Why?"),
        ("easy", "A person wore glasses when entering from the cold and the lenses turned foggy indoors. Why?"),
        ("medium", "Bread became hard after being left on the counter overnight. What likely changed?"),
        ("medium", "Salt was added to icy pavement and the ice later melted more quickly. Why might salt help?"),
        ("hard", "A metal spoon and a plastic spoon were both left in hot tea, but only one became hot quickly. Why?"),
        ("hard", "After a long run, a runner kept breathing hard even after stopping. Why would breathing remain elevated?"),
        ("easy", "A mirror in a bathroom became cloudy after a hot shower. Why did that happen?"),
        ("medium", "A sealed bag of chips puffed up on an airplane. Why might the bag expand during the flight?"),
        ("medium", "Soup cooled faster when poured into a wide bowl than when left in a deep mug. Why?"),
        ("hard", "A black car parked in sunlight became hotter than a white car nearby. What is a plausible explanation?"),
        ("hard", "A dropped egg broke on concrete but not on a thick cushion. Why did the outcomes differ?"),
    ]
    return [
        PromptRecord(
            prompt_id=f"commonsense_{idx:03d}",
            task_family="commonsense_multihop",
            difficulty=difficulty,
            prompt=f"Reason step by step: {body}",
        )
        for idx, (difficulty, body) in enumerate(items, start=1)
    ]


def build_prompt_bank() -> list[PromptRecord]:
    records: list[PromptRecord] = []
    for builder in [
        build_arithmetic_records,
        build_logic_records,
        build_temporal_records,
        build_causal_records,
        build_commonsense_records,
    ]:
        records.extend(builder())
    return records
