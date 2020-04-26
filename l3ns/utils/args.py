
def list_from_args(args_list):
    try:
        return list(args_list[0])
    except (TypeError, IndexError):
        return list(args_list)
