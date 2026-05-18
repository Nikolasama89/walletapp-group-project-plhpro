"""Custom exceptions"""


class WalletError(Exception):
    """Base exception για σφάλματα της εφαρμογής."""
    pass


class NotFoundError(WalletError):
    """Όταν ζητάμε κάτι που δεν υπάρχει."""
    pass


class ValidationError(WalletError):
    """Όταν τα δεδομένα δεν είναι έγκυρα."""
    pass


class DuplicateError(WalletError):
    """Όταν υπάρχει ήδη κάτι με το ίδιο όνομα."""
    pass
