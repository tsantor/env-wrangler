"""Domain rules for working with secrets."""


def filter_keys_by_substring(input_dict: dict, words_to_keep: list[str]) -> dict:
    """Keep only keys that include any of the specified words."""
    return {
        key: input_dict[key]
        for key in input_dict
        if any(word in key for word in words_to_keep)
    }


def remove_masked_values(input_dict: dict) -> dict:
    """Remove values that are already masked."""
    return {key: value for key, value in input_dict.items() if value != "********"}
