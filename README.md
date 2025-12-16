Persistent Segment Tree - Python Solution

This repository contains my implementation of a **Persistent Segment Tree** in Python. It supports efficient range queries and updates while maintaining previous versions of the array, enabling historical queries.

Features
- Persistent Updates: Every update creates a new version without modifying the previous ones.  
- Range Queries: Efficiently query sums or other aggregates over a range.  
- Version Management: Access any previous version of the array for queries.  
- Optimized for Competitive Programming: Designed for speed and minimal memory overhead.

Files
.pysolution/
├── main.py # Implementation of the Persistent Segment Tree
├── README.md # Project description (this file)

## Setup
1. **Python Version**: 3.8+  
2. **No external dependencies** (standard Python library is sufficient)  

## Usage
```python
from main import PersistentSegmentTree

# Example: initialize tree
arr = [1, 2, 3, 4, 5]
pst = PersistentSegmentTree(arr)

# Perform updates
pst.update(version=0, index=2, value=10)  # creates new version

# Query sum in a range
result = pst.query(version=1, left=1, right=3)
print(result)
