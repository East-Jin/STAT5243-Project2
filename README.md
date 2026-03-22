# STAT5243 Project 2 — Data Preprocessing 

Implemented preprocessing steps include:

1. **Standardize missing-value representations**
   - Converts tokens such as `""`, `"NA"`, `"N/A"`, `"null"`, `"None"`, `"?"`, and `"-"` into true missing values (`NaN`)
2. **Handle missing values**
   - Drop rows with missing values
   - Drop columns above a missing-value threshold
   - Impute numeric columns with mean / median
   - Impute categorical columns with mode / `"Unknown"`
3. **Handle duplicates**
   - Detect and remove exact duplicate rows
4. **Format standardization**
   - Standardize column names
   - Trim whitespace in text columns
   - Convert text to lowercase (optional)
   - Attempt safe numeric conversion
5. **Scale numeric features**
   - `StandardScaler`
   - `MinMaxScaler`
6. **Encode categorical features**
   - One-hot encoding
   - Label encoding
7. **Handle outliers**
   - IQR-based row removal
   - IQR-based value capping

The module also includes visual outputs such as:

- missing-value bar chart
- numeric distribution histogram
- outlier boxplot
- column information table
- dataset quality overview

**Input:** `shared_store.raw_data`  
**Output:** `shared_store.cleaned_data`
