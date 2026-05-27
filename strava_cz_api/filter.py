import json

class Filter:
    @staticmethod
    def filter_json(items, jidelnicek):
        if isinstance(items, (str, bytes)):
            keywords = [items]
        elif items is None:
            keywords = []
        else:
            keywords = list(items)

        keywords = [str(k).lower() for k in keywords if k is not None and str(k).strip()]

        is_string_input = isinstance(jidelnicek, str)
        data = json.loads(jidelnicek) if is_string_input else jidelnicek

        if not keywords:
            return json.dumps(data, ensure_ascii=False, indent=2) if is_string_input else data

        filtered = Filter._filter_top_level(data, keywords)
        return json.dumps(filtered, ensure_ascii=False, indent=2) if is_string_input else filtered

    @staticmethod
    def _filter_top_level(data, keywords):
        if isinstance(data, dict):
            filtered = {}
            for key, value in data.items():
                if isinstance(value, list):
                    filtered[key] = [Filter._filter_item(item, keywords) for item in value]
                elif isinstance(value, dict):
                    filtered[key] = Filter._filter_dict_keys(value, keywords)
                else:
                    filtered[key] = value
            return filtered

        if isinstance(data, list):
            return [Filter._filter_item(item, keywords) for item in data]

        return data

    @staticmethod
    def _filter_item(item, keywords):
        if isinstance(item, dict):
            return Filter._filter_dict_keys(item, keywords)
        if isinstance(item, list):
            return [Filter._filter_item(sub_item, keywords) for sub_item in item]
        return item

    @staticmethod
    def _filter_dict_keys(data, keywords):
        filtered = {}
        for key, value in data.items():
            if Filter._key_matches(key, keywords):
                filtered[key] = value
        return filtered

    @staticmethod
    def _key_matches(key, keywords):
        key_lower = str(key).lower()
        return any(keyword == key_lower for keyword in keywords)