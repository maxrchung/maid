from storyboard import RotateCommand

def generate_variables(materials, storyboard):
    rotate_counts = {}

    for sprite in storyboard.sprites:
        for command in sprite.commands:
            if isinstance(command, RotateCommand):
                key = f"{command.start}_{command.end}"
                if key in rotate_counts:
                    rotate_counts[key]["count"] += 1
                else:
                    rotate_counts[key] = {
                        "command": command,
                        "count": 0,
                    }

    # Sort by highest count so one-byte replacements are used more
    sorted_counts = sorted(
        rotate_counts.values(),
        key=lambda item: item["count"],
        reverse=True
    )

    variables = []
    code_point = 0
    added = set()

    def add_variable(value):
        nonlocal code_point
        if value in added:
            return
        added.add(value)

        key = "$" + chr(code_point)
        variables.append((key, value))

        code_point += 1

        # Skip some characters that breaks things...
        while code_point in (
            10,  # \n
            13,  # \r
            36,  # $
            38,  # &
            39,  # '
            61,  # =
            96,  # `
        ):
            code_point += 1

    # Sprite declarations
    for file in materials.values():
        add_variable(f"4,0,0,{file},")

    for entry in sorted_counts:
        command = entry["command"]
        # Rotate has start and end
        add_variable(f" R,0,{round(command.start)},{round(command.end)},")
        # Scale only has start
        add_variable(f" V,0,{round(command.start)},,")

    return variables

