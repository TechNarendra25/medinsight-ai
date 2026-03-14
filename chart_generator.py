import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def generate_chart(df, user_question):
    """
    Automatically detect what chart to generate
    based on user question keywords
    """
    question = user_question.lower()

    try:
        # ── Bar Chart: Company / Manufacturer count ──────────
        if any(word in question for word in
               ["company", "manufacturer", "brand", "top"]):
            col = detect_text_column(df,
                  ["manufacturer", "company", "brand"])
            if col:
                counts = df[col].value_counts().head(10)
                fig = px.bar(
                    x=counts.values,
                    y=counts.index,
                    orientation="h",
                    title=f"Top 10 by {col.title()}",
                    labels={"x": "Count", "y": col.title()},
                    color=counts.values,
                    color_continuous_scale="Blues"
                )
                fig.update_layout(showlegend=False)
                return fig

        # ── Pie Chart: Category distribution ─────────────────
        elif any(word in question for word in
                 ["category", "type", "class",
                  "distribution", "breakdown"]):
            col = detect_text_column(df,
                  ["category", "type", "class", "therapeutic"])
            if col:
                counts = df[col].value_counts().head(8)
                fig = px.pie(
                    values=counts.values,
                    names=counts.index,
                    title=f"Distribution by {col.title()}",
                    hole=0.3
                )
                return fig

        # ── Histogram: Price distribution ────────────────────
        elif any(word in question for word in
                 ["price", "cost", "expensive",
                  "cheap", "affordable"]):
            col = detect_numeric_column(df,
                  ["price", "mrp", "cost", "rate"])
            if col:
                fig = px.histogram(
                    df,
                    x=col,
                    nbins=50,
                    title=f"Distribution of {col.title()}",
                    labels={col: col.title()},
                    color_discrete_sequence=["#00CC96"]
                )
                fig.update_layout(
                    xaxis_title=col.title(),
                    yaxis_title="Number of Medicines"
                )
                return fig

        # ── Box Plot: Compare prices ───────────────────────
        elif any(word in question for word in
                 ["compare", "vs", "versus",
                  "difference", "average"]):
            num_col = detect_numeric_column(df,
                      ["price", "mrp", "cost"])
            cat_col = detect_text_column(df,
                      ["category", "type", "therapeutic"])
            if num_col and cat_col:
                top_cats = df[cat_col].value_counts(
                ).head(6).index
                filtered = df[df[cat_col].isin(top_cats)]
                fig = px.box(
                    filtered,
                    x=cat_col,
                    y=num_col,
                    title=f"{num_col.title()} by "
                          f"{cat_col.title()}",
                    color=cat_col
                )
                fig.update_layout(showlegend=False)
                return fig

        # ── Scatter Plot ─────────────────────────────────────
        elif any(word in question for word in
                 ["correlation", "relationship",
                  "scatter", "trend"]):
            num_cols = df.select_dtypes(
                include="number").columns.tolist()
            if len(num_cols) >= 2:
                fig = px.scatter(
                    df,
                    x=num_cols[0],
                    y=num_cols[1],
                    title=f"{num_cols[0].title()} vs "
                          f"{num_cols[1].title()}",
                    opacity=0.6,
                    color_discrete_sequence=["#EF553B"]
                )
                return fig

        # ── Default: Top 10 bar chart ─────────────────────────
        else:
            col = detect_text_column(df,
                  ["name", "medicine", "drug"])
            num_col = detect_numeric_column(df,
                      ["price", "mrp", "cost"])
            if col and num_col:
                top10 = df.nlargest(10, num_col)[
                    [col, num_col]
                ]
                fig = px.bar(
                    top10,
                    x=num_col,
                    y=col,
                    orientation="h",
                    title=f"Top 10 Medicines by "
                          f"{num_col.title()}",
                    color=num_col,
                    color_continuous_scale="Reds"
                )
                fig.update_layout(showlegend=False)
                return fig

    except Exception as e:
        print(f"Chart error: {e}")
        return None

    return None


def detect_text_column(df, keywords):
    """Find best matching text column from keywords"""
    for keyword in keywords:
        for col in df.columns:
            if keyword.lower() in col.lower():
                return col
    text_cols = df.select_dtypes(include="object").columns
    return text_cols[0] if len(text_cols) > 0 else None


def detect_numeric_column(df, keywords):
    """Find best matching numeric column from keywords"""
    for keyword in keywords:
        for col in df.columns:
            if keyword.lower() in col.lower():
                if pd.api.types.is_numeric_dtype(df[col]):
                    return col
    num_cols = df.select_dtypes(include="number").columns
    return num_cols[0] if len(num_cols) > 0 else None