"""Test the mynames module."""
import pytest

from mynames import MyNames


@pytest.fixture
def new_names():
    """Return a new names instance."""
    return MyNames()


@pytest.fixture
def name_string_list():
    """Return a list of example names."""
    return ["Alice", "Bob", "Eve"]


@pytest.fixture
def used_names(name_string_list):
    """Return a names instance, after three names have been added."""
    my_name = MyNames()
    for name in name_string_list:
        my_name.lookup(name)
    return my_name


def test_get_string_raises_exceptions(used_names):
    """Test if get_string raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.get_string(1.4)
    with pytest.raises(TypeError):
        used_names.get_string("hello")
    with pytest.raises(ValueError):
        used_names.get_string(-1)


@pytest.mark.parametrize("name_id, expected_string", [
    (0, "Alice"),
    (1, "Bob"),
    (2, "Eve"),
    (3, None)
])
def test_get_string(used_names, new_names, name_id, expected_string):
    """Test if get_string returns the expected string."""
    # Name is present
    assert used_names.get_string(name_id) == expected_string
    # Name is absent
    assert new_names.get_string(name_id) is None


def test_lookup_append(used_names):
    """Checks that lookup appends a name if it is not already in the class"""
    before = len(used_names.names)
    used_names.lookup(["Andrew"])
    after = len(used_names.names)
    assert before + 1 == after


def test_lookup_unique_id(used_names, name_string_list):
    """Test to check that all the of the name ids are unique"""
    for i in range(0, 2):
        for j in range(0, 2):
            if i != j:
                assert not used_names.lookup(
                    name_string_list[i]) == used_names.lookup(name_string_list[j])
            elif i == j:
                assert used_names.lookup(
                    name_string_list[i]) == used_names.lookup(name_string_list[j])
            else:
                break


def test_types(used_names, name_string_list):
    """Makes sure that the expected type of value is coming out of the main functions"""
    i = 0
    while i <= 2:
        assert (type(used_names.lookup(name_string_list[i]))) is int
        i += 1
