import json
import math

# load relevant json data
with open('rs_levels.json', 'r') as f:
    levels = json.load(f)

with open('tier_multipliers.json', 'r') as f:
    leagues_multipliers = json.load(f)

with open('rs_birdhouses.json', 'r') as f:
    base_birdhouses = json.load(f)

# recast the keys in the levels and tier dictionaries from strings to integers
levels = {int(key): value for key, value in levels.items()}
leagues_multipliers = {int(key): value for key, value in leagues_multipliers.items()}


def check_level(xp_to_check):
    """
    Determines the player's level based on their current XP.

    Args:
        xp_to_check (int): The player's current XP.

    Returns:
        int: The level corresponding to the given XP.
    """
    for level, experience in levels.items():
        if xp_to_check < experience:
            return level - 1  # Return the previous level if XP is less than required
    # If XP is greater than or equal to the maximum XP, return level 99
    return max(levels.keys())


def check_birdhouse_tier(level, birdhouses):
    """
    Determines the current birdhouse tier and the next tier the player can unlock.

    Args:
        level (int): The player's current Hunter level.
        birdhouses (dict): Dictionary of birdhouse data.

    Returns:
        tuple: The current birdhouse tier and the next tier (or None if there is no next tier).
    """
    current_tier = "None"
    for tier, tier_level in birdhouses.items():
        if level < tier_level['Hunter Level']:
            return current_tier, tier
        current_tier = tier
    return current_tier, None


def calc_trips_to_next_benchmark(current_xp, target_level, birdhouses):
    """
    Calculates the number of trips needed to reach the next XP benchmark.

    Args:
        current_xp (int): The player's current XP.
        target_level (int): The target level to calculate trips for.
        birdhouses (dict): Dictionary of birdhouse data.

    Returns:
        tuple: Total trips, total logs needed, and the resulting XP after the trips.
    """
    # XP needed to reach the target level
    xp_to_target = levels[target_level] - current_xp

    # Get the current level and birdhouse tier
    current_level = check_level(current_xp)
    birdhouse_tier = check_birdhouse_tier(current_level, birdhouses)[0]

    # Calculate XP per trip (4 birdhouses per trip)
    trip_xp = birdhouses[birdhouse_tier]['Hunter XP'] * 4

    # Calculate total trips needed
    total_trips = math.ceil(xp_to_target / trip_xp)

    # Calculate total XP gain and logs needed
    xp_gain = total_trips * trip_xp
    end_xp = xp_gain + current_xp
    logs_needed = total_trips * 4

    return total_trips, logs_needed, end_xp


def format_logs(birdhouse_tier, logs_needed):
    """
    Formats the logs needed for a given birdhouse tier.

    Args:
        birdhouse_tier (str): The current birdhouse tier.
        logs_needed (int): The number of logs needed.

    Returns:
        dict: A dictionary with the log type and count.
    """
    # Extract the log type from the birdhouse tier
    log_tier = birdhouse_tier.split(" ")[0]

    # Format the log count
    return {f"{log_tier} logs": logs_needed}


def calc_trips_to_target(current_xp, target_level, birdhouses):
    """
    Calculates the full training path from the current XP to the target level.

    Args:
        current_xp (int): The player's starting XP.
        target_level (int): The target level to reach.
        birdhouses (dict): Dictionary of birdhouse data.

    Returns:
        list: A list of dictionaries detailing the logs needed for each birdhouse tier.
    """
    logs_to_target = []  # List to store log requirements for each tier
    current_level = check_level(current_xp)  # Determine the starting level

    while current_level < target_level:  # Continue until the target level is reached
        # Get the current and next birdhouse tiers
        current_tier, next_tier = check_birdhouse_tier(current_level, birdhouses)

        # Determine the XP needed for the next benchmark (next tier or target level)
        if next_tier is None or target_level < birdhouses[next_tier]['Hunter Level']:
            next_benchmark = levels[target_level]
        else:
            next_benchmark = levels[birdhouses[next_tier]['Hunter Level']]

        # Calculate trips, logs needed, and XP gain
        birdhouse_xp = birdhouses[current_tier]['Hunter XP'] * 4
        trips = math.ceil((next_benchmark - current_xp) / birdhouse_xp)
        xp_gain = trips * birdhouse_xp
        current_xp += xp_gain  # Update XP
        logs_needed = trips * 4  # Calculate logs needed

        # Add the logs needed for this tier to the result
        logs_to_target.append(format_logs(current_tier, logs_needed))

        # Update the player's level based on the new XP
        current_level = check_level(current_xp)

    return logs_to_target


def get_inputs():
    """
    Collects user input for current XP and target level.

    Returns:
        tuple: The player's current XP and target level, or (None, None) if invalid input.
    """
    while True:
        experience = input("What is your current Hunter xp? (Example: 2224614) ")
        try:
            experience = int(experience)
            if experience < levels[5]:
                print("You need at least 5 Hunter to make a birdhouse.")
                return None, None
        except TypeError:
            print("Sorry, try entering a whole number.")
        target_level = input("What is your target Hunter level? (Example: 99) ")
        try:
            target_level = int(target_level)
            if experience > levels[target_level]:
                print("You've already passed your target.")
                return None, None
            return experience, target_level
        except TypeError:
            print("Sorry, try entering a whole number.")


def check_leagues():
    """
    Asks the user if they are playing in Leagues mode.

    Returns:
        bool: True if Leagues mode is active, False otherwise.
    """
    check = input("Type 1 if this is Leagues. ")
    if check == "1":
        return True
    else:
        return False


def get_relic_multiplier():
    """
    Collects the XP multiplier based on the user's Leagues tier.

    Returns:
        int: The XP multiplier tier.
    """
    while True:
        tier = input("What tier have you unlocked? (1-7) ")
        try:
            tier = int(tier)
            if 1 > tier or tier > 7:
                print("Please enter an integer between 1 and 7.")
            else:
                return tier
        except TypeError:
            print("Please enter an integer between 1 and 7.")


def display_plan(starting_xp, train_path):
    """
    Displays the calculated training plan to the user.

    Args:
        starting_xp (int): The starting XP of the user.
        train_path (list): The calculated training path.
    """
    print(f"\nStarting from {starting_xp}xp, you will need:\n")
    for tier in train_path:
        for logs, amount in tier.items():
            print(f"{amount} {logs} ")


def main():
    start_xp, end_level = get_inputs()  # Get user input
    leagues_flag = check_leagues()
    if leagues_flag:
        relic_tier = get_relic_multiplier()
        multiplier = leagues_multipliers[relic_tier]
        print(f"Your XP modifier is {multiplier}")
        birdhouses = {key: {k: (v * multiplier if k == "Hunter XP" else v) for k, v in value.items()}
                      for key, value in base_birdhouses.items()}
    else:
        birdhouses = base_birdhouses
    if end_level:
        training_path = calc_trips_to_target(start_xp, end_level, birdhouses)
        display_plan(start_xp, training_path)


if __name__ == "__main__":
    main()
