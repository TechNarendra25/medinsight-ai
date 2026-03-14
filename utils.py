import pandas as pd
import io

def load_csv(file):
    """Load CSV file and return dataframe"""
    try:
        df = pd.read_csv(file, low_memory=False)
        return df, None
    except Exception as e:
        return None, str(e)

def get_dataframe_summary(df):
    """Generate a COMPACT summary to save API quota"""
    summary = f"""
Dataset Overview:
- Total Rows: {df.shape[0]}
- Total Columns: {df.shape[1]}
- Column Names: {list(df.columns)}
- Numeric Columns: {list(df.select_dtypes(include='number').columns)}
- Text Columns: {list(df.select_dtypes(include='object').columns)}

Sample Data (first 5 rows):
{df.head(5).to_string()}

Basic Statistics (numeric columns only):
{df.describe().to_string()}
    """
    return summary[:3000]  # Limit to 3000 characters

def get_basic_stats(df):
    """Return basic stats dictionary for display"""
    return {
        "Total Rows": df.shape[0],
        "Total Columns": df.shape[1],
        "Missing Values": int(df.isnull().sum().sum()),
        "Numeric Columns": len(df.select_dtypes(
                              include='number').columns),
        "Text Columns": len(df.select_dtypes(
                           include='object').columns)
    }

def export_chat_history(chat_history):
    """Export chat history as text file"""
    output = "MedInsight AI — Chat History\n"
    output += "=" * 40 + "\n\n"
    for i, chat in enumerate(chat_history, 1):
        output += f"Q{i}: {chat['question']}\n"
        output += f"A{i}: {chat['answer']}\n"
        output += "-" * 40 + "\n\n"
    return output

def clean_dataframe(df):
    """Basic cleaning — strip whitespace from text columns"""
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
    return df

def get_column_insights(df):
    """Return quick insights about each column"""
    insights = []
    for col in df.columns:
        if df[col].dtype == "object":
            insights.append({
                "Column": col,
                "Type": "Text",
                "Unique Values": df[col].nunique(),
                "Sample": str(df[col].dropna().iloc[0])
                          if len(df) > 0 else "N/A"
            })
        else:
            insights.append({
                "Column": col,
                "Type": "Numeric",
                "Min": round(df[col].min(), 2),
                "Max": round(df[col].max(), 2),
                "Mean": round(df[col].mean(), 2)
            })
    return pd.DataFrame(insights)