"""
Advanced Sport Types API for Professional Playground System
==========================================================
This module provides comprehensive sport type management with dynamic features,
real-time data integration, and professional-grade customization options.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.db import transaction
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Professional Sport Types Database with Advanced Features
PROFESSIONAL_SPORT_TYPES = {
    'football': {
        'id': 'football',
        'name': 'Football',
        'display_name': 'Professional Football',
        'icon': '⚽',
        'emoji': '⚽',
        'category': 'team_sport',
        'description': 'Professional football training and matches with FIFA-standard facilities',
        'short_description': 'FIFA-standard football facilities',
        'facilities': {
            'field_type': 'Natural/Artificial Grass',
            'field_size': '100m x 64m (FIFA Standard)',
            'goal_posts': 'Professional Steel Goals',
            'lighting': 'LED Floodlights',
            'seating': 'Stadium Seating Available',
            'dressing_rooms': 'Professional Changing Facilities',
            'equipment_storage': 'Secure Equipment Storage'
        },
        'features': [
            'Professional Goal Posts',
            'FIFA Standard Pitch',
            'Video Analysis System',
            'Professional Referee',
            'Team Tactical Board',
            'Medical Kit Available',
            'Ball Collection Service',
            'Match Statistics',
            'Live Streaming Setup',
            'VAR System (Premium)'
        ],
        'equipment_included': [
            'Professional Footballs',
            'Training Cones',
            'Goal Nets',
            'Corner Flags',
            'Bibs/Pinnies',
            'First Aid Kit'
        ],
        'coaching_options': [
            'Youth Development Coach',
            'Professional Trainer',
            'Goalkeeper Specialist',
            'Tactical Analyst',
            'Fitness Coach'
        ],
        'pricing': {
            'base_price': 150.0,
            'currency': 'USD',
            'peak_hours_multiplier': 1.5,
            'weekend_multiplier': 1.3,
            'tournament_multiplier': 2.0,
            'coaching_fee': 50.0
        },
        'time_constraints': {
            'min_duration': 90,  # minutes
            'max_duration': 180,
            'preferred_duration': 120,
            'break_between_sessions': 15
        },
        'capacity': {
            'min_players': 6,
            'max_players': 22,
            'optimal_players': 18,
            'spectators': 100
        },
        'professional_leagues': [
            'Local Amateur League',
            'Youth Development League',
            'Corporate Championship',
            'Weekend Warriors League'
        ],
        'seasonal_availability': {
            'peak_season': ['september', 'october', 'november', 'december', 'january', 'february'],
            'off_season': ['june', 'july', 'august'],
            'year_round': True
        }
    },
    
    'basketball': {
        'id': 'basketball',
        'name': 'Basketball',
        'display_name': 'Professional Basketball',
        'icon': '🏀',
        'emoji': '🏀',
        'category': 'team_sport',
        'description': 'NBA-standard basketball courts with professional training facilities',
        'short_description': 'NBA-standard basketball courts',
        'facilities': {
            'court_type': 'Hardwood/Synthetic Court',
            'court_size': '28m x 15m (FIBA Standard)',
            'hoops': 'Professional Breakaway Rims',
            'lighting': 'Anti-glare LED System',
            'seating': 'Bleacher Seating',
            'sound_system': 'Professional Audio',
            'scoreboard': 'Electronic Scoreboard'
        },
        'features': [
            'Professional Basketball Hoops',
            'Shot Clock System',
            'Performance Analytics',
            'Professional Referee',
            'Video Recording',
            'Strength Training Area',
            'Recovery Zone',
            'Tactical Whiteboard'
        ],
        'equipment_included': [
            'Professional Basketballs',
            'Training Equipment',
            'First Aid Kit',
            'Ball Rack',
            'Cleaning Supplies'
        ],
        'coaching_options': [
            'Skills Development Coach',
            'Shooting Specialist',
            'Defensive Coordinator',
            'Youth Coach',
            'Fitness Trainer'
        ],
        'pricing': {
            'base_price': 120.0,
            'currency': 'USD',
            'peak_hours_multiplier': 1.4,
            'weekend_multiplier': 1.2,
            'tournament_multiplier': 1.8,
            'coaching_fee': 40.0
        },
        'time_constraints': {
            'min_duration': 60,
            'max_duration': 150,
            'preferred_duration': 90,
            'break_between_sessions': 10
        },
        'capacity': {
            'min_players': 4,
            'max_players': 12,
            'optimal_players': 10,
            'spectators': 80
        }
    },
    
    'tennis': {
        'id': 'tennis',
        'name': 'Tennis',
        'display_name': 'Professional Tennis',
        'icon': '🎾',
        'emoji': '🎾',
        'category': 'racquet_sport',
        'description': 'Wimbledon-quality tennis courts with professional coaching',
        'short_description': 'Wimbledon-quality tennis courts',
        'facilities': {
            'court_type': 'Clay/Hard/Grass Courts',
            'court_size': '23.77m x 10.97m (ITF Standard)',
            'net': 'Professional Tennis Net',
            'lighting': 'LED Court Lighting',
            'seating': 'Courtside Seating',
            'ball_machine': 'Available on Request',
            'practice_wall': 'Rebound Wall Available'
        },
        'features': [
            'Professional Tennis Courts',
            'Ball Machine Access',
            'Video Analysis',
            'Line Calling System',
            'Professional Coaching',
            'Fitness Assessment',
            'Match Play Organization',
            'Tournament Hosting'
        ],
        'equipment_included': [
            'Professional Tennis Balls',
            'Court Maintenance',
            'First Aid Kit',
            'Ball Hopper',
            'Court Squeegee'
        ],
        'coaching_options': [
            'Professional Tennis Coach',
            'Junior Development Coach',
            'Tournament Preparation',
            'Technique Specialist',
            'Mental Game Coach'
        ],
        'pricing': {
            'base_price': 80.0,
            'currency': 'USD',
            'peak_hours_multiplier': 1.3,
            'weekend_multiplier': 1.2,
            'tournament_multiplier': 1.5,
            'coaching_fee': 60.0
        },
        'time_constraints': {
            'min_duration': 60,
            'max_duration': 180,
            'preferred_duration': 90,
            'break_between_sessions': 15
        },
        'capacity': {
            'min_players': 2,
            'max_players': 4,
            'optimal_players': 2,
            'spectators': 40
        }
    },
    
    'badminton': {
        'id': 'badminton',
        'name': 'Badminton',
        'display_name': 'Professional Badminton',
        'icon': '🏸',
        'emoji': '🏸',
        'category': 'racquet_sport',
        'description': 'Olympic-standard badminton courts with professional equipment',
        'short_description': 'Olympic-standard badminton courts',
        'facilities': {
            'court_type': 'Wooden/PVC Court',
            'court_size': '13.4m x 6.1m (BWF Standard)',
            'net': 'Professional Badminton Net',
            'lighting': 'Shadow-free LED Lighting',
            'flooring': 'Professional Sports Flooring',
            'ventilation': 'Climate Controlled',
            'seating': 'Courtside Benches'
        },
        'features': [
            'Professional Badminton Courts',
            'Shuttlecock Supply',
            'Racket Rental Service',
            'Professional Coaching',
            'Tournament Organization',
            'Performance Tracking',
            'Video Analysis',
            'Injury Prevention Program'
        ],
        'equipment_included': [
            'Professional Shuttlecocks',
            'Court Maintenance',
            'First Aid Kit',
            'Shuttlecock Tubes',
            'Court Cleaning'
        ],
        'coaching_options': [
            'Professional Badminton Coach',
            'Junior Coach',
            'Doubles Specialist',
            'Singles Specialist',
            'Fitness Coach'
        ],
        'pricing': {
            'base_price': 45.0,
            'currency': 'USD',
            'peak_hours_multiplier': 1.3,
            'weekend_multiplier': 1.2,
            'tournament_multiplier': 1.6,
            'coaching_fee': 35.0
        },
        'time_constraints': {
            'min_duration': 45,
            'max_duration': 120,
            'preferred_duration': 60,
            'break_between_sessions': 10
        },
        'capacity': {
            'min_players': 2,
            'max_players': 4,
            'optimal_players': 2,
            'spectators': 30
        }
    },
    
    'swimming': {
        'id': 'swimming',
        'name': 'Swimming',
        'display_name': 'Professional Swimming',
        'icon': '🏊',
        'emoji': '🏊‍♂️',
        'category': 'aquatic_sport',
        'description': 'Olympic-size swimming pool with professional training facilities',
        'short_description': 'Olympic-size swimming facilities',
        'facilities': {
            'pool_type': 'Olympic Size Pool',
            'pool_size': '50m x 25m',
            'lanes': '8 Competition Lanes',
            'depth': '2m Minimum',
            'temperature': 'Heated Pool (26-28°C)',
            'timing_system': 'Electronic Timing',
            'starting_blocks': 'Professional Starting Blocks'
        },
        'features': [
            'Olympic Size Pool',
            'Lane Reservation',
            'Timing System',
            'Professional Coaching',
            'Stroke Analysis',
            'Fitness Assessment',
            'Recovery Facilities',
            'Aqua Fitness Classes'
        ],
        'equipment_included': [
            'Lane Ropes',
            'Kickboards',
            'Pull Buoys',
            'Pool Safety Equipment',
            'Cleaning Supplies'
        ],
        'coaching_options': [
            'Professional Swim Coach',
            'Technique Specialist',
            'Competitive Training Coach',
            'Aqua Fitness Instructor',
            'Safety Instructor'
        ],
        'pricing': {
            'base_price': 35.0,
            'currency': 'USD',
            'peak_hours_multiplier': 1.2,
            'weekend_multiplier': 1.1,
            'tournament_multiplier': 1.5,
            'coaching_fee': 45.0
        },
        'time_constraints': {
            'min_duration': 45,
            'max_duration': 120,
            'preferred_duration': 60,
            'break_between_sessions': 15
        },
        'capacity': {
            'min_swimmers': 1,
            'max_swimmers': 16,
            'optimal_swimmers': 8,
            'spectators': 50
        }
    },
    
    'gym_fitness': {
        'id': 'gym_fitness',
        'name': 'Gym & Fitness',
        'display_name': 'Professional Gym & Fitness',
        'icon': '💪',
        'emoji': '💪',
        'category': 'fitness',
        'description': 'State-of-the-art fitness center with professional equipment and training',
        'short_description': 'Professional fitness center',
        'facilities': {
            'equipment': 'Latest Fitness Equipment',
            'cardio_zone': 'Modern Cardio Machines',
            'weight_area': 'Free Weights & Machines',
            'functional_area': 'Functional Training Zone',
            'group_studio': 'Group Fitness Studio',
            'recovery_zone': 'Stretching & Recovery Area',
            'locker_rooms': 'Premium Locker Facilities'
        },
        'features': [
            'Personal Training',
            'Group Fitness Classes',
            'Nutrition Consultation',
            'Fitness Assessment',
            'Progress Tracking',
            'Recovery Services',
            'Wellness Programs',
            'Equipment Orientation'
        ],
        'equipment_included': [
            'Full Access to Equipment',
            'Towel Service',
            'Water Bottles',
            'Fitness Tracker',
            'Workout Programs'
        ],
        'coaching_options': [
            'Personal Trainer',
            'Group Fitness Instructor',
            'Nutrition Coach',
            'Wellness Coach',
            'Strength Coach'
        ],
        'pricing': {
            'base_price': 25.0,
            'currency': 'USD',
            'peak_hours_multiplier': 1.2,
            'weekend_multiplier': 1.1,
            'membership_discount': 0.8,
            'coaching_fee': 50.0
        },
        'time_constraints': {
            'min_duration': 60,
            'max_duration': 180,
            'preferred_duration': 90,
            'break_between_sessions': 10
        },
        'capacity': {
            'min_users': 1,
            'max_users': 50,
            'optimal_users': 25,
            'spectators': 0
        }
    },
    
    'volleyball': {
        'id': 'volleyball',
        'name': 'Volleyball',
        'display_name': 'Professional Volleyball',
        'icon': '🏐',
        'emoji': '🏐',
        'category': 'team_sport',
        'description': 'FIVB-standard volleyball courts for professional play',
        'short_description': 'FIVB-standard volleyball courts',
        'facilities': {
            'court_type': 'Indoor/Beach Volleyball',
            'court_size': '18m x 9m (FIVB Standard)',
            'net': 'Professional Volleyball Net',
            'flooring': 'Professional Sports Flooring',
            'lighting': 'Competition Standard Lighting',
            'seating': 'Team Benches & Spectator Seating',
            'scoreboard': 'Electronic Scoreboard'
        },
        'features': [
            'Professional Volleyball Courts',
            'Official Net Heights',
            'Match Officials',
            'Video Recording',
            'Training Equipment',
            'Skill Development',
            'Team Building',
            'Tournament Hosting'
        ],
        'equipment_included': [
            'Professional Volleyballs',
            'Net System',
            'Line Markers',
            'First Aid Kit',
            'Ball Cart'
        ],
        'coaching_options': [
            'Volleyball Coach',
            'Beach Volleyball Specialist',
            'Youth Development Coach',
            'Technique Coach',
            'Team Strategy Coach'
        ],
        'pricing': {
            'base_price': 100.0,
            'currency': 'USD',
            'peak_hours_multiplier': 1.4,
            'weekend_multiplier': 1.2,
            'tournament_multiplier': 1.7,
            'coaching_fee': 40.0
        },
        'time_constraints': {
            'min_duration': 90,
            'max_duration': 180,
            'preferred_duration': 120,
            'break_between_sessions': 15
        },
        'capacity': {
            'min_players': 6,
            'max_players': 12,
            'optimal_players': 12,
            'spectators': 60
        }
    },
    
    'cricket': {
        'id': 'cricket',
        'name': 'Cricket',
        'display_name': 'Professional Cricket',
        'icon': '🏏',
        'emoji': '🏏',
        'category': 'team_sport',
        'description': 'ICC-standard cricket grounds with professional facilities',
        'short_description': 'ICC-standard cricket facilities',
        'facilities': {
            'ground_type': 'Turf/Artificial Pitch',
            'pitch_size': '22 yards (ICC Standard)',
            'boundary': '60-70m radius',
            'pavilion': 'Players Pavilion',
            'nets': 'Practice Net Facilities',
            'scoreboard': 'Electronic Scoreboard',
            'commentary_box': 'Commentary Facilities'
        },
        'features': [
            'Professional Cricket Pitch',
            'Practice Net Facilities',
            'Professional Umpiring',
            'Match Analysis',
            'Video Recording',
            'Player Statistics',
            'Equipment Storage',
            'Match Day Services'
        ],
        'equipment_included': [
            'Cricket Balls',
            'Stumps & Bails',
            'Boundary Markers',
            'First Aid Kit',
            'Ground Maintenance'
        ],
        'coaching_options': [
            'Professional Cricket Coach',
            'Batting Specialist',
            'Bowling Coach',
            'Wicket Keeping Coach',
            'Youth Development Coach'
        ],
        'pricing': {
            'base_price': 200.0,
            'currency': 'USD',
            'peak_hours_multiplier': 1.5,
            'weekend_multiplier': 1.3,
            'tournament_multiplier': 2.5,
            'coaching_fee': 60.0
        },
        'time_constraints': {
            'min_duration': 180,
            'max_duration': 480,
            'preferred_duration': 300,
            'break_between_sessions': 30
        },
        'capacity': {
            'min_players': 6,
            'max_players': 22,
            'optimal_players': 22,
            'spectators': 200
        }
    }
}

# Sport Categories for Organization
SPORT_CATEGORIES = {
    'team_sport': {
        'name': 'Team Sports',
        'description': 'Sports requiring team coordination and strategy',
        'icon': '🏆',
        'sports': ['football', 'basketball', 'volleyball', 'cricket']
    },
    'racquet_sport': {
        'name': 'Racquet Sports',
        'description': 'Individual or doubles sports with racquets',
        'icon': '🎾',
        'sports': ['tennis', 'badminton']
    },
    'aquatic_sport': {
        'name': 'Aquatic Sports',
        'description': 'Water-based sports and activities',
        'icon': '🏊',
        'sports': ['swimming']
    },
    'fitness': {
        'name': 'Fitness & Training',
        'description': 'Fitness, strength training, and wellness',
        'icon': '💪',
        'sports': ['gym_fitness']
    }
}

@csrf_exempt
@require_http_methods(["GET", "POST"])
def get_sport_types(request):
    """
    Get all available sport types with comprehensive details
    """
    try:
        if request.method == 'GET':
            return JsonResponse({
                'success': True,
                'sport_types': PROFESSIONAL_SPORT_TYPES,
                'categories': SPORT_CATEGORIES,
                'total_sports': len(PROFESSIONAL_SPORT_TYPES),
                'last_updated': datetime.now().isoformat()
            })
        
        elif request.method == 'POST':
            # Handle sport type filtering/searching
            data = json.loads(request.body)
            category_filter = data.get('category')
            search_term = data.get('search', '').lower()
            
            filtered_sports = {}
            
            for sport_id, sport_data in PROFESSIONAL_SPORT_TYPES.items():
                # Apply category filter
                if category_filter and sport_data['category'] != category_filter:
                    continue
                
                # Apply search filter
                if search_term:
                    searchable_text = f"{sport_data['name']} {sport_data['description']} {' '.join(sport_data['features'])}".lower()
                    if search_term not in searchable_text:
                        continue
                
                filtered_sports[sport_id] = sport_data
            
            return JsonResponse({
                'success': True,
                'sport_types': filtered_sports,
                'total_found': len(filtered_sports),
                'filters_applied': {
                    'category': category_filter,
                    'search': search_term
                }
            })
    
    except Exception as e:
        logger.error(f"Error in get_sport_types: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve sport types'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_sport_details(request, sport_id):
    """
    Get detailed information for a specific sport type
    """
    try:
        if sport_id not in PROFESSIONAL_SPORT_TYPES:
            return JsonResponse({
                'success': False,
                'error': 'Sport type not found'
            }, status=404)
        
        sport_data = PROFESSIONAL_SPORT_TYPES[sport_id]
        
        # Calculate dynamic pricing based on current time
        current_hour = datetime.now().hour
        is_peak_hour = 17 <= current_hour <= 21  # 5 PM to 9 PM
        is_weekend = datetime.now().weekday() >= 5
        
        base_price = sport_data['pricing']['base_price']
        current_price = base_price
        
        if is_peak_hour:
            current_price *= sport_data['pricing']['peak_hours_multiplier']
        
        if is_weekend:
            current_price *= sport_data['pricing']['weekend_multiplier']
        
        # Add real-time availability (simulated)
        availability_slots = generate_availability_slots(sport_data)
        
        enhanced_data = {
            **sport_data,
            'current_pricing': {
                'base_price': base_price,
                'current_price': round(current_price, 2),
                'is_peak_hour': is_peak_hour,
                'is_weekend': is_weekend,
                'next_price_change': calculate_next_price_change()
            },
            'availability': availability_slots,
            'popularity_score': calculate_popularity_score(sport_id),
            'recommended_duration': sport_data['time_constraints']['preferred_duration']
        }
        
        return JsonResponse({
            'success': True,
            'sport': enhanced_data,
            'category_info': SPORT_CATEGORIES.get(sport_data['category'], {})
        })
    
    except Exception as e:
        logger.error(f"Error in get_sport_details: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve sport details'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def calculate_sport_pricing(request):
    """
    Calculate dynamic pricing for sport bookings
    """
    try:
        data = json.loads(request.body)
        sport_id = data.get('sport_id')
        duration = data.get('duration', 60)
        date_time = data.get('date_time')
        participants = data.get('participants', 1)
        features = data.get('features', [])
        
        if sport_id not in PROFESSIONAL_SPORT_TYPES:
            return JsonResponse({
                'success': False,
                'error': 'Invalid sport type'
            }, status=400)
        
        sport_data = PROFESSIONAL_SPORT_TYPES[sport_id]
        base_price = sport_data['pricing']['base_price']
        
        # Parse booking datetime
        if date_time:
            booking_dt = datetime.fromisoformat(date_time)
        else:
            booking_dt = datetime.now()
        
        # Calculate multipliers
        multipliers = {
            'base': 1.0,
            'peak_hour': 1.0,
            'weekend': 1.0,
            'duration': 1.0,
            'capacity': 1.0,
            'features': 1.0,
            'membership': 1.0,
            'seasonal': 1.0
        }
        
        # Peak hour multiplier
        if 17 <= booking_dt.hour <= 21:
            multipliers['peak_hour'] = sport_data['pricing'].get('peak_hours_multiplier', 1.0)
        
        # Weekend multiplier
        if booking_dt.weekday() >= 5:
            multipliers['weekend'] = sport_data['pricing'].get('weekend_multiplier', 1.0)
        
        # Duration multiplier (longer sessions get slight discount)
        if duration > sport_data['time_constraints']['preferred_duration']:
            multipliers['duration'] = 0.95
        
        # Capacity multiplier (larger groups)
        optimal_capacity = sport_data['capacity'].get('optimal_players', sport_data['capacity'].get('optimal_users', 10))
        if participants > optimal_capacity:
            multipliers['capacity'] = 1.1
        
        # Membership discount for gym/fitness
        if 'membership' in features or sport_id == 'gym_fitness':
            multipliers['membership'] = sport_data['pricing'].get('membership_discount', 1.0)
        
        # Features multiplier
        feature_cost = len(features) * 5.0  # $5 per feature
        
        # Calculate final price
        total_multiplier = 1.0
        for multiplier in multipliers.values():
            total_multiplier *= multiplier
        
        session_price = base_price * total_multiplier
        total_price = session_price + feature_cost
        
        # Add coaching if requested
        coaching_price = 0
        if 'coaching' in features:
            coaching_price = sport_data['pricing']['coaching_fee']
            total_price += coaching_price
        
        pricing_breakdown = {
            'base_price': base_price,
            'session_price': round(session_price, 2),
            'feature_cost': feature_cost,
            'coaching_cost': coaching_price,
            'total_price': round(total_price, 2),
            'multipliers': multipliers,
            'currency': sport_data['pricing']['currency'],
            'savings': round(max(0, base_price * 0.1), 2) if duration > 120 else 0
        }
        
        return JsonResponse({
            'success': True,
            'pricing': pricing_breakdown,
            'booking_details': {
                'sport': sport_data['display_name'],
                'duration': duration,
                'participants': participants,
                'date_time': booking_dt.isoformat(),
                'features': features
            }
        })
    
    except Exception as e:
        logger.error(f"Error in calculate_sport_pricing: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to calculate pricing'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_sport_availability(request, sport_id):
    """
    Get real-time availability for a specific sport
    """
    try:
        if sport_id not in PROFESSIONAL_SPORT_TYPES:
            return JsonResponse({
                'success': False,
                'error': 'Sport type not found'
            }, status=404)
        
        sport_data = PROFESSIONAL_SPORT_TYPES[sport_id]
        
        # Generate availability for next 7 days
        availability = {}
        start_date = datetime.now().date()
        
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            daily_slots = generate_daily_availability(sport_data, current_date)
            availability[current_date.isoformat()] = daily_slots
        
        return JsonResponse({
            'success': True,
            'sport_id': sport_id,
            'sport_name': sport_data['display_name'],
            'availability': availability,
            'time_constraints': sport_data['time_constraints'],
            'capacity': sport_data['capacity']
        })
    
    except Exception as e:
        logger.error(f"Error in get_sport_availability: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve availability'
        }, status=500)

def generate_availability_slots(sport_data):
    """Generate available time slots for a sport"""
    slots = []
    current_time = datetime.now()
    
    # Generate slots for today and tomorrow
    for day_offset in range(2):
        day = current_time + timedelta(days=day_offset)
        
        # Operating hours: 6 AM to 11 PM
        for hour in range(6, 23):
            slot_time = day.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            # Skip past time slots for today
            if day_offset == 0 and slot_time <= current_time:
                continue
            
            # Simulate availability (80% chance of being available)
            import random
            is_available = random.random() > 0.2
            
            slots.append({
                'time': slot_time.isoformat(),
                'available': is_available,
                'capacity_remaining': sport_data['capacity']['max_players'] if is_available else 0
            })
    
    return slots[:20]  # Return first 20 slots

def generate_daily_availability(sport_data, date):
    """Generate availability slots for a specific date"""
    slots = []
    
    # Operating hours: 6 AM to 11 PM
    for hour in range(6, 23):
        # Generate slots every hour
        slot_time = datetime.combine(date, datetime.min.time().replace(hour=hour))
        
        # Simulate availability
        import random
        is_available = random.random() > 0.3
        
        slots.append({
            'time': slot_time.time().isoformat(),
            'available': is_available,
            'capacity_remaining': sport_data['capacity']['max_players'] if is_available else 0,
            'peak_hour': 17 <= hour <= 21
        })
    
    return slots

def calculate_popularity_score(sport_id):
    """Calculate popularity score for a sport (simulated)"""
    import random
    base_scores = {
        'football': 95,
        'basketball': 88,
        'tennis': 82,
        'badminton': 75,
        'swimming': 70,
        'gym_fitness': 90,
        'volleyball': 68,
        'cricket': 85
    }
    
    base = base_scores.get(sport_id, 70)
    # Add some randomness to simulate real-time changes
    return min(100, max(50, base + random.randint(-5, 5)))

def calculate_next_price_change():
    """Calculate when the next price change will occur"""
    now = datetime.now()
    
    # Price changes at 5 PM (peak start) and 9 PM (peak end)
    if now.hour < 17:
        next_change = now.replace(hour=17, minute=0, second=0, microsecond=0)
    elif now.hour < 21:
        next_change = now.replace(hour=21, minute=0, second=0, microsecond=0)
    else:
        # Next day 5 PM
        next_change = (now + timedelta(days=1)).replace(hour=17, minute=0, second=0, microsecond=0)
    
    return next_change.isoformat()
