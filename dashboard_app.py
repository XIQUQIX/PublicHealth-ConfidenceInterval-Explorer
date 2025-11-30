# =========================
# 1. Imports: load core libraries for data handling, plotting, and Dash app
# =========================
import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px

# =========================
# 2. Data loading: read aggregated parquet file and validate required columns
# =========================
DATA_PATH = r"E:\GRADUATE\Semster\25 Fall Semster\DS5110\project\Final\cleaned.parquet"

print(f"📥 Loading aggregated dataset from: {DATA_PATH}")
df = pd.read_parquet(DATA_PATH)
print("Data loaded! Shape:", df.shape)
print("Columns:", df.columns.tolist())

required_cols = [
    "Year",
    "Locationabbr",
    "Class",
    "Topic",
    "Question",
    "Response",
    "Break_Out",
    "Break_Out_Category",
    "Sample_Size",
    "Data_value",
    "Confidence_limit_Low",
    "Confidence_limit_High",
    "proportion",
    "persons",
]
for c in required_cols:
    if c not in df.columns:
        raise ValueError(f"Dataset missing required column: {c}")

# =========================
# 3. Type casting: ensure numeric columns are floats for later calculations
# =========================
for col in [
    "Sample_Size",
    "Data_value",
    "Confidence_limit_Low",
    "Confidence_limit_High",
    "proportion",
    "persons",
]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# =========================
# 4. Constants: define breakout labels and z-score for 95% confidence intervals
# =========================
BREAKOUT_OVERALL = "Overall"
BREAKOUT_GENDER = "Sex"
BREAKOUT_AGE = "Age Group"
BREAKOUT_EDU = "Education Attained"
BREAKOUT_INC = "Household Income"
Z = 1.96


# =========================
# 5. Helper function: aggregate persons and sample size, then recompute CI
# =========================
def aggregate_groups(sub_df: pd.DataFrame, group_cols):
    if sub_df.empty:
        return pd.DataFrame(
            columns=list(group_cols)
            + [
                "Sample_Size",
                "persons",
                "proportion",
                "Data_value",
                "Confidence_limit_Low",
                "Confidence_limit_High",
            ]
        )

    g = sub_df.groupby(list(group_cols), as_index=False).agg(
        Sample_Size=("Sample_Size", "sum"),
        persons=("persons", "sum"),
    )

    g["proportion"] = g["persons"] / g["Sample_Size"]
    g.loc[g["Sample_Size"] <= 0, "proportion"] = np.nan

    se = np.sqrt(g["proportion"] * (1 - g["proportion"]) / g["Sample_Size"])
    g["Data_value"] = g["proportion"] * 100.0
    g["Confidence_limit_Low"] = (g["proportion"] - Z * se) * 100.0
    g["Confidence_limit_High"] = (g["proportion"] + Z * se) * 100.0

    g["Confidence_limit_Low"] = g["Confidence_limit_Low"].clip(0, 100)
    g["Confidence_limit_High"] = g["Confidence_limit_High"].clip(0, 100)

    return g


# =========================
# 6. Helper function: build a single-series bar chart with error bars for CI
# =========================
def make_bar_with_ci(df_panel, x_col, title):
    if df_panel.empty:
        fig = go.Figure()
        fig.update_layout(
            title=title,
            xaxis_title=x_col,
            yaxis_title="Percent (%)",
            template="plotly_white",
            height=400,
        )
        return fig

    x = df_panel[x_col].astype(str)
    y = df_panel["Data_value"]
    err_plus = df_panel["Confidence_limit_High"] - df_panel["Data_value"]
    err_minus = df_panel["Data_value"] - df_panel["Confidence_limit_Low"]

    fig = go.Figure(
        data=[
            go.Bar(
                x=x,
                y=y,
                error_y=dict(
                    type="data",
                    array=err_plus,
                    arrayminus=err_minus,
                    visible=True,
                ),
            )
        ]
    )
    fig.update_layout(
        title=title,
        xaxis_title=x_col,
        yaxis_title="Percent (%)",
        template="plotly_white",
        height=400,
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


# =========================
# 7. Helper function: build grouped bar chart (x × color) with CI error bars
# =========================
def make_grouped_bar_with_ci(df_panel, x_col, color_col, title):
    if df_panel.empty:
        fig = go.Figure()
        fig.update_layout(
            title=title,
            xaxis_title=x_col,
            yaxis_title="Percent (%)",
            template="plotly_white",
            height=400,
        )
        return fig

    df_panel = df_panel.copy()
    df_panel[x_col] = df_panel[x_col].astype(str)
    df_panel[color_col] = df_panel[color_col].astype(str)
    df_panel["err_plus"] = df_panel["Confidence_limit_High"] - df_panel["Data_value"]
    df_panel["err_minus"] = df_panel["Data_value"] - df_panel["Confidence_limit_Low"]

    fig = px.bar(
        df_panel,
        x=x_col,
        y="Data_value",
        color=color_col,
        barmode="group",
        error_y="err_plus",
        error_y_minus="err_minus",
        labels={"Data_value": "Percent (%)"},
    )
    fig.update_layout(
        title=title,
        xaxis_title=x_col,
        yaxis_title="Percent (%)",
        template="plotly_white",
        height=400,
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig


# =========================
# 8. Panel function: create overall bar chart by response using Overall breakout
# =========================
def make_overall_panel(df_q):
    sub = df_q[df_q["Break_Out_Category"] == BREAKOUT_OVERALL].copy()
    if sub.empty:
        return make_bar_with_ci(pd.DataFrame(), "Response", "Overall (no data)")

    agg = aggregate_groups(sub, ["Response"])
    agg = agg.sort_values("Response")
    return make_bar_with_ci(agg, "Response", "Overall by Response")


# =========================
# 9. Panel function: create gender grouped bar chart by response and sex
# =========================
def make_gender_panel(df_q):
    sub = df_q[df_q["Break_Out_Category"] == BREAKOUT_GENDER].copy()
    if sub.empty:
        return make_grouped_bar_with_ci(
            pd.DataFrame(), "Response", "Break_Out", "By Gender (no data)"
        )

    agg = aggregate_groups(sub, ["Break_Out", "Response"])
    return make_grouped_bar_with_ci(
        agg, "Response", "Break_Out", "By Gender (Response × Sex)"
    )


# =========================
# 10. Panel function: create education grouped bar chart by response and level
# =========================
def make_education_panel(df_q):
    sub = df_q[df_q["Break_Out_Category"] == BREAKOUT_EDU].copy()
    if sub.empty:
        return make_grouped_bar_with_ci(
            pd.DataFrame(), "Response", "Break_Out", "By Education (no data)"
        )

    agg = aggregate_groups(sub, ["Break_Out", "Response"])
    order = ["Less than H.S.", "H.S. or G.E.D.", "Some post-H.S.", "College graduate"]
    agg["Break_Out"] = pd.Categorical(agg["Break_Out"], ordered=True, categories=order)
    agg = agg.sort_values(["Break_Out", "Response"])
    return make_grouped_bar_with_ci(
        agg, "Response", "Break_Out", "By Education (Response × Education)"
    )


# =========================
# 11. Panel function: create income grouped bar chart by response and income bin
# =========================
def make_income_panel(df_q):
    sub = df_q[df_q["Break_Out_Category"] == BREAKOUT_INC].copy()
    if sub.empty:
        return make_grouped_bar_with_ci(
            pd.DataFrame(), "Response", "Break_Out", "By Income (no data)"
        )

    agg = aggregate_groups(sub, ["Break_Out", "Response"])
    return make_grouped_bar_with_ci(
        agg, "Response", "Break_Out", "By Income (Response × Income)"
    )


# =========================
# 12. Panel function: create age grouped bar chart with More/Less granular modes
# =========================
def make_age_panel(df_q, mode="more"):
    sub = df_q[df_q["Break_Out_Category"] == BREAKOUT_AGE].copy()
    if sub.empty:
        return make_grouped_bar_with_ci(
            pd.DataFrame(), "Response", "Break_Out", "By Age (no data)"
        )

    if mode == "more":
        agg = aggregate_groups(sub, ["Break_Out", "Response"])
        age_order = [
            "18-24",
            "25-34",
            "35-44",
            "45-54",
            "55-64",
            "65-74",
            "75+",
        ]
        agg["Break_Out"] = pd.Categorical(
            agg["Break_Out"], ordered=True, categories=age_order
        )
        agg = agg.sort_values(["Break_Out", "Response"])
        title = "By Age (More detail: Response × Age group)"
        return make_grouped_bar_with_ci(agg, "Response", "Break_Out", title)
    else:
        mapping = {
            "18-24": "18-34",
            "25-34": "18-34",
            "35-44": "35-64",
            "45-54": "35-64",
            "55-64": "35-64",
            "65-74": "65+",
            "75+": "65+",
        }
        sub = sub[sub["Break_Out"].isin(mapping.keys())].copy()
        if sub.empty:
            return make_grouped_bar_with_ci(
                pd.DataFrame(), "Response", "Break_Out", "By Age (Less, no data)"
            )

        sub["Age_Group_3"] = sub["Break_Out"].map(mapping)
        agg = aggregate_groups(sub, ["Age_Group_3", "Response"])
        agg = agg.rename(columns={"Age_Group_3": "Break_Out"})
        order = ["18-34", "35-64", "65+"]
        agg["Break_Out"] = pd.Categorical(
            agg["Break_Out"], ordered=True, categories=order
        )
        agg = agg.sort_values(["Break_Out", "Response"])
        title = "By Age (Less detail: Response × Age group 3)"
        return make_grouped_bar_with_ci(agg, "Response", "Break_Out", title)


# =========================
# 13. Panel function: create temporal grouped bar chart by year and response
# =========================
def make_year_panel(df_q):
    sub = df_q[df_q["Break_Out_Category"] == BREAKOUT_OVERALL].copy()
    if sub.empty:
        return make_grouped_bar_with_ci(
            pd.DataFrame(), "Year", "Response", "By Year (no data)"
        )

    agg = aggregate_groups(sub, ["Year", "Response"])
    agg = agg.sort_values(["Year", "Response"])
    return make_grouped_bar_with_ci(
        agg, "Year", "Response", "By Year (Overall × Response)"
    )


# =========================
# 14. Panel function: create US choropleth map by state for a chosen response
# =========================
def make_location_map(df_q):
    sub = df_q[df_q["Break_Out_Category"] == BREAKOUT_OVERALL].copy()
    if sub.empty:
        fig = go.Figure()
        fig.update_layout(
            title="By Location (no data)",
            template="plotly_white",
            height=500,
        )
        return fig

    responses = sorted(sub["Response"].dropna().unique())
    target_resp = "Yes" if "Yes" in responses else (responses[0] if responses else None)
    sub = sub[sub["Response"] == target_resp].copy()

    if sub.empty:
        fig = go.Figure()
        fig.update_layout(
            title="By Location (no data for selected response)",
            template="plotly_white",
            height=500,
        )
        return fig

    agg = aggregate_groups(sub, ["Locationabbr"])
    agg = agg.dropna(subset=["Locationabbr"])

    if agg.empty:
        fig = go.Figure()
        fig.update_layout(
            title="By Location (no data)",
            template="plotly_white",
            height=500,
        )
        return fig

    fig = px.choropleth(
        agg,
        locations="Locationabbr",
        locationmode="USA-states",
        color="Data_value",
        scope="usa",
        hover_data={
            "Locationabbr": True,
            "Data_value": True,
            "Confidence_limit_Low": True,
            "Confidence_limit_High": True,
        },
        labels={"Data_value": f"{target_resp} (%)"},
    )
    fig.update_layout(
        title=f"By Location (Response = {target_resp})",
        height=500,
        margin=dict(l=0, r=0, t=60, b=0),
    )
    return fig


# =========================
# 15. Defaults: compute initial Class/Topic/Question values for dropdowns
# =========================
default_class = sorted(df["Class"].dropna().unique())[0]
default_topic = df[df["Class"] == default_class]["Topic"].dropna().sort_values().iloc[0]
default_question = (
    df[(df["Class"] == default_class) & (df["Topic"] == default_topic)]["Question"]
    .dropna()
    .sort_values()
    .iloc[0]
)

# =========================
# 16. App setup: create Dash app instance and server reference
# =========================
app = Dash(__name__)
server = app.server

# =========================
# 17. Layout: define page structure, controls, and graph placeholders
# =========================
app.layout = html.Div(
    [
        html.H1("BRFSS Dashboard (DS5110)", style={"textAlign": "center"}),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Class"),
                        dcc.Dropdown(
                            id="class-dropdown",
                            options=[
                                {"label": c, "value": c}
                                for c in sorted(df["Class"].dropna().unique())
                            ],
                            value=default_class,
                            clearable=False,
                        ),
                    ],
                    style={
                        "width": "24%",
                        "display": "inline-block",
                        "padding": "0 5px",
                    },
                ),
                html.Div(
                    [
                        html.Label("Topic"),
                        dcc.Dropdown(
                            id="topic-dropdown",
                            clearable=False,
                        ),
                    ],
                    style={
                        "width": "24%",
                        "display": "inline-block",
                        "padding": "0 5px",
                    },
                ),
                html.Div(
                    [
                        html.Label("Question"),
                        dcc.Dropdown(
                            id="question-dropdown",
                            clearable=False,
                        ),
                    ],
                    style={
                        "width": "48%",
                        "display": "inline-block",
                        "padding": "0 5px",
                    },
                ),
            ],
            style={"marginBottom": "16px"},
        ),
        html.Div(
            [
                html.Label("Age granularity (More / Less): "),
                dcc.RadioItems(
                    id="age-mode-radio",
                    options=[
                        {"label": "More (fine age groups)", "value": "more"},
                        {"label": "Less (3 broad groups)", "value": "less"},
                    ],
                    value="more",
                    inline=True,
                ),
            ],
            style={"marginBottom": "20px"},
        ),
        html.Div(
            [
                html.H3("Overall"),
                dcc.Graph(id="overall-graph"),
                html.H3("By Gender"),
                dcc.Graph(id="gender-graph"),
                html.H3("By Age"),
                dcc.Graph(id="age-graph"),
                html.H3("By Education"),
                dcc.Graph(id="education-graph"),
                html.H3("By Income"),
                dcc.Graph(id="income-graph"),
                html.H3("By Location (Map)"),
                dcc.Graph(id="location-graph"),
                html.H3("By Year (Temporal)"),
                dcc.Graph(id="year-graph"),
            ]
        ),
    ],
    style={"maxWidth": "1200px", "margin": "0 auto"},
)


# =========================
# 18. Callback: update topic dropdown options and value when class changes
# =========================
@app.callback(
    Output("topic-dropdown", "options"),
    Output("topic-dropdown", "value"),
    Input("class-dropdown", "value"),
)
def update_topic_dropdown(selected_class):
    sub = df[df["Class"] == selected_class]
    topics = sorted(sub["Topic"].dropna().unique())
    options = [{"label": t, "value": t} for t in topics]
    value = topics[0] if topics else None
    return options, value


# =========================
# 19. Callback: update question dropdown based on selected class and topic
# =========================
@app.callback(
    Output("question-dropdown", "options"),
    Output("question-dropdown", "value"),
    Input("class-dropdown", "value"),
    Input("topic-dropdown", "value"),
)
def update_question_dropdown(selected_class, selected_topic):
    sub = df[(df["Class"] == selected_class) & (df["Topic"] == selected_topic)]
    questions = sorted(sub["Question"].dropna().unique())
    options = [{"label": q, "value": q} for q in questions]
    value = questions[0] if questions else None
    return options, value


# =========================
# 20. Callback: recompute all seven figures when filters or age mode change
# =========================
@app.callback(
    Output("overall-graph", "figure"),
    Output("gender-graph", "figure"),
    Output("age-graph", "figure"),
    Output("education-graph", "figure"),
    Output("income-graph", "figure"),
    Output("location-graph", "figure"),
    Output("year-graph", "figure"),
    Input("class-dropdown", "value"),
    Input("topic-dropdown", "value"),
    Input("question-dropdown", "value"),
    Input("age-mode-radio", "value"),
)
def update_all_panels(sel_class, sel_topic, sel_question, age_mode):
    sub = df[
        (df["Class"] == sel_class)
        & (df["Topic"] == sel_topic)
        & (df["Question"] == sel_question)
    ].copy()

    if sub.empty:
        empty_fig = make_bar_with_ci(pd.DataFrame(), "x", "No data")
        return (empty_fig,) * 7

    fig_overall = make_overall_panel(sub)
    fig_gender = make_gender_panel(sub)
    fig_age = make_age_panel(sub, mode=age_mode)
    fig_edu = make_education_panel(sub)
    fig_income = make_income_panel(sub)
    fig_loc = make_location_map(sub)
    fig_year = make_year_panel(sub)

    return (
        fig_overall,
        fig_gender,
        fig_age,
        fig_edu,
        fig_income,
        fig_loc,
        fig_year,
    )


# =========================
# 21. Entry point: run the Dash development server
# =========================
if __name__ == "__main__":
    app.run(debug=True)
