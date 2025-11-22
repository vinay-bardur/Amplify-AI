import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.csv_handler import validate_csv, parse_csv_upload
import pandas as pd
import io

def test_valid_csv():
    """Test valid CSV validation"""
    csv_content = b"hour,ghi,temp_c,cloud_pct,output_kwh\n12,950,33,3,3.8\n13,980,34,2,4.2\n14,900,32,5,3.5\n15,850,31,8,3.0\n16,700,30,10,2.5"
    df, error = validate_csv(csv_content)
    assert df is not None
    assert error is None
    assert len(df) == 5
    print("✓ Valid CSV test passed")

def test_missing_columns():
    """Test CSV with missing columns"""
    csv_content = b"hour,ghi,temp_c\n12,950,33\n13,980,34"
    df, error = validate_csv(csv_content)
    assert df is None
    assert error is not None
    print("✓ Missing columns test passed")

def test_insufficient_rows():
    """Test CSV with insufficient rows"""
    csv_content = b"hour,ghi,temp_c,cloud_pct,output_kwh\n12,950,33,3,3.8"
    df, error = validate_csv(csv_content)
    assert df is None
    assert error is not None
    print("✓ Insufficient rows test passed")

def test_csv_with_nulls():
    """Test CSV with null values"""
    csv_content = b"hour,ghi,temp_c,cloud_pct,output_kwh\n12,950,33,3,3.8\n13,,34,2,4.2\n14,900,32,5,3.5\n15,850,31,8,3.0\n16,700,30,10,2.5"
    df, error = validate_csv(csv_content)
    assert df is not None
    assert error is None
    print("✓ CSV with nulls test passed")

def test_invalid_format():
    """Test invalid CSV format"""
    csv_content = b"not a valid csv"
    df, error = validate_csv(csv_content)
    assert df is None
    assert error is not None
    print("✓ Invalid format test passed")

if __name__ == '__main__':
    test_valid_csv()
    test_missing_columns()
    test_insufficient_rows()
    test_csv_with_nulls()
    test_invalid_format()
    print("\n✅ All CSV ingestion tests passed!")
