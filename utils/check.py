# Fonction pour voir si une chaine de charactère peut être transformé en entier
def can_convert_to_int(msg: str) -> bool:
    try:
        int(msg)
        return True
    except:
        return False