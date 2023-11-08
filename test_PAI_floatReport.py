import pytest
from unittest.mock import patch
from io import StringIO
from PAI_floatReport_csv import (
    extract_date,
    look_for_new_data,
    determine_output_filename,
    Process_any_known_downloadfile,
)

@pytest.fixture
def sample_csv_filename():
    return "Terminal Status(w_FLOAT)automated20230115.csv"

@pytest.fixture
def sample_output_folder():
    return "test_output"

@pytest.fixture
def sample_output_file(sample_output_folder):
    return f"{sample_output_folder}/_Terminal Status(w_FLOAT)automated.xlsx"

def test_extract_date(sample_csv_filename):
    expected_date = "20230115"
    result = extract_date(sample_csv_filename)
    assert result == expected_date

def test_look_for_new_data(sample_csv_filename, sample_output_file):
    with patch('pathlib.Path.glob') as mock_glob:
        mock_glob.return_value = [
            Path(sample_csv_filename),
            Path(sample_output_file),
        ]
        result = look_for_new_data("Terminal Status(w_FLOAT)automated", [".csv"])
        assert result == Path(sample_csv_filename)

def test_determine_output_filename(sample_output_folder):
    datestr = "20230115"
    matchedname = "Terminal Status(w_FLOAT)automated"
    ext = ".xlsx"
    expected_output = Path(f"{sample_output_folder}/_{matchedname}{ext}")
    result = determine_output_filename(datestr, matchedname, ext, sample_output_folder)
    assert result == expected_output

def test_remove_file(sample_output_file):
    test_file = Path(sample_output_file)
    with test_file.open("w") as f:
        f.write("Test content")
    result = remove_file(test_file)
    assert result is True
    assert not test_file.exists()

# You can add more test cases as needed

if __name__ == "__main__":
    pytest.main()
