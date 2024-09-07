def naming_columns(model = None) -> dict or [dict]:
    """Функция для вывода данных с БД в формате dict"""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            data = func(self, *args, **kwargs)
            if data is not None:
                column_names = [i[0] for i in self.cur.description]
                if isinstance(data, list):
                    arr = []
                    for item in data:
                        res = dict(zip(column_names, item))
                        if model:
                            arr.append(model(**res))
                        else:
                            arr.append(res)
                    return arr
                res = dict(zip(column_names, data))
                return model(**res) if model else res
            return data
        return wrapper
    return decorator