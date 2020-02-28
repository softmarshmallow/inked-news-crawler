from langdetect import detect


def accept_languages(accepted_languages:[str], title:str) -> bool:
    try:
        # 1. lang filter
        if detect(title) in accepted_languages:
            return True
        else:
            return False
    except Exception as e:
        return True
