"""Tests for formatters module."""

import json

import pytest

from ouracli.formatters import (
    format_dataframe,
    format_json,
    format_markdown,
    format_output,
    format_tree,
)


class TestFormatTree:
    """Tests for format_tree function."""

    def test_simple_dict(self) -> None:
        """Test formatting simple dictionary."""
        data = {"name": "John", "age": 30}
        result = format_tree(data)
        assert "Name" in result
        assert "John" in result
        assert "Age" in result
        assert "30" in result
        # Should have dot leaders for alignment
        assert "..." in result

    def test_nested_dict(self) -> None:
        """Test formatting nested dictionary."""
        data = {"person": {"name": "John", "age": 30}}
        result = format_tree(data)
        assert "Person" in result
        assert "Name" in result
        assert "John" in result
        assert "Age" in result
        assert "30" in result

    def test_list(self) -> None:
        """Test formatting list."""
        data = [1, 2, 3]
        result = format_tree(data)
        # Simple lists show values directly without indices
        assert "1" in result
        assert "2" in result
        assert "3" in result

    def test_empty_dict(self) -> None:
        """Test formatting empty dictionary."""
        result = format_tree({})
        assert result == ""


class TestFormatJson:
    """Tests for format_json function."""

    def test_simple_dict(self) -> None:
        """Test JSON formatting."""
        data = {"name": "John", "age": 30}
        result = format_json(data)
        parsed = json.loads(result)
        assert parsed == data

    def test_list(self) -> None:
        """Test JSON formatting for list."""
        data = [{"id": 1}, {"id": 2}]
        result = format_json(data)
        parsed = json.loads(result)
        assert parsed == data


class TestFormatDataframe:
    """Tests for format_dataframe function."""

    def test_list_of_dicts(self) -> None:
        """Test DataFrame formatting for list of dicts."""
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        result = format_dataframe(data)
        assert "name" in result
        assert "John" in result
        assert "Jane" in result

    def test_empty_list(self) -> None:
        """Test DataFrame formatting for empty list."""
        result = format_dataframe([])
        assert result == "No data"

    def test_dict_with_lists(self) -> None:
        """Test DataFrame formatting for dict with lists."""
        data = {"users": [{"name": "John"}, {"name": "Jane"}]}
        result = format_dataframe(data)
        assert "users" in result
        assert "John" in result


class TestFormatMarkdown:
    """Tests for format_markdown function."""

    def test_list_of_dicts(self) -> None:
        """Test Markdown formatting for list of dicts."""
        data = [{"name": "John", "age": 30}]
        result = format_markdown(data)
        # Keys are humanized (capitalized)
        assert "Name" in result
        assert "John" in result
        assert "Age" in result
        assert "30" in result

    def test_empty_list(self) -> None:
        """Test Markdown formatting for empty list."""
        result = format_markdown([])
        assert "*No data*" in result

    def test_dict_with_lists(self) -> None:
        """Test Markdown formatting for dict with lists."""
        data = {"users": [{"name": "John"}]}
        result = format_markdown(data)
        # Top-level category gets # heading
        assert "# Users" in result
        assert "John" in result


class TestFormatOutput:
    """Tests for format_output function."""

    def test_tree_format(self) -> None:
        """Test output with tree format."""
        data = {"name": "John"}
        result = format_output(data, "tree")
        assert "Name" in result
        assert "John" in result

    def test_json_format(self) -> None:
        """Test output with JSON format."""
        data = {"name": "John"}
        result = format_output(data, "json")
        parsed = json.loads(result)
        assert parsed == data

    def test_invalid_format(self) -> None:
        """Test output with invalid format."""
        with pytest.raises(ValueError, match="Unknown format type"):
            format_output({}, "invalid")

    def test_default_format(self) -> None:
        """Test output with default format."""
        data = {"name": "John"}
        result = format_output(data)
        assert "Name" in result
        assert "John" in result
