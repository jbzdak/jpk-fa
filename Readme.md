# Simple JPK-FA generator 

Polska wersja poniżej (Polish see below). 

This is short program that generates ``JPK-FA`` files 
from simple yaml-formatted files. 

Use at your own risk

# Prosty generator JPK-FA

## Uwaga

* Nie twierdzę że ten pogram nie posiada błedów;
* Nie twierdzę że robi on poprawne pliki JPK FA; 
* Używacie na własne ryzyko;
* Nie używałem go jeszcze dla siebie (będę się widział z księgowym to sprawdzę plik JPK wygenerowany tym ustrojstwem)

## Czemu to stworzyłem 

* Jako że mój księgowy używa programu komputerowego 
  do księgowości, ja muszę wystawiać pliki JPK-FA na 
  żądanie US; 
* Wystawiam, góra, trzy faktury na miesiąc;
* Program e-mikfrofirma (dostarczony przez Ministerstwo Finansów) program do 
  księgowości nie potrafi obsłużyć kontrachentów zagranicznych (ponieważ 
  pola takie jak NIP, kod pocztowy itp walidują się do polskich formatów). 
  Do tego program ten jest mało ergonomiczny; 
* Nie mam ochoty zarządzać dziwnym programem do faktur, który 
  ściągam z internetu i który działą tylko pod Windowsem. 
* Nie mam ochoty wgrywać dokumentów do dziwnych sieciowych systemów
  księgowości (które mogą np. zniknąć). 
* W ramach riserczy znalazłem przynajmniej jedną usługę która wystawiała 
  JPK-FA niezgodnie ze schematem danych. 
* Lubie mój szablon faktury w Libre Office i chce z niego korzystać.

Uwaga: dla każdego normalnego człowieka skorzystanie z normalnego programu do księgowości ma sens.  

## Założenia

1. Program jest głupi i nie przelicza sam rzeczy poza rzeczami oczywistymi
2. Są dwie metody liczenia podatku VAT (obie poprawne) ten program działa tak
   że linie faktury mają tylko ceny netto, a potem od cen netto nalicza się 
   VAT zbiorczo
3. Do każdej faktury generujesz JPK zaraz po wystawieniu a potem US wysyłasz 
   paczkę plików JPK jak poprosi. 

## Dane źródłowe. 

Musisz stworzyć dwa pliki, jeden globalny i jeden na każdy plik JPK jaki 
chcesz generować.

Oba są w formacie yaml:

### seller.yml   

Zawiera **Twoje** dane jako wystawcy faktury. 
    
    # Tax rates array, needs to be 5 elements, elements 3 and 4 are reserved for
    # future use by the ministry
    tax_rates: [23, 8, 5, 0, 0]
    seller:
      # Seller NIP number
      tax_id: 123
      # Seller full name
      name: Seller Name
      # Seller address (I didn't want to generate address from below dict)
      address_line: Seller Address
      address:
        #  Seller address parts
        street: Seller Street
        city: Seller City
        voivoidship: Mazowieckie
        powiat: Warszawa
        gmina: Warszawa
        locality: Miejscowość
        postcode: 00-001
        homeNumber: 134
        post: Poczta
        
### invoice.yml        
    
Zawiera wszystkie dane fakturach w pliku JPK. 

Jeśli masz taką wolę możesz 
generować jpk z wieloma fakturami, do tego musisz po prostu dodać więcej elementów 
we własności invoices.  

    # If you want to override DataWytworzeniaJPK field you might do so here
    # I use it for tests.
    now: 1985-09-19
    
    # Header for JPK-FA file
    header:
      # Currency ISO code
      currency: PLN
      # From when to you were asked to provide data
      date_from: 1985-09-19
      # Until when you were asked to provide data
      date_to: 1985-09-20
      # Code for Urząd Skarbowy that requested the code. For values see
      # KodyUrzedowSkarbowych_v3-0E.xsd
      taxAuthorityCode: REPLACE_ME_WITH_GREP
    
    # List of invoices
    invoices:
    # Invoice issue date in ISO FORMAT
    - issue_date: 1985-09-19
      # Invoice NO (string)
      invoice_no: 1985/1
      # Service date. OPTIONAL
      # Data dokonania lub zakończenia dostawy towarów lub wykonania
      # usługi lub data otrzymania zapłaty, o której mowa w art. 106b ust.
      # 1 pkt 4, o ile taka data jest określona i różni się od daty wystawienia
      # faktury (pole opcjonalne)
      service_date: 1985-09-19
    
      # Grand total for invoice AFTER tax
      # If your invoice is in other Currency than PLN you should convert that to PLN
      # here
      total_after_tax: 246
    
      # Tax lines for invoice
      tax_lines:
        # Reference to tax_rates list. -1 means tax rate equal to 0%, 0 means 23%, 1 means 8%...
      - tax_rate_id: -1
        total_pre_tax: 123
      - tax_rate_id: 0
        total_pre_tax: 100
      buyer:
        name: Buyer name string
        address: Buer address string
        # Tax Id is optional if buyer has none (personal buyer and/or from outside EU)
        buyer_eu_tax_id:
          country_code: PL
          tax_id: 1234
    
      # invoice lines
      lines:
        # What you did sell
      - name: Consulting
        # Unit of quantity
        unit: hours
        # Quantity
        quantity: 1
        # Unit price before tax
        unit_price_pre_tax: 123
        # Unit price after tax
        total_pre_tax: 123
        # Reference to tax_rates list. -1 means tax rate equal to 0%, 0 means 23%, 1 means 8%...
        tax_rate: -1
      - name: Consulting
        unit: hours
        quantity: 1
        unit_price_pre_tax: 100
        total_pre_tax: 100
        total_tax: 23
        tax_rate: 1
    
## Jak tego używć

1. Instalujesz pythona 3.7 
2. Tworzysz virtualenva 
3. pip install pipenv 
4. pipenv sync --dev 
5.  python jpk-fa-cli.py --seller tests/data/seller.yml --invoice tests/data/invoice1.yml --output out.xml

        