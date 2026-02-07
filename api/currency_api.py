"""
Dynamic Currency API with Real-time Exchange Rates and Country Detection
Professional implementation for playground pricing system
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.cache import cache
import json
import requests
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class DynamicCurrencyAPI(View):
    """
    Comprehensive Currency API providing real-time exchange rates and currency data
    """
    
    # Comprehensive currency database with country mappings
    CURRENCY_DATABASE = {
        'USD': {'symbol': '$', 'name': 'US Dollar', 'flag': '🇺🇸', 'decimal_places': 2, 'countries': ['US']},
        'EUR': {'symbol': '€', 'name': 'Euro', 'flag': '🇪🇺', 'decimal_places': 2, 'countries': ['DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT', 'PT', 'IE', 'FI', 'EE', 'LV', 'LT', 'LU', 'SK', 'SI', 'MT', 'CY', 'GR']},
        'GBP': {'symbol': '£', 'name': 'British Pound', 'flag': '🇬🇧', 'decimal_places': 2, 'countries': ['GB']},
        'CAD': {'symbol': 'C$', 'name': 'Canadian Dollar', 'flag': '🇨🇦', 'decimal_places': 2, 'countries': ['CA']},
        'AUD': {'symbol': 'A$', 'name': 'Australian Dollar', 'flag': '🇦🇺', 'decimal_places': 2, 'countries': ['AU']},
        'JPY': {'symbol': '¥', 'name': 'Japanese Yen', 'flag': '🇯🇵', 'decimal_places': 0, 'countries': ['JP']},
        'INR': {'symbol': '₹', 'name': 'Indian Rupee', 'flag': '🇮🇳', 'decimal_places': 2, 'countries': ['IN']},
        'BDT': {'symbol': '৳', 'name': 'Bangladeshi Taka', 'flag': '🇧🇩', 'decimal_places': 2, 'countries': ['BD']},
        'CNY': {'symbol': '¥', 'name': 'Chinese Yuan', 'flag': '🇨🇳', 'decimal_places': 2, 'countries': ['CN']},
        'CHF': {'symbol': 'Fr', 'name': 'Swiss Franc', 'flag': '🇨🇭', 'decimal_places': 2, 'countries': ['CH']},
        'SEK': {'symbol': 'kr', 'name': 'Swedish Krona', 'flag': '🇸🇪', 'decimal_places': 2, 'countries': ['SE']},
        'NOK': {'symbol': 'kr', 'name': 'Norwegian Krone', 'flag': '🇳🇴', 'decimal_places': 2, 'countries': ['NO']},
        'SGD': {'symbol': 'S$', 'name': 'Singapore Dollar', 'flag': '🇸🇬', 'decimal_places': 2, 'countries': ['SG']},
        'HKD': {'symbol': 'HK$', 'name': 'Hong Kong Dollar', 'flag': '🇭🇰', 'decimal_places': 2, 'countries': ['HK']},
        'AED': {'symbol': 'د.إ', 'name': 'UAE Dirham', 'flag': '🇦🇪', 'decimal_places': 2, 'countries': ['AE']},
        'SAR': {'symbol': '﷼', 'name': 'Saudi Riyal', 'flag': '🇸🇦', 'decimal_places': 2, 'countries': ['SA']},
        'THB': {'symbol': '฿', 'name': 'Thai Baht', 'flag': '🇹🇭', 'decimal_places': 2, 'countries': ['TH']},
        'MYR': {'symbol': 'RM', 'name': 'Malaysian Ringgit', 'flag': '🇲🇾', 'decimal_places': 2, 'countries': ['MY']},
        'KRW': {'symbol': '₩', 'name': 'South Korean Won', 'flag': '🇰🇷', 'decimal_places': 0, 'countries': ['KR']},
        'ZAR': {'symbol': 'R', 'name': 'South African Rand', 'flag': '🇿🇦', 'decimal_places': 2, 'countries': ['ZA']},
        'BRL': {'symbol': 'R$', 'name': 'Brazilian Real', 'flag': '🇧🇷', 'decimal_places': 2, 'countries': ['BR']},
        'MXN': {'symbol': '$', 'name': 'Mexican Peso', 'flag': '🇲🇽', 'decimal_places': 2, 'countries': ['MX']},
        'RUB': {'symbol': '₽', 'name': 'Russian Ruble', 'flag': '🇷🇺', 'decimal_places': 2, 'countries': ['RU']},
        'TRY': {'symbol': '₺', 'name': 'Turkish Lira', 'flag': '🇹🇷', 'decimal_places': 2, 'countries': ['TR']},
        'EGP': {'symbol': '£', 'name': 'Egyptian Pound', 'flag': '🇪🇬', 'decimal_places': 2, 'countries': ['EG']},
        'PKR': {'symbol': '₨', 'name': 'Pakistani Rupee', 'flag': '🇵🇰', 'decimal_places': 2, 'countries': ['PK']},
        'IDR': {'symbol': 'Rp', 'name': 'Indonesian Rupiah', 'flag': '🇮🇩', 'decimal_places': 0, 'countries': ['ID']},
        'PHP': {'symbol': '₱', 'name': 'Philippine Peso', 'flag': '🇵🇭', 'decimal_places': 2, 'countries': ['PH']},
        'VND': {'symbol': '₫', 'name': 'Vietnamese Dong', 'flag': '🇻🇳', 'decimal_places': 0, 'countries': ['VN']},
    }
    
    def get(self, request):
        """Handle GET requests with different actions"""
        try:
            # Check if country ID is provided for quick currency lookup
            country_id = request.GET.get('country')
            if country_id:
                return self._get_currency_by_country_id(country_id)
            
            action = request.GET.get('action', 'list')
            
            if action == 'list':
                return self._get_currency_list()
            elif action == 'detect':
                return self._detect_currency_by_country(request)
            elif action == 'rates':
                return self._get_exchange_rates(request)
            elif action == 'convert':
                return self._convert_currency(request)
            elif action == 'projection':
                return self._calculate_revenue_projection(request)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid action parameter'
                }, status=400)
                
        except Exception as e:
            logger.error(f"Currency API error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)
    
    def _get_currency_by_country_id(self, country_id):
        """Get currency by database country ID"""
        try:
            from playgrounds.models import Country
            country = Country.objects.get(id=country_id)
            currency_code = country.get_currency()
            
            # Get symbol from our database
            currency_info = self.CURRENCY_DATABASE.get(currency_code, {
                'symbol': currency_code + ' ',
                'name': currency_code,
                'flag': '🌍',
                'decimal_places': 2
            })
            
            return JsonResponse({
                'success': True,
                'country_id': int(country_id),
                'country_name': country.name,
                'currency_code': currency_code,
                'currency_symbol': currency_info['symbol'],
                'currency_name': currency_info['name'],
                'flag': currency_info['flag'],
                'decimal_places': currency_info['decimal_places']
            })
        except Exception as e:
            logger.error(f"Error getting currency for country {country_id}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Country not found',
                'currency_code': 'USD',
                'currency_symbol': '$'
            })
    
    def _get_currency_list(self):
        """Get complete list of supported currencies"""
        currencies = []
        for code, data in self.CURRENCY_DATABASE.items():
            currencies.append({
                'code': code,
                'symbol': data['symbol'],
                'name': data['name'],
                'flag': data['flag'],
                'decimal_places': data['decimal_places'],
                'display_name': f"{data['flag']} {code} - {data['name']}"
            })
        
        # Sort by name for better UX
        currencies.sort(key=lambda x: x['name'])
        
        return JsonResponse({
            'success': True,
            'currencies': currencies,
            'default_currency': 'USD',
            'total_count': len(currencies),
            'timestamp': cache.get('currency_list_timestamp') or 'live'
        })
    
    def _detect_currency_by_country(self, request):
        """Detect currency based on country code"""
        country_code = request.GET.get('country_code', '').upper()
        
        if not country_code:
            return JsonResponse({
                'success': False,
                'error': 'Country code is required'
            }, status=400)
        
        # Find currency by country code
        detected_currency = None
        for code, data in self.CURRENCY_DATABASE.items():
            if country_code in data['countries']:
                detected_currency = {
                    'code': code,
                    'symbol': data['symbol'],
                    'name': data['name'],
                    'flag': data['flag'],
                    'decimal_places': data['decimal_places']
                }
                break
        
        if not detected_currency:
            # Default to USD if country not found
            detected_currency = {
                'code': 'USD',
                'symbol': '$',
                'name': 'US Dollar',
                'flag': '🇺🇸',
                'decimal_places': 2
            }
        
        return JsonResponse({
            'success': True,
            'country_code': country_code,
            'detected_currency': detected_currency,
            'auto_detected': True
        })
    
    def _get_exchange_rates(self, request):
        """Get real-time exchange rates"""
        base_currency = request.GET.get('base', 'USD')
        
        # Check cache first (1 hour expiry)
        cache_key = f"exchange_rates_{base_currency}"
        cached_rates = cache.get(cache_key)
        
        if cached_rates:
            return JsonResponse({
                'success': True,
                'base_currency': base_currency,
                'rates': cached_rates['rates'],
                'cached': True,
                'timestamp': cached_rates['timestamp'],
                'expires_at': cached_rates.get('expires_at')
            })
        
        try:
            # Use free exchange rate API
            api_url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                rates = data.get('rates', {})
                
                # Cache for 1 hour
                cache_data = {
                    'rates': rates,
                    'timestamp': data.get('date'),
                    'expires_at': 'in 1 hour'
                }
                cache.set(cache_key, cache_data, 3600)
                
                return JsonResponse({
                    'success': True,
                    'base_currency': base_currency,
                    'rates': rates,
                    'cached': False,
                    'timestamp': data.get('date'),
                    'source': 'live_api'
                })
            else:
                return self._get_fallback_rates(base_currency)
                
        except requests.RequestException:
            return self._get_fallback_rates(base_currency)
    
    def _get_fallback_rates(self, base_currency):
        """Provide fallback exchange rates when API is unavailable"""
        fallback_rates = {
            'USD': {
                'EUR': 0.85, 'GBP': 0.73, 'CAD': 1.25, 'AUD': 1.35, 'JPY': 110, 
                'INR': 74, 'BDT': 85, 'CNY': 6.5, 'CHF': 0.92, 'SEK': 8.5
            },
            'EUR': {
                'USD': 1.18, 'GBP': 0.86, 'CAD': 1.47, 'AUD': 1.59, 'JPY': 129, 
                'INR': 87, 'BDT': 100, 'CNY': 7.6, 'CHF': 1.08, 'SEK': 10.0
            }
        }
        
        rates = fallback_rates.get(base_currency, fallback_rates['USD'])
        
        return JsonResponse({
            'success': True,
            'base_currency': base_currency,
            'rates': rates,
            'cached': False,
            'fallback': True,
            'timestamp': 'fallback_data',
            'note': 'Using fallback rates - API temporarily unavailable'
        })
    
    def _convert_currency(self, request):
        """Convert amount between currencies"""
        try:
            amount = float(request.GET.get('amount', 0))
            from_currency = request.GET.get('from', 'USD')
            to_currency = request.GET.get('to', 'USD')
            
            if amount <= 0:
                return JsonResponse({
                    'success': False,
                    'error': 'Amount must be greater than 0'
                }, status=400)
            
            # Get exchange rates
            rates_request = type('obj', (object,), {'GET': {'base': from_currency}})
            rates_response = self._get_exchange_rates(rates_request)
            rates_data = json.loads(rates_response.content)
            
            if not rates_data.get('success'):
                return JsonResponse({
                    'success': False,
                    'error': 'Unable to get exchange rates'
                }, status=500)
            
            rates = rates_data.get('rates', {})
            
            if from_currency == to_currency:
                converted_amount = amount
                rate = 1
            else:
                rate = rates.get(to_currency, 1)
                converted_amount = amount * rate
            
            # Get currency symbols
            from_data = self.CURRENCY_DATABASE.get(from_currency, {'symbol': from_currency})
            to_data = self.CURRENCY_DATABASE.get(to_currency, {'symbol': to_currency})
            
            return JsonResponse({
                'success': True,
                'conversion': {
                    'original_amount': amount,
                    'converted_amount': round(converted_amount, to_data.get('decimal_places', 2)),
                    'from_currency': from_currency,
                    'to_currency': to_currency,
                    'from_symbol': from_data['symbol'],
                    'to_symbol': to_data['symbol'],
                    'exchange_rate': round(rate, 6),
                    'formatted_original': f"{from_data['symbol']}{amount:,.{from_data.get('decimal_places', 2)}f}",
                    'formatted_converted': f"{to_data['symbol']}{converted_amount:,.{to_data.get('decimal_places', 2)}f}"
                }
            })
            
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid amount provided'
            }, status=400)
    
    def _calculate_revenue_projection(self, request):
        """Calculate revenue projections with current currency"""
        try:
            hourly_rate = float(request.GET.get('amount', 25.00))
            currency = request.GET.get('currency', 'USD')
            
            # Get currency data
            currency_data = self.CURRENCY_DATABASE.get(currency, {
                'symbol': '$', 'name': 'US Dollar', 'flag': '🇺🇸', 'decimal_places': 2
            })
            
            # Revenue calculation parameters
            daily_hours = 8  # Average daily operating hours
            monthly_days = 25  # Average bookable days per month
            occupancy_rate = 0.6  # 60% occupancy rate
            
            # Calculate projections
            daily_revenue = hourly_rate * daily_hours * occupancy_rate
            monthly_revenue = daily_revenue * monthly_days
            yearly_revenue = monthly_revenue * 12
            
            decimal_places = currency_data.get('decimal_places', 2)
            
            return JsonResponse({
                'success': True,
                'currency': {
                    'code': currency,
                    'symbol': currency_data['symbol'],
                    'name': currency_data['name'],
                    'flag': currency_data['flag'],
                    'decimal_places': decimal_places
                },
                'pricing': {
                    'hourly_rate': hourly_rate,
                    'formatted_hourly': f"{currency_data['symbol']}{hourly_rate:,.{decimal_places}f}"
                },
                'revenue_projection': {
                    'daily': {
                        'amount': round(daily_revenue, decimal_places),
                        'formatted': f"{currency_data['symbol']}{daily_revenue:,.{decimal_places}f}"
                    },
                    'monthly': {
                        'amount': round(monthly_revenue, decimal_places),
                        'formatted': f"{currency_data['symbol']}{monthly_revenue:,.{decimal_places}f}"
                    },
                    'yearly': {
                        'amount': round(yearly_revenue, decimal_places),
                        'formatted': f"{currency_data['symbol']}{yearly_revenue:,.{decimal_places}f}"
                    },
                    'assumptions': {
                        'daily_hours': daily_hours,
                        'monthly_days': monthly_days,
                        'occupancy_rate': f"{occupancy_rate * 100}%",
                        'currency': currency
                    }
                },
                'live_rates': True,
                'timestamp': cache.get('currency_timestamp') or 'live'
            })
            
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid amount provided'
            }, status=400)


@csrf_exempt
def detect_user_currency(request):
    """
    Detect user's currency based on playground location
    """
    if request.method == 'GET':
        try:
            # Try to get playground ID directly from request
            playground_id = request.GET.get('playground_id', '')
            country_code = request.GET.get('country', '').upper()
            
            # If playground ID is provided, use it directly
            if playground_id:
                try:
                    from playgrounds.models import Playground
                    playground = Playground.objects.get(id=int(playground_id))
                    if playground.city and playground.city.state and playground.city.state.country:
                        country_name = playground.city.state.country.name.lower()
                        
                        # Map country names to currency codes
                        country_currency_map = {
                            'malaysia': 'MYR',
                            'singapore': 'SGD', 
                            'indonesia': 'IDR',
                            'thailand': 'THB',
                            'united states': 'USD',
                            'usa': 'USD',
                            'united kingdom': 'GBP',
                            'uk': 'GBP',
                            'britain': 'GBP',
                            'england': 'GBP',
                            'canada': 'CAD',
                            'australia': 'AUD',
                            'india': 'INR',
                            'bangladesh': 'BDT',
                            'china': 'CNY',
                            'japan': 'JPY',
                            'south korea': 'KRW',
                            'korea': 'KRW',
                            'pakistan': 'PKR',
                            'philippines': 'PHP',
                            'vietnam': 'VND'
                        }
                        
                        currency_code = country_currency_map.get(country_name, 'USD')
                        
                        # Get currency data from our database
                        api = DynamicCurrencyAPI()
                        currency_data = api.CURRENCY_DATABASE.get(currency_code)
                        
                        if currency_data:
                            return JsonResponse({
                                'success': True,
                                'currency': {
                                    'code': currency_code,
                                    'symbol': currency_data['symbol'],
                                    'name': currency_data['name'],
                                    'flag': currency_data['flag'],
                                    'decimal_places': currency_data['decimal_places'],
                                    'rate': 1
                                },
                                'auto_detected': True,
                                'source': 'playground_location',
                                'country': country_name.title(),
                                'playground_id': playground_id
                            })
                except Exception as e:
                    logger.error(f"Error getting playground {playground_id}: {str(e)}")
            
            # If no playground ID, try to detect from referrer
            if not country_code:
                referer = request.META.get('HTTP_REFERER', '')
                if 'playground/details/' in referer or '/details/' in referer:
                    try:
                        from playgrounds.models import Playground
                        # Extract playground ID from URL
                        url_parts = referer.split('/')
                        for i, part in enumerate(url_parts):
                            if part == 'details' and i + 1 < len(url_parts):
                                playground_id = url_parts[i + 1]
                                break
                        
                        if playground_id:
                            playground = Playground.objects.get(id=int(playground_id))
                            if playground.city and playground.city.state and playground.city.state.country:
                                country_name = playground.city.state.country.name.lower()
                                
                                country_currency_map = {
                                    'malaysia': 'MYR',
                                    'singapore': 'SGD', 
                                    'indonesia': 'IDR',
                                    'thailand': 'THB',
                                    'united states': 'USD',
                                    'united kingdom': 'GBP',
                                    'canada': 'CAD',
                                    'australia': 'AUD',
                                    'india': 'INR',
                                    'bangladesh': 'BDT',
                                    'china': 'CNY',
                                    'japan': 'JPY',
                                    'south korea': 'KRW',
                                    'pakistan': 'PKR',
                                    'philippines': 'PHP',
                                    'vietnam': 'VND'
                                }
                                
                                currency_code = country_currency_map.get(country_name, 'USD')
                                
                                # Get currency data from our database
                                api = DynamicCurrencyAPI()
                                currency_data = api.CURRENCY_DATABASE.get(currency_code)
                                
                                if currency_data:
                                    return JsonResponse({
                                        'success': True,
                                        'currency': {
                                            'code': currency_code,
                                            'symbol': currency_data['symbol'],
                                            'name': currency_data['name'],
                                            'flag': currency_data['flag'],
                                            'decimal_places': currency_data['decimal_places'],
                                            'rate': 1
                                        },
                                        'auto_detected': True,
                                        'source': 'playground_location',
                                        'country': country_name.title()
                                    })
                    except Exception as e:
                        logger.error(f"Error detecting currency from playground: {str(e)}")
            
            # Default fallback to USD
            return JsonResponse({
                'success': True,
                'currency': {
                    'code': 'USD',
                    'symbol': '$',
                    'name': 'US Dollar',
                    'flag': '🇺🇸',
                    'decimal_places': 2,
                    'rate': 1
                },
                'auto_detected': False,
                'source': 'default'
            })
            
        except Exception as e:
            logger.error(f"Currency detection error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Currency detection failed'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Only GET method allowed'
    }, status=405)
