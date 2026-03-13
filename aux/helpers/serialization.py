from functools import partial


def dict_keys_converter(
        _dict: dict,
        /,
        keys: tuple[str, ...],
        from_symbol: str,
        to_symbol: str,
) -> dict:
        """Changes symbols in dict's keys."""
        for key in keys:
            try:
                value= _dict.pop(key)
            except KeyError:
                continue
            else:
                new_key = key.replace(from_symbol, to_symbol)
                _dict[new_key] = value

        return _dict


convert_dash_to_underscore = partial(dict_keys_converter, from_symbol='-', to_symbol='_')