"""
Serwis integracji z API GUS (Główny Urząd Statystyczny)
"""
import requests
import json
import xml.etree.ElementTree as ET
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

# GUS API Configuration
GUS_API_URL = "https://wyszukiwarkaregon.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc"
GUS_AJAX_URL = "https://wyszukiwarkaregon.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc/ajax/DaneSzukajPodmioty"

HEADERS = {
    'Content-Type': 'application/soap+xml; charset=utf-8',
    'User-Agent': 'FaktuLove/1.0'
}

AJAX_HEADERS = {
    'Content-Type': 'application/json',
    'User-Agent': 'FaktuLove/1.0'
}


class GUSService:
    """Service for GUS API integration"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'GUS_API_KEY', None)
        if not self.api_key:
            logger.warning("GUS_API_KEY not configured")
    
    def get_session_id(self):
        """
        Get session ID from GUS API (SOAP method)
        Cache session for 5 minutes to avoid excessive requests
        """
        if not self.api_key:
            logger.error("GUS API key not configured")
            return None
            
        # Check cache first
        session_id = cache.get('gus_session_id')
        if session_id:
            logger.info("Using cached GUS session ID")
            return session_id
        
        # SOAP request to get session - simplified approach
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:bir="http://CIS/BIR/PUBL/2014/07">
  <soap:Header />
  <soap:Body>
    <bir:Zaloguj>
      <bir:pKluczUzytkownika>{self.api_key}</bir:pKluczUzytkownika>
    </bir:Zaloguj>
  </soap:Body>
</soap:Envelope>"""

        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://CIS/BIR/PUBL/2014/07/Zaloguj',
            'User-Agent': 'FaktuLove/1.0'
        }

        try:
            logger.info("Requesting new GUS session ID")
            response = requests.post(GUS_API_URL, data=soap_body, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse SOAP response
            root = ET.fromstring(response.text)
            namespace = {"ns": "http://CIS/BIR/PUBL/2014/07"}
            session_element = root.find(".//ns:ZalogujResult", namespace)
            
            if session_element is not None and session_element.text:
                session_id = session_element.text
                # Cache for 5 minutes
                cache.set('gus_session_id', session_id, 300)
                logger.info(f"Got new GUS session ID: {session_id[:10]}...")
                return session_id
            else:
                logger.error("Failed to get session ID from GUS API response")
                return None
                
        except requests.RequestException as e:
            logger.error(f"GUS API session request failed: {e}")
            return None
        except ET.ParseError as e:
            logger.error(f"Failed to parse GUS API response: {e}")
            return None
    
    def search_by_nip(self, nip):
        """
        Search company data by NIP - simplified version with mock data for testing
        TODO: Implement proper GUS API integration when API key is properly configured
        """
        if not nip:
            return {'error': 'NIP number is required'}
        
        # Clean NIP (remove spaces, dashes)
        nip = nip.replace(' ', '').replace('-', '')
        
        # Validate NIP format
        if not nip.isdigit() or len(nip) != 10:
            return {'error': 'Invalid NIP format. Should be 10 digits.'}
        
        # For now, return mock data for demonstration
        # This should be replaced with proper GUS API integration
        logger.info(f"Mock search for NIP: {nip}")
        
        # Mock company data based on NIP
        mock_companies = {
            '1234567890': {
                'nazwa': 'Testowa Firma Sp. z o.o.',
                'ulica': 'ul. Testowa',
                'numer_domu': '123',
                'numer_mieszkania': '',
                'kod_pocztowy': '00-001',
                'miejscowosc': 'Warszawa',
                'regon': '123456789',
                'nip': nip,
                'kraj': 'Polska',
                'status': 'AKTYWNY',
                'nazwa_skrocona': 'Testowa Firma',
                'wojewodztwo': 'mazowieckie',
                'powiat': 'warszawski',
                'gmina': 'Warszawa',
            },
            '9876543210': {
                'nazwa': 'Druga Testowa Firma S.A.',
                'ulica': 'al. Główna',
                'numer_domu': '456',
                'numer_mieszkania': '78',
                'kod_pocztowy': '30-001',
                'miejscowosc': 'Kraków',
                'regon': '987654321',
                'nip': nip,
                'kraj': 'Polska',
                'status': 'AKTYWNY',
                'nazwa_skrocona': 'Druga Testowa',
                'wojewodztwo': 'małopolskie',
                'powiat': 'krakowski',
                'gmina': 'Kraków',
            }
        }
        
        if nip in mock_companies:
            result = {
                'success': True,
                'data': mock_companies[nip]
            }
            logger.info(f"Found mock company: {result['data']['nazwa']}")
            return result
        else:
            # Try basic NIP validation algorithm
            if self._validate_nip(nip):
                # Return generic company data for valid NIPs
                result = {
                    'success': True,
                    'data': {
                        'nazwa': f'Firma z NIP {nip}',
                        'ulica': 'ul. Nieznana',
                        'numer_domu': '1',
                        'numer_mieszkania': '',
                        'kod_pocztowy': '00-000',
                        'miejscowosc': 'Nieznane',
                        'regon': '',
                        'nip': nip,
                        'kraj': 'Polska',
                        'status': 'NIEZNANY',
                        'nazwa_skrocona': f'Firma {nip}',
                        'wojewodztwo': '',
                        'powiat': '',
                        'gmina': '',
                    }
                }
                logger.info(f"Generated mock data for valid NIP: {nip}")
                return result
            else:
                logger.warning(f"Invalid NIP: {nip}")
                return {'error': 'Invalid NIP number (failed checksum validation)'}
    
    def _validate_nip(self, nip):
        """
        Validate NIP using checksum algorithm
        """
        if len(nip) != 10 or not nip.isdigit():
            return False
        
        # NIP checksum validation
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        total = sum(int(nip[i]) * weights[i] for i in range(9))
        checksum = total % 11
        
        if checksum == 10:
            return False
        
        return checksum == int(nip[9])
    
    def search_by_regon(self, regon):
        """
        Search company data by REGON
        """
        if not regon:
            return {'error': 'REGON number is required'}
        
        # Clean REGON
        regon = regon.replace(' ', '').replace('-', '')
        
        # Validate REGON format (9 or 14 digits)
        if not regon.isdigit() or len(regon) not in [9, 14]:
            return {'error': 'Invalid REGON format. Should be 9 or 14 digits.'}
        
        session_id = self.get_session_id()
        if not session_id:
            return {'error': 'Failed to authenticate with GUS API'}
        
        payload = {
            'jestWojewodztwo': False,
            'pParametryWyszukiwania': {
                'Regon': regon,
            }
        }
        
        headers = AJAX_HEADERS.copy()
        headers['sid'] = session_id
        
        try:
            logger.info(f"Searching GUS for REGON: {regon}")
            response = requests.post(GUS_AJAX_URL, headers=headers, data=json.dumps(payload), timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data and isinstance(data, list) and len(data) > 0:
                company_data = data[0]
                
                result = {
                    'success': True,
                    'data': {
                        'nazwa': company_data.get('Nazwa', ''),
                        'ulica': company_data.get('Ulica', ''),
                        'numer_domu': company_data.get('NrNieruchomosci', ''),
                        'numer_mieszkania': company_data.get('NrLokalu', ''),
                        'kod_pocztowy': company_data.get('KodPocztowy', ''),
                        'miejscowosc': company_data.get('Miejscowosc', ''),
                        'regon': regon,
                        'nip': company_data.get('Nip', ''),
                        'kraj': 'Polska',
                        'status': company_data.get('StatusNip', ''),
                    }
                }
                
                logger.info(f"Found company: {result['data']['nazwa']}")
                return result
            else:
                logger.warning(f"No company found for REGON: {regon}")
                return {'error': 'Company not found in GUS database'}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"GUS API request failed: {e}")
            return {'error': f'GUS API communication error: {str(e)}'}
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Failed to parse GUS API response: {e}")
            return {'error': f'Failed to parse GUS API response: {str(e)}'}
    
    def get_detailed_data(self, regon):
        """
        Get detailed company data by REGON
        This requires additional API calls for extended information
        """
        basic_data = self.search_by_regon(regon)
        if not basic_data.get('success'):
            return basic_data
        
        # For now, return basic data
        # TODO: Implement detailed data fetching with additional SOAP calls
        return basic_data
    
    def test_connection(self):
        """
        Test GUS API connection
        """
        session_id = self.get_session_id()
        if session_id:
            return {
                'success': True,
                'message': 'GUS API connection successful',
                'session_id': session_id[:10] + '...' if len(session_id) > 10 else session_id
            }
        else:
            return {
                'success': False,
                'message': 'Failed to connect to GUS API'
            }


# Create global instance
gus_service = GUSService()
