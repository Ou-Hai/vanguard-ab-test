# Vanguard-ab-test
A/B testing analysis of Vanguard’s digital process redesign, including EDA, KPIs, hypothesis testing, and visualization.
---

## Project Overview

We are a team of data analysts who work with data from start to finish, cleaning it, analyzing it, and presenting insights in a clear and meaningful way.


The presentation is available (Insert when done)
---

## 💾 Data Sources

The analysis merges multiple data sets to come up with a concise answer on if the upgrade was worth it

| Dataset                        | Source                                                    | Purpose                                                                                    |
| :----------------------------- | :-------------------------------------------------------- | :----------------------------------------------------------------------------------------- |
| **Client Profile**             | GitHub: 'Df_final_demo'                                   | Demographics like age, gender, and account details of our clients                           |
| **Digital Footprints**         | GitHub: 'Df_Final_Web_Data'                               | A detailed trace of client interactions online, divided into two parts: pt_1 and pt_2.     |
| **Experiment Roster**          | GitHub: 'Df_final_experiment_clients'                     | A list revealing which clients were part of the grand experiment                            

## Day 1: Exploration and Hypothesis Formulation

The initial day focused on exploratory data analysis and defining the analytical framework.

### Analysis Goals

1. **Goal A:** Develop a Crime Risk Index — a weighted index that combines crime rates (crime count / population) to rank districts.
2. **Goal B:** Identify correlations between demographics and crime — check whether specific age groups are associated with certain crime types.
3. **Goal C:** Analyze crime specialization and temporal trends — investigate unique crime patterns in districts and changes over time.

### Testable Hypotheses

| ID     | Category                  | Hypothesis Statement                                                                                                                |
| :----- | :------------------------ | :---------------------------------------------------------------------------------------------------------------------------------- |
| **H1** | General Crime Rate        | Districts with higher population density will have a higher absolute number of non-violent crimes.                                  |
| **H2** | General Crime Rate        | The **Regierungsviertel** will have an above-average rate of **Threat** and **Damage** (per capita).                                |
| **H3** | Demographics (Age)        | Locations with a higher proportion of residents aged **65 and older** will show a higher rate of **Burglary** per capita.           |
| **H4** | Demographics (Age)        | Locations with a higher proportion of the **18-27** age group will correlate with a higher rate of **Drugs** offenses (per capita). |
| **H5** | Specific Crime (Temporal) | The rate of **Car theft** has declined over the years covered in the dataset.                                                       ||
