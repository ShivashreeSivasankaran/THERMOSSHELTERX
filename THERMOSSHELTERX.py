import streamlit as st
import numpy as np
import pandas as pd
import math


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="THERMOS SHELTERX",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PROFESSIONAL MIDNIGHT BLUE / CLASSIC BLUE THEME
# ============================================================

st.markdown("""
<style>

    /* -------------------------------------------------------
       GLOBAL APPLICATION
    ------------------------------------------------------- */

    .stApp {
        background-color: #0B1220;
        color: #E8EEF7;
    }

    .main {
        background-color: #0B1220;
    }

    /* -------------------------------------------------------
       SIDEBAR
    ------------------------------------------------------- */

    section[data-testid="stSidebar"] {
        background-color: #101B30;
        border-right: 1px solid #263B5A;
    }

    section[data-testid="stSidebar"] * {
        color: #E8EEF7;
    }

    /* -------------------------------------------------------
       HEADINGS
    ------------------------------------------------------- */

    h1 {
        color: #FFFFFF !important;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    h2 {
        color: #DCE8F7 !important;
        font-weight: 650;
    }

    h3 {
        color: #C8D8EB !important;
        font-weight: 600;
    }

    /* -------------------------------------------------------
       NORMAL TEXT
    ------------------------------------------------------- */

    p, label, span {
        color: #D5DFEC;
    }

    /* -------------------------------------------------------
       INPUTS
    ------------------------------------------------------- */

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        background-color: #16243A;
        border: 1px solid #304866;
        border-radius: 6px;
    }

    input {
        color: #FFFFFF !important;
    }

    div[data-baseweb="select"] span {
        color: #FFFFFF !important;
    }

    /* -------------------------------------------------------
       BUTTONS
    ------------------------------------------------------- */

    .stButton > button {
        background-color: #1E5AA8;
        color: #FFFFFF;
        border: none;
        border-radius: 6px;
        padding: 0.65rem 1rem;
        font-weight: 600;
        transition: 0.2s;
    }

    .stButton > button:hover {
        background-color: #2874C7;
        color: #FFFFFF;
    }

    /* -------------------------------------------------------
       DOWNLOAD BUTTON
    ------------------------------------------------------- */

    .stDownloadButton > button {
        background-color: #162F52;
        color: #FFFFFF;
        border: 1px solid #2E5F91;
        border-radius: 6px;
        font-weight: 600;
    }

    .stDownloadButton > button:hover {
        background-color: #1E5AA8;
        color: #FFFFFF;
    }

    /* -------------------------------------------------------
       METRIC CARDS
    ------------------------------------------------------- */

    div[data-testid="stMetric"] {
        background-color: #111D31;
        border: 1px solid #263B5A;
        border-radius: 8px;
        padding: 16px;
    }

    div[data-testid="stMetricLabel"] {
        color: #9FB2C9 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: 700;
    }

    /* -------------------------------------------------------
       ALERT BOXES
    ------------------------------------------------------- */

    div[data-testid="stAlert"] {
        background-color: #111D31;
        border: 1px solid #2B4E75;
        color: #DCE8F7;
    }

    /* -------------------------------------------------------
       DIVIDERS
    ------------------------------------------------------- */

    hr {
        border-color: #263B5A;
    }

    /* -------------------------------------------------------
       EXPANDERS
    ------------------------------------------------------- */

    details {
        background-color: #111D31;
        border: 1px solid #263B5A;
        border-radius: 7px;
    }

    /* -------------------------------------------------------
       DATAFRAMES
    ------------------------------------------------------- */

    div[data-testid="stDataFrame"] {
        border: 1px solid #263B5A;
        border-radius: 6px;
    }

    /* -------------------------------------------------------
       SLIDERS
    ------------------------------------------------------- */

    div[data-baseweb="slider"] {
        color: #1E5AA8;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# MATERIAL DATABASE
# ============================================================

MATERIALS = {

    "80 mm PUF Sandwich Panel": {
        "thickness": 0.080,
        "k": 0.023,
        "density": 40,
        "cp": 1400,
        "description": "Polyurethane foam insulated sandwich panel"
    },

    "60 mm PUF Sandwich Panel": {
        "thickness": 0.060,
        "k": 0.023,
        "density": 40,
        "cp": 1400,
        "description": "Polyurethane foam insulated sandwich panel"
    },

    "80 mm PIR Sandwich Panel": {
        "thickness": 0.080,
        "k": 0.022,
        "density": 35,
        "cp": 1400,
        "description": "Polyisocyanurate insulated sandwich panel"
    },

    "100 mm PUF Sandwich Panel": {
        "thickness": 0.100,
        "k": 0.023,
        "density": 40,
        "cp": 1400,
        "description": "High-performance polyurethane insulated panel"
    }
}


# ============================================================
# FUNCTIONS
# ============================================================

def roof_geometry(length, width, height):
    """
    Calculates roof area for a 1:2 roof slope.
    """

    half_span = width / 2
    rise = half_span / 2

    sloped_length = math.sqrt(
        half_span ** 2 + rise ** 2
    )

    roof_area = 2 * length * sloped_length

    return roof_area


def calculate_u_value(thickness, conductivity):
    """
    Calculates U-value including surface resistances.
    """

    Rsi = 0.13
    Rse = 0.04

    resistance = (
        Rsi +
        thickness / conductivity +
        Rse
    )

    return 1 / resistance


def outdoor_temperature(hour, t_min, t_max):
    """
    Representative 24-hour outdoor temperature profile.

    Minimum occurs around early morning.
    Maximum occurs during afternoon.
    """

    phase = (hour - 6) / 24 * 2 * np.pi

    temperature = (
        (t_min + t_max) / 2
        +
        (t_max - t_min) / 2 * np.sin(phase)
    )

    return temperature


def solar_irradiance(hour, peak_irradiance):
    """
    Simplified daylight solar profile.
    """

    if hour < 6 or hour > 18:
        return 0

    angle = math.pi * (hour - 6) / 12

    return peak_irradiance * math.sin(angle)


def calculate_thermal_mass(
    wall_area,
    roof_area,
    floor_area,
    material,
    floor_thickness
):
    """
    Approximate effective thermal capacity.

    Includes:
    - wall insulation
    - roof insulation
    - floor insulation
    - indoor air
    """

    density = material["density"]
    cp = material["cp"]

    wall_mass = (
        wall_area *
        material["thickness"] *
        density
    )

    roof_mass = (
        roof_area *
        material["thickness"] *
        density
    )

    floor_mass = (
        floor_area *
        floor_thickness *
        density
    )

    insulation_mass = (
        wall_mass +
        roof_mass +
        floor_mass
    )

    insulation_capacity = (
        insulation_mass *
        cp
    )

    return insulation_capacity


# ============================================================
# APPLICATION HEADER
# ============================================================

st.title("THERMOS SHELTERX")

st.markdown(
    """
    **Thermal Performance Analysis System for High-Altitude Shelters**

    A software-based engineering model for analysing indoor
    temperature, heat transfer, insulation performance and
    thermal energy requirements under Ladakh-like climatic
    conditions.
    """
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("THERMOS SHELTERX")
st.sidebar.markdown("Simulation Parameters")
st.sidebar.divider()


# ============================================================
# SHELTER GEOMETRY
# ============================================================

st.sidebar.subheader("Shelter Geometry")

length = st.sidebar.number_input(
    "Shelter Length (m)",
    min_value=2.0,
    max_value=30.0,
    value=15.0,
    step=0.1
)

width = st.sidebar.number_input(
    "Shelter Width (m)",
    min_value=2.0,
    max_value=15.0,
    value=6.0,
    step=0.1
)

height = st.sidebar.number_input(
    "Wall Height (m)",
    min_value=2.0,
    max_value=8.0,
    value=4.0,
    step=0.1
)

roof_slope = st.sidebar.selectbox(
    "Roof Configuration",
    [
        "1:2 Sloped Roof",
        "Flat Roof"
    ]
)


# ============================================================
# INSULATION
# ============================================================

st.sidebar.subheader("Insulation")

material_name = st.sidebar.selectbox(
    "Wall and Roof Insulation",
    list(MATERIALS.keys()),
    index=0
)

material = MATERIALS[material_name]

thickness_mm = st.sidebar.slider(
    "Insulation Thickness (mm)",
    min_value=40,
    max_value=150,
    value=int(material["thickness"] * 1000),
    step=10
)

insulation_thickness = thickness_mm / 1000

k_value = material["k"]


# ============================================================
# OPENINGS
# ============================================================

st.sidebar.subheader("Openings")

window_area = st.sidebar.number_input(
    "Total Window Area (m²)",
    min_value=0.0,
    max_value=50.0,
    value=4.0,
    step=0.5
)

door_area = st.sidebar.number_input(
    "Door Area (m²)",
    min_value=0.0,
    max_value=20.0,
    value=2.0,
    step=0.5
)

window_u = st.sidebar.number_input(
    "Window U-value (W/m²K)",
    min_value=0.5,
    max_value=6.0,
    value=2.5,
    step=0.1
)

door_u = st.sidebar.number_input(
    "Door U-value (W/m²K)",
    min_value=0.5,
    max_value=6.0,
    value=1.5,
    step=0.1
)


# ============================================================
# CLIMATE CONDITIONS
# ============================================================

st.sidebar.subheader("External Climate")

outdoor_min = st.sidebar.number_input(
    "Minimum Outdoor Temperature (°C)",
    min_value=-50.0,
    max_value=10.0,
    value=-20.0,
    step=1.0
)

outdoor_max = st.sidebar.number_input(
    "Maximum Outdoor Temperature (°C)",
    min_value=-30.0,
    max_value=20.0,
    value=-5.0,
    step=1.0
)

solar_peak = st.sidebar.slider(
    "Peak Solar Irradiance (W/m²)",
    min_value=100,
    max_value=1000,
    value=450,
    step=25
)

ach = st.sidebar.slider(
    "Air Changes per Hour (ACH)",
    min_value=0.1,
    max_value=3.0,
    value=0.5,
    step=0.1
)


# ============================================================
# HEAT SOURCES
# ============================================================

st.sidebar.subheader("Thermal Energy Supply")

geothermal_power = st.sidebar.slider(
    "Geothermal Heat Supply (kW)",
    min_value=0.0,
    max_value=20.0,
    value=3.0,
    step=0.5
)

occupants = st.sidebar.number_input(
    "Number of Occupants",
    min_value=0,
    max_value=50,
    value=4,
    step=1
)

equipment_power = st.sidebar.slider(
    "Internal Equipment Load (kW)",
    min_value=0.0,
    max_value=5.0,
    value=0.5,
    step=0.1
)


# ============================================================
# THERMAL STORAGE
# ============================================================

st.sidebar.subheader("Thermal Storage")

storage_enabled = st.sidebar.checkbox(
    "Enable Thermal Storage",
    value=True
)

if storage_enabled:

    storage_capacity = st.sidebar.number_input(
        "Storage Capacity (kWh)",
        min_value=0.0,
        max_value=500.0,
        value=50.0,
        step=5.0
    )

    initial_storage = st.sidebar.slider(
        "Initial Storage Level (%)",
        min_value=0,
        max_value=100,
        value=50,
        step=5
    )

    storage_efficiency = st.sidebar.slider(
        "Storage Efficiency (%)",
        min_value=50,
        max_value=100,
        value=90,
        step=5
    ) / 100

else:

    storage_capacity = 0
    initial_storage = 0
    storage_efficiency = 1


# ============================================================
# INITIAL INDOOR CONDITIONS
# ============================================================

st.sidebar.subheader("Initial Conditions")

initial_temp = st.sidebar.number_input(
    "Initial Indoor Temperature (°C)",
    min_value=-10.0,
    max_value=40.0,
    value=18.0,
    step=0.5
)


# ============================================================
# SIMULATION BUTTON
# ============================================================

st.sidebar.divider()

run = st.sidebar.button(
    "RUN SIMULATION",
    use_container_width=True
)


# ============================================================
# MAIN INFORMATION PANEL
# ============================================================

st.info(
    "Default geometry is based on a reference high-altitude "
    "prefabricated shelter configuration. Material properties "
    "are representative engineering values and should be "
    "replaced with manufacturer-certified data for final design."
)


# ============================================================
# RUN SIMULATION
# ============================================================

if run:

    # --------------------------------------------------------
    # GEOMETRY
    # --------------------------------------------------------

    floor_area = length * width

    wall_area_total = (
        2 * (length + width) * height
    )

    wall_area = max(
        wall_area_total - window_area - door_area,
        0.1
    )

    if roof_slope == "1:2 Sloped Roof":

        roof_area = roof_geometry(
            length,
            width,
            height
        )

    else:

        roof_area = floor_area


    volume = (
        length *
        width *
        height
    )


    # --------------------------------------------------------
    # FLOOR INSULATION
    # --------------------------------------------------------

    floor_thickness = 0.060


    # --------------------------------------------------------
    # U VALUES
    # --------------------------------------------------------

    wall_u = calculate_u_value(
        insulation_thickness,
        k_value
    )

    roof_u = calculate_u_value(
        insulation_thickness,
        k_value
    )

    floor_u = calculate_u_value(
        floor_thickness,
        k_value
    )


    # --------------------------------------------------------
    # THERMAL MASS
    # --------------------------------------------------------

    thermal_capacity = calculate_thermal_mass(
        wall_area,
        roof_area,
        floor_area,
        material,
        floor_thickness
    )

    # Air thermal capacity
    air_density = 1.225
    air_cp = 1005

    air_capacity = (
        volume *
        air_density *
        air_cp
    )

    total_capacity = (
        thermal_capacity +
        air_capacity
    )

    # Prevent numerical instability
    total_capacity = max(
        total_capacity,
        500000
    )


    # --------------------------------------------------------
    # STORAGE INITIAL STATE
    # --------------------------------------------------------

    storage_level = (
        storage_capacity *
        initial_storage /
        100
    )


    # --------------------------------------------------------
    # SIMULATION ARRAYS
    # --------------------------------------------------------

    hours = np.arange(0, 24, 1)

    indoor_temps = []
    outdoor_temps = []

    wall_losses = []
    roof_losses = []
    floor_losses = []
    opening_losses = []
    ventilation_losses = []

    solar_gains = []
    occupant_gains = []
    equipment_gains = []
    geothermal_gains = []
    storage_gains = []

    total_heat_loss = []
    total_heat_gain = []
    storage_levels = []


    # Current indoor temperature
    indoor_temp = initial_temp


    # --------------------------------------------------------
    # 24-HOUR SIMULATION
    # --------------------------------------------------------

    for hour in hours:

        outdoor_temp = outdoor_temperature(
            hour,
            outdoor_min,
            outdoor_max
        )

        solar = solar_irradiance(
            hour,
            solar_peak
        )

        delta_t = indoor_temp - outdoor_temp


        # ----------------------------------------------------
        # HEAT LOSS THROUGH WALLS
        # ----------------------------------------------------

        wall_loss = (
            wall_u *
            wall_area *
            delta_t
        ) / 1000


        # ----------------------------------------------------
        # HEAT LOSS THROUGH ROOF
        # ----------------------------------------------------

        roof_loss = (
            roof_u *
            roof_area *
            delta_t
        ) / 1000


        # ----------------------------------------------------
        # HEAT LOSS THROUGH FLOOR
        # ----------------------------------------------------

        floor_loss = (
            floor_u *
            floor_area *
            delta_t
        ) / 1000


        # ----------------------------------------------------
        # HEAT LOSS THROUGH WINDOWS AND DOORS
        # ----------------------------------------------------

        opening_loss = (
            (
                window_u * window_area
            )
            +
            (
                door_u * door_area
            )
        ) * delta_t / 1000


        # ----------------------------------------------------
        # VENTILATION / INFILTRATION LOSS
        # ----------------------------------------------------

        ventilation_loss = (
            0.33 *
            ach *
            volume *
            delta_t
        ) / 1000


        # ----------------------------------------------------
        # TOTAL HEAT LOSS
        # ----------------------------------------------------

        heat_loss = (
            wall_loss +
            roof_loss +
            floor_loss +
            opening_loss +
            ventilation_loss
        )

        heat_loss = max(
            heat_loss,
            0
        )


        # ----------------------------------------------------
        # SOLAR HEAT GAIN
        # ----------------------------------------------------

        shgc = 0.65

        solar_gain = (
            window_area *
            solar *
            shgc
        ) / 1000


        # ----------------------------------------------------
        # OCCUPANT HEAT GAIN
        # ----------------------------------------------------

        occupant_gain = (
            occupants *
            0.075
        )


        # ----------------------------------------------------
        # EQUIPMENT HEAT GAIN
        # ----------------------------------------------------

        equipment_gain = equipment_power


        # ----------------------------------------------------
        # GEOTHERMAL HEAT
        # ----------------------------------------------------

        geothermal_gain = geothermal_power


        # ----------------------------------------------------
        # NET HEAT BEFORE STORAGE
        # ----------------------------------------------------

        direct_gain = (
            solar_gain +
            occupant_gain +
            equipment_gain +
            geothermal_gain
        )

        net_without_storage = (
            direct_gain -
            heat_loss
        )


        # ----------------------------------------------------
        # THERMAL STORAGE
        # ----------------------------------------------------

        storage_gain = 0.0

        if storage_enabled:

            # Excess heat charges storage
            if net_without_storage > 0:

                excess_heat = net_without_storage

                charge = min(
                    excess_heat *
                    storage_efficiency,
                    storage_capacity -
                    storage_level
                )

                storage_level += charge

            # Storage supplies heat during deficit
            elif net_without_storage < 0:

                required_heat = abs(
                    net_without_storage
                )

                available_discharge = min(
                    required_heat /
                    max(storage_efficiency, 0.01),
                    storage_level
                )

                storage_level -= (
                    available_discharge
                )

                storage_gain = (
                    available_discharge *
                    storage_efficiency
                )


        # ----------------------------------------------------
        # FINAL NET HEAT
        # ----------------------------------------------------

        total_gain = (
            direct_gain +
            storage_gain
        )

        net_heat = (
            total_gain -
            heat_loss
        )


        # ----------------------------------------------------
        # TEMPERATURE UPDATE
        # ----------------------------------------------------

        # 1 hour time step
        energy_joules = (
            net_heat *
            1000 *
            3600
        )

        temperature_change = (
            energy_joules /
            total_capacity
        )

        indoor_temp += temperature_change


        # ----------------------------------------------------
        # STORE RESULTS
        # ----------------------------------------------------

        indoor_temps.append(
            indoor_temp
        )

        outdoor_temps.append(
            outdoor_temp
        )

        wall_losses.append(
            wall_loss
        )

        roof_losses.append(
            roof_loss
        )

        floor_losses.append(
            floor_loss
        )

        opening_losses.append(
            opening_loss
        )

        ventilation_losses.append(
            ventilation_loss
        )

        solar_gains.append(
            solar_gain
        )

        occupant_gains.append(
            occupant_gain
        )

        equipment_gains.append(
            equipment_gain
        )

        geothermal_gains.append(
            geothermal_gain
        )

        storage_gains.append(
            storage_gain
        )

        total_heat_loss.append(
            heat_loss
        )

        total_heat_gain.append(
            total_gain
        )

        storage_levels.append(
            storage_level
        )


    # ========================================================
    # RESULTS
    # ========================================================

    st.success(
        "Simulation completed successfully."
    )

    st.divider()

    st.header("Simulation Results")


    # ========================================================
    # KPI CARDS
    # ========================================================

    min_temp = min(indoor_temps)
    max_temp = max(indoor_temps)
    avg_temp = sum(indoor_temps) / len(indoor_temps)
    max_loss = max(total_heat_loss)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Minimum Indoor Temperature",
            f"{min_temp:.1f} °C"
        )

    with col2:
        st.metric(
            "Maximum Indoor Temperature",
            f"{max_temp:.1f} °C"
        )

    with col3:
        st.metric(
            "Average Indoor Temperature",
            f"{avg_temp:.1f} °C"
        )

    with col4:
        st.metric(
            "Maximum Heat Loss",
            f"{max_loss:.2f} kW"
        )


    # ========================================================
    # TEMPERATURE GRAPH
    # ========================================================

    st.subheader(
        "24-Hour Temperature Profile"
    )

    temperature_df = pd.DataFrame(
        {
            "Hour": hours,
            "Indoor Temperature (°C)": indoor_temps,
            "Outdoor Temperature (°C)": outdoor_temps
        }
    )

    st.line_chart(
        temperature_df.set_index("Hour")
    )


    # ========================================================
    # HEAT TRANSFER GRAPH
    # ========================================================

    st.subheader(
        "Heat Gain and Heat Loss"
    )

    heat_df = pd.DataFrame(
        {
            "Hour": hours,
            "Total Heat Gain (kW)": total_heat_gain,
            "Total Heat Loss (kW)": total_heat_loss
        }
    )

    st.line_chart(
        heat_df.set_index("Hour")
    )


    # ========================================================
    # DETAILED HEAT LOSS
    # ========================================================

    st.subheader(
        "Heat Loss Components"
    )

    loss_df = pd.DataFrame(
        {
            "Hour": hours,
            "Walls (kW)": wall_losses,
            "Roof (kW)": roof_losses,
            "Floor (kW)": floor_losses,
            "Windows and Doors (kW)": opening_losses,
            "Ventilation (kW)": ventilation_losses
        }
    )

    st.line_chart(
        loss_df.set_index("Hour")
    )


    # ========================================================
    # HEAT GAIN COMPONENTS
    # ========================================================

    st.subheader(
        "Heat Gain Components"
    )

    gain_df = pd.DataFrame(
        {
            "Hour": hours,
            "Solar Gain (kW)": solar_gains,
            "Occupants (kW)": occupant_gains,
            "Equipment (kW)": equipment_gains,
            "Geothermal (kW)": geothermal_gains,
            "Storage (kW)": storage_gains
        }
    )

    st.line_chart(
        gain_df.set_index("Hour")
    )


    # ========================================================
    # THERMAL STORAGE
    # ========================================================

    if storage_enabled:

        st.subheader(
            "Thermal Storage State"
        )

        storage_df = pd.DataFrame(
            {
                "Hour": hours,
                "Stored Thermal Energy (kWh)": storage_levels
            }
        )

        st.line_chart(
            storage_df.set_index("Hour")
        )


    # ========================================================
    # DESIGN SUMMARY
    # ========================================================

    st.divider()

    st.header(
        "Design Summary"
    )

    summary_col1, summary_col2 = st.columns(2)


    with summary_col1:

        st.markdown("### Shelter Configuration")

        st.write(
            f"**Length:** {length:.2f} m"
        )

        st.write(
            f"**Width:** {width:.2f} m"
        )

        st.write(
            f"**Wall Height:** {height:.2f} m"
        )

        st.write(
            f"**Floor Area:** {floor_area:.2f} m²"
        )

        st.write(
            f"**Wall Area:** {wall_area:.2f} m²"
        )

        st.write(
            f"**Roof Area:** {roof_area:.2f} m²"
        )

        st.write(
            f"**Internal Volume:** {volume:.2f} m³"
        )


    with summary_col2:

        st.markdown("### Thermal Configuration")

        st.write(
            f"**Insulation:** {material_name}"
        )

        st.write(
            f"**Insulation Thickness:** {thickness_mm} mm"
        )

        st.write(
            f"**Thermal Conductivity:** {k_value:.3f} W/m·K"
        )

        st.write(
            f"**Wall U-value:** {wall_u:.3f} W/m²K"
        )

        st.write(
            f"**Roof U-value:** {roof_u:.3f} W/m²K"
        )

        st.write(
            f"**Floor U-value:** {floor_u:.3f} W/m²K"
        )


    # ========================================================
    # ENERGY BALANCE
    # ========================================================

    st.divider()

    st.header(
        "Energy Balance"
    )

    total_wall_loss = sum(wall_losses)
    total_roof_loss = sum(roof_losses)
    total_floor_loss = sum(floor_losses)
    total_opening_loss = sum(opening_losses)
    total_vent_loss = sum(ventilation_losses)

    total_solar = sum(solar_gains)
    total_occupant = sum(occupant_gains)
    total_equipment = sum(equipment_gains)
    total_geothermal = sum(geothermal_gains)
    total_storage = sum(storage_gains)

    energy_balance = pd.DataFrame(
        {
            "Energy Component": [
                "Wall Heat Loss",
                "Roof Heat Loss",
                "Floor Heat Loss",
                "Window and Door Heat Loss",
                "Ventilation Heat Loss",
                "Solar Heat Gain",
                "Occupant Heat Gain",
                "Equipment Heat Gain",
                "Geothermal Heat Gain",
                "Thermal Storage Contribution"
            ],

            "24-Hour Energy (kWh)": [
                total_wall_loss,
                total_roof_loss,
                total_floor_loss,
                total_opening_loss,
                total_vent_loss,
                total_solar,
                total_occupant,
                total_equipment,
                total_geothermal,
                total_storage
            ]
        }
    )

    energy_balance[
        "24-Hour Energy (kWh)"
    ] = energy_balance[
        "24-Hour Energy (kWh)"
    ].round(2)

    st.dataframe(
        energy_balance,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # DESIGN ASSESSMENT
    # ========================================================

    st.divider()

    st.header(
        "Thermal Performance Assessment"
    )

    if min_temp < 18:

        st.warning(
            "The simulated indoor temperature falls below "
            "18 °C during part of the simulation period. "
            "Consider increasing insulation, geothermal "
            "heat supply or thermal storage capacity."
        )

    elif max_temp > 28:

        st.warning(
            "The simulated indoor temperature exceeds "
            "28 °C during part of the simulation period. "
            "Consider reducing heat input or improving "
            "thermal regulation."
        )

    else:

        st.success(
            "The simulated indoor temperature remains "
            "within the selected reference comfort range "
            "of 18–28 °C."
        )


    # ========================================================
    # TECHNICAL NOTES
    # ========================================================

    with st.expander(
        "Technical Notes and Assumptions"
    ):

        st.write(
            """
            The model uses a lumped thermal-capacitance approach
            with a one-hour simulation time step.

            Heat transfer through walls, roof and floor is
            calculated using U-values derived from insulation
            thickness and thermal conductivity.

            Additional heat losses include window and door
            transmission and ventilation/infiltration.

            Heat gains include solar radiation, occupants,
            internal equipment, geothermal heating and thermal
            storage.

            The outdoor temperature and solar radiation profiles
            represent simplified design-day conditions rather
            than measured weather data.

            Material thermal conductivity values are
            representative engineering values. Manufacturer
            datasheets should be used for final engineering
            design.

            This software is intended for simulation,
            comparison and academic/project analysis and is not
            a substitute for certified building thermal design.
            """
        )


    # ========================================================
    # DOWNLOAD RESULTS
    # ========================================================

    st.divider()

    st.header(
        "Simulation Data"
    )

    results_df = pd.DataFrame(
        {
            "Hour": hours,
            "Outdoor Temperature (°C)": outdoor_temps,
            "Indoor Temperature (°C)": indoor_temps,
            "Wall Heat Loss (kW)": wall_losses,
            "Roof Heat Loss (kW)": roof_losses,
            "Floor Heat Loss (kW)": floor_losses,
            "Opening Heat Loss (kW)": opening_losses,
            "Ventilation Heat Loss (kW)": ventilation_losses,
            "Total Heat Loss (kW)": total_heat_loss,
            "Solar Heat Gain (kW)": solar_gains,
            "Occupant Heat Gain (kW)": occupant_gains,
            "Equipment Heat Gain (kW)": equipment_gains,
            "Geothermal Heat Gain (kW)": geothermal_gains,
            "Storage Heat Gain (kW)": storage_gains,
            "Total Heat Gain (kW)": total_heat_gain,
            "Storage Level (kWh)": storage_levels
        }
    )

    csv_data = results_df.to_csv(
        index=False
    )

    st.download_button(
        label="DOWNLOAD SIMULATION DATA",
        data=csv_data,
        file_name="thermos_shelterx_simulation.csv",
        mime="text/csv",
        use_container_width=True
    )


# ============================================================
# DEFAULT SCREEN
# ============================================================

else:

    st.markdown(
        """
        ### System Overview

        THERMOS SHELTERX evaluates the thermal behaviour of
        high-altitude shelters by combining building geometry,
        insulation properties, environmental conditions and
        thermal energy inputs.

        **Simulation modules**

        - Shelter geometry and surface-area calculation
        - Wall, roof and floor heat-transfer analysis
        - Window and door heat-loss analysis
        - Ventilation and infiltration losses
        - Solar heat-gain estimation
        - Occupant and equipment heat gains
        - Geothermal heating
        - Thermal energy storage
        - 24-hour indoor-temperature prediction
        - Energy-balance analysis
        - Simulation-data export

        Configure the parameters in the left panel and select
        **RUN SIMULATION** to begin.
        """
    )

    st.divider()

    st.markdown(
        """
        **THERMOS SHELTERX**

        Thermal modelling and energy analysis platform for
        high-altitude shelter applications.
        """
    )