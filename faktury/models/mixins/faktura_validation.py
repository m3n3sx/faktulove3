class FakturaValidationMixin:
    def clean_korekta(self):
        if self.typ_dokumentu == 'KOR' and not self.dokument_podstawowy:
            raise ValidationError("Korekta wymaga dokumentu podstawowego")

    def clean_paragon(self):
        if self.typ_dokumentu == 'PAR':
            if not self.kasa:
                raise ValidationError("Paragon wymaga numeru kasy")
            if self.metoda_platnosci != 'gotowka':
                raise ValidationError("Paragon dotyczy tylko płatności gotówkowych")

class FakturaAutoKsiegowanieMixin:
    def handle_auto_ksiegowanie(self):
        # ...extracted auto-ksiegowanie logic...