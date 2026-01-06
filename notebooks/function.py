import pandas as pd


def load_and_concat_data(
    demo_path: str,
    web_pt1_path: str,
    web_pt2_path: str,
    exp_path: str,
    sep: str = ",",
    parse_web_datetime: bool = True,
    web_time_col: str = "date_time",
):
    """
    Load raw demo, web (part 1 & 2), and experiment data.
    Concatenate web data into a single dataframe.

    Parameters
    ----------
    demo_path : str
        Path to demo dataset
    web_pt1_path : str
        Path to web data part 1
    web_pt2_path : str
        Path to web data part 2
    exp_path : str
        Path to experiment clients dataset
    sep : str, default=","
        Column separator used in CSV files
    parse_web_datetime : bool, default=True
        Convert web datetime column to pandas datetime
    web_time_col : str, default="date_time"
        Name of datetime column in web data

    Returns
    -------
    df_demo : pd.DataFrame
    df_web : pd.DataFrame
    df_exp : pd.DataFrame
    """

    df_demo = pd.read_csv(demo_path, sep=sep)
    df_web_pt1 = pd.read_csv(web_pt1_path, sep=sep)
    df_web_pt2 = pd.read_csv(web_pt2_path, sep=sep)
    df_exp = pd.read_csv(exp_path, sep=sep)

    df_web = pd.concat([df_web_pt1, df_web_pt2], axis=0, ignore_index=True)

    if parse_web_datetime and web_time_col in df_web.columns:
        df_web[web_time_col] = pd.to_datetime(df_web[web_time_col], errors="coerce")

    return df_demo, df_web, df_exp


def compute_completion_rate_by_variation(
    df_web: pd.DataFrame,
    df_exp: pd.DataFrame,
    client_col: str = "client_id",
    visit_col: str = "visit_id",
    step_col: str = "process_step",
    variation_col: str = "Variation",
    confirm_step: str = "confirm",
):
    """
    KPI 1: Completion Rate

    A visit is considered completed if it contains at least one
    'confirm' step. Completion rate is calculated at the visit level
    and then averaged by variation (Control vs Test).

    Parameters
    ----------
    df_web : pd.DataFrame
        Web tracking data
    df_exp : pd.DataFrame
        Experiment assignment data
    client_col : str
        Client identifier column
    visit_col : str
        Visit identifier column
    step_col : str
        Process step column
    variation_col : str
        Experiment variation column
    confirm_step : str
        Value indicating completion (default: "confirm")

    Returns
    -------
    pd.DataFrame
        Completion rate by variation
    """

    # 1. Merge web data with experiment variation
    df_merged = df_web.merge(
        df_exp[[client_col, variation_col]], on=client_col, how="inner"
    )

    # 2. Determine completion at visit level
    visit_completion = (
        df_merged.groupby([visit_col, variation_col])[step_col]
        .apply(lambda x: confirm_step in x.values)
        .reset_index(name="completed")
    )

    # 3. Compute completion rate by variation
    completion_rate = (
        visit_completion.groupby(variation_col)["completed"].mean().reset_index()
    )

    return completion_rate


def compute_avg_time_per_step_by_variation(
    df_web: pd.DataFrame,
    df_exp: pd.DataFrame,
    client_col: str = "client_id",
    visit_col: str = "visit_id",
    step_col: str = "process_step",
    time_col: str = "date_time",
    variation_col: str = "Variation",
    how_merge: str = "inner",
):
    """
    KPI 2: Time Spent on Each Step

    Time spent is computed as the time difference (in seconds) between
    consecutive events within the same visit. Then we compute the average
    time per step by variation (Control vs Test).

    Parameters
    ----------
    df_web : pd.DataFrame
        Web tracking data containing visit_id, process_step, and datetime column.
    df_exp : pd.DataFrame
        Experiment assignment data containing client_id and Variation.
    client_col, visit_col, step_col, time_col, variation_col : str
        Column names.
    how_merge : str
        Merge type with experiment table (default: "inner").

    Returns
    -------
    pd.DataFrame
        Columns: [Variation, process_step, time_diff_sec]
        where time_diff_sec is the mean time spent for that step.
    """

    df = df_web.copy()

    # 1) Convert time column to datetime
    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")

    # 2) Sort by visit and time
    df = df.sort_values([visit_col, time_col])

    # 3) Compute time difference within each visit (seconds)
    df["time_diff_sec"] = df.groupby(visit_col)[time_col].diff().dt.total_seconds()

    # 4) Merge variation into web data
    df = df.merge(df_exp[[client_col, variation_col]], on=client_col, how=how_merge)

    # 5) Average time per step by variation
    avg_time_per_step = (
        df.groupby([variation_col, step_col])["time_diff_sec"].mean().reset_index()
    )

    return avg_time_per_step


def compute_error_rate_by_variation(
    df_web: pd.DataFrame,
    df_exp: pd.DataFrame,
    client_col: str = "client_id",
    visit_col: str = "visit_id",
    step_col: str = "process_step",
    time_col: str = "date_time",
    variation_col: str = "Variation",
    step_order: dict | None = None,
    how_merge: str = "inner",
):
    """
    KPI 3: Error Rate (Step Backward)

    An error is defined as a backward movement within the same visit:
    the user goes from a later step to an earlier step.

    Steps are converted to numeric order (step_order), then we compute
    step_diff within each visit. If step_diff < 0 => error event.

    At the visit level: a visit is marked as error=True if it contains
    at least one backward movement.

    Finally: error rate is the mean of visit-level error by variation.

    Returns
    -------
    pd.DataFrame
        Columns: [Variation, error]
        where error is the error rate (0-1).
    """

    # Default step order (matches your notebook)
    if step_order is None:
        step_order = {"start": 0, "step_1": 1, "step_2": 2, "step_3": 3, "confirm": 4}

    df = df_web.copy()

    # Ensure correct ordering before diff (important!)
    if time_col in df.columns:
        df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
        df = df.sort_values([visit_col, time_col])
    else:
        df = df.sort_values([visit_col])

    # Merge variation info
    df = df.merge(df_exp[[client_col, variation_col]], on=client_col, how=how_merge)

    # Map steps to numeric order
    df["step_num"] = df[step_col].map(step_order)

    # Compute step differences within visit
    df["step_diff"] = df.groupby(visit_col)["step_num"].diff()

    # Error event: backward step
    df["error_event"] = df["step_diff"] < 0

    # Visit-level: any backward step in the visit
    visit_errors = (
        df.groupby([visit_col, variation_col])["error_event"]
        .any()
        .reset_index(name="error")
    )

    # Variation-level: average error across visits
    error_rate = visit_errors.groupby(variation_col)["error"].mean().reset_index()

    return error_rate
