import re


# Database in {Acronym: (Regular Expression, Definition, Units)} format
field_info = {
    "avg_pressure": (
        r"^avg_pressure$",
        "Cell-averaged pressure from the node-centers ",
        "[Pa]",
    ),
    "density": (r"^density$", "Density ", "[kg/m^3]"),
    "diffcoeff": (
        r"^D_+.",
        "Mixture-averaged diffusion coefficients (mass) ",
        "[m^2/s]",
    ),
    "DistributionMap": (
        r"^DistributionMap$",
        "The MPI-rank of each box ",
        "[-]"
    ),
    "divu": (r"^divu$", "Divergence of the velocity field ", "[1 / s]"),
    "enstrophy": (
        r"^enstrophy$",
        "Enstrophy as 0.5 * Rho * |omega^2| ",
        "[kg / m s^2]",
    ),
    "FunctCall": (
        r"^FunctCall$",
        "Number of function calls to chemistry ",
        "[-]"
    ),
    "gradp": (r"^gradp+\w$", "Local pressure gradient ", "[Pa / m]"),
    "HeatRelease": (
        r"^HeatRelease$",
        "Heat release rate from chem. reactions ",
        "[W / m^3]",
    ),
    "I_R": (r"^I_R\(.+\)$", "Species reaction rates ", "[kg / s m^3]"),
    "kinetic_energy": (
        r"^kinetic_energy$",
        "Kinetic energy as 0.5 * Rho * |U^2| ",
        "[kg / m s^2]",
    ),
    "lambda": (r"^lambda$", "Thermal diffusivity ", "[W / m / K]"),
    "mag_vort": (r"^mag_vort$", "Vorticity magnitude ", "[1 / s]"),
    "mass_fractions": (r"^mass_fractions$", "Species mass fractions ", "[-]"),
    "mixture_fraction": (
        r"^mixture_fraction$",
        "Mixture fraction based on Bilger’s formulation ",
        "[-]",
    ),
    "mole_fraction": (r"^mole_fraction$", "Species mole fractions ", "[-]"),
    "progress_variable": (
        r"^progress_variable$",
        "User defined progress variable ",
        "[-]",
    ),
    "Qcrit": (r"^Qcrit$", "Q-Criterion ", "[-]"),
    "rhoh": (r"^rhoh$", "Density * Specific Enthalpy ", "[J / m^3]"),
    "RhoRT": (r"^RhoRT$", "Density * (R / M_bar) * Temperature ", "[Pa]"),
    "temp": (r"^temp$", "Temperature ", "[K]"),
    "velocity": (r"^\w+_velocity$", "Velocity ", "[m/s]"),
    "viscosity": (r"^viscosity$", "Mixture viscosity ", "[Pa-s]"),
    "volFrac": (
        r"^volFrac$",
        "Volume fraction at embedded boundaries ",
        "[-]"
        ),
    "vorticity": (r"^vorticity$", "Vortricity components ", "[1 / s]"),
    "X": (r"^X\(.+\)$", "Species mole fractions ", "[-]"),
    "Y": (r"^Y\(.+\)$", "Species mass fractions ", "[-]"),
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
            regexp = re.compile(field_info[key][0])
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
                field_info[field] = (field, "Units unknown", "[...]")
    list_fields.sort(key=str.lower)
    return list_fields


def species_finder(fields: dict) -> list[str]:
    regexp = re.compile(field_info["Y"][0])
    Y_species = []
    for field in fields:
        if regexp.search(field):
            Y_species.append(field)
    # Et s'il n'y a aucun Field Y(...) dans la plotfile ??
    Y_species = [re.sub(r"^Y\(", "", sp) for sp in Y_species]
    Y_species = [re.sub(r"\)$", "", sp) for sp in Y_species]
    Y_species.sort()
    return Y_species
