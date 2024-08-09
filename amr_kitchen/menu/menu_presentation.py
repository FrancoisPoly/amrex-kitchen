import re


# Database in {Acronym: (Regular Expression, Definition, Units)} format
field_info = {
    "avg_pressure": r"^avg_pressure$",
    "density": r"^density$",
    "diffcoeff": r"^D_+.",
    "DistributionMap": r"^DistributionMap$",
    "divu": r"^divu$",
    "enstrophy": r"^enstrophy$",
    "FunctCall": r"^FunctCall$",
    "gradp": r"^gradp+\w$",
    "HeatRelease": r"^HeatRelease$",
    "I_R": r"^I_R\(.+\)$",
    "kinetic_energy": r"^kinetic_energy$",
    "lambda": r"^lambda$",
    "mag_vort": r"^mag_vort$",
    "mass_fractions": r"^mass_fractions$",
    "mixture_fraction": r"^mixture_fraction$",
    "mole_fraction": r"^mole_fraction$",
    "progress_variable": r"^progress_variable$",
    "Qcrit": r"^Qcrit$",
    "rhoh": r"^rhoh$",
    "RhoRT": r"^RhoRT$",
    "temp": r"^temp$",
    "velocity": r"^\w+_velocity$",
    "viscosity": r"^viscosity$",
    "volFrac": r"^volFrac$",
    "vorticity": r"^vorticity$",
    "X": r"^X\(.+\)$",
    "Y": r"^Y\(.+\)$",
}


def menu(fields: dict) -> list[str]:
    output = []
    variables = variables_finder(fields)
    output = show_variables(variables, output)

    species = species_finder(fields)
    output = show_species(species, output)

    return output


def show_species(list_species: list[str], output: list[str]) -> list[str]:
    # Let's print the Species
    # Get the length of the string of each species
    sp_lens = [len(sp) for sp in list_species]
    # Amount of spaces padding so each string has the same lenght
    pad = [li + (max(sp_lens) - li) for li in sp_lens]
    sp_padded = [f"{sp: <{p}}" for sp, p in zip(list_species, pad)]
    sp_lines = [" ".join(sp_padded[i: i + 8]) for i in range(0,
                                                             len(sp_padded),
                                                             8)]
    line_lenght = len(sp_lines[0])
    cap = "+" + ("-" * (line_lenght - 2)) + "+"
    title = (line_lenght // 3) * (" ") + "Species found in file:"
    # Printing out the Species on the menu
    output.append(title + "\n")
    output.append(cap + "\n")
    for li in sp_lines:
        output.append(li + "\n")
    output.append(cap)

    return output


def show_variables(list_variables: list[str], output: list[str]) -> list[str]:
    # Let's print the Variables
    # Get the length of the string of each variable
    sp_lens = [len(sp) for sp in list_variables]
    # Amount of spaces padding so each string has the same lenght
    pad = [li + (max(sp_lens) - li) for li in sp_lens]
    sp_padded = [f"{sp: <{p}}" for sp, p in zip(list_variables, pad)]
    field_per_line = 4
    sp_lines = [
        " ".join(sp_padded[i: i + field_per_line])
        for i in range(0, len(sp_padded), field_per_line)
    ]
    line_lenght = len(sp_lines[0])
    cap = "+" + ("-" * (line_lenght - 2)) + "+"
    title = ((line_lenght // 2) - 10) * (" ") + "Fields found in file:"
    # Printing out the variables on the menu
    output.append(title + "\n")
    output.append(cap + "\n")
    for li in sp_lines:
        output.append(li + "\n")
    output.append(cap + "\n" * 2)

    return output


def variables_finder(fields: dict) -> list[str]:
    # Let's find all the fields in the plot file
    list_fields = []
    for field in list(fields):
        for key in field_info:
            regexp = re.compile(field_info[key])
            if regexp.search(field):
                if key not in list_fields:
                    list_fields.append(key)
                    break
                else:
                    break
        # A plot_file's field is not in the database
        else:
            if field not in list_fields:
                list_fields.append(field)
                field_info[field] = field
    list_fields.sort(key=str.lower)
    return list_fields


def species_finder(fields: dict) -> list[str]:
    regexp = re.compile(field_info["Y"])
    Y_species = []
    for field in fields:
        if regexp.search(field):
            Y_species.append(field)
    # Et s'il n'y a aucun Field Y(...) dans la plotfile ??
    Y_species = [re.sub(r"^Y\(", "", sp) for sp in Y_species]
    Y_species = [re.sub(r"\)$", "", sp) for sp in Y_species]
    Y_species.sort()
    return Y_species
