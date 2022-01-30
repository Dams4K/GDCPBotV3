class ShopErrors:
    class ShopError(Exception): pass

    class NotEnoughCoins(ShopError):
        def __init__(self, coins_needed, coins):
            self.coins_needed = coins_needed
            self.coins = coins
        def __str__(self):
            return str(self.coins_needed - self.coins)
    class HasAlreadyTheRole(ShopError): pass
    class RoleDoesntExist(ShopError): pass
    class ICantGiveYouThisRole(ShopError): pass
    class CooldownDidntFinished(ShopError):
        def __init__(self, left_time):
            self.text_date = [
                "seconde(s)",
                "minute(s)",
                "heure(s)",
                "jour(s)"
            ]
            self.left_time = left_time
        
        def __str__(self):
            text_date_conversion = 0

            # Conversion en minutes
            if self.left_time > 60:
                self.left_time /= 60
                text_date_conversion += 1
            # Conversion en heures
            if self.left_time > 60:
                self.left_time /= 60
                text_date_conversion += 1
            # Conversion en jours:
            if self.left_time > 24:
                self.left_time /= 24
                text_date_conversion += 1

            return str(int(self.left_time)) + " " + self.text_date[text_date_conversion]
