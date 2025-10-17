"""
Management command to seed the database with all 16 sports and their positions.
Run with: python manage.py seed_sports
"""
from django.core.management.base import BaseCommand
from recruiting.models import Sport, Position


class Command(BaseCommand):
    help = 'Seeds the database with all 16 sports and their positions/events'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting sports data seeding...'))

        # Define all 16 sports with their positions
        sports_data = {
            'FOOTBALL': {
                'name': 'Football',
                'description': 'American Football',
                'has_positions': True,
                'has_events': False,
                'has_weight_classes': False,
                'positions': [
                    ('QB', 'Quarterback', 'QB', 'Offense', 1),
                    ('RB', 'Running Back', 'RB', 'Offense', 2),
                    ('FB', 'Fullback', 'FB', 'Offense', 3),
                    ('WR', 'Wide Receiver', 'WR', 'Offense', 4),
                    ('TE', 'Tight End', 'TE', 'Offense', 5),
                    ('OL_C', 'Center', 'C', 'Offensive Line', 6),
                    ('OL_G', 'Guard', 'G', 'Offensive Line', 7),
                    ('OL_T', 'Tackle', 'T', 'Offensive Line', 8),
                    ('DL_DE', 'Defensive End', 'DE', 'Defensive Line', 9),
                    ('DL_DT', 'Defensive Tackle', 'DT', 'Defensive Line', 10),
                    ('LB_MLB', 'Middle Linebacker', 'MLB', 'Linebacker', 11),
                    ('LB_OLB', 'Outside Linebacker', 'OLB', 'Linebacker', 12),
                    ('DB_CB', 'Cornerback', 'CB', 'Defensive Back', 13),
                    ('DB_S', 'Safety', 'S', 'Defensive Back', 14),
                    ('K', 'Kicker', 'K', 'Special Teams', 15),
                    ('P', 'Punter', 'P', 'Special Teams', 16),
                ]
            },
            'BASKETBALL': {
                'name': 'Basketball',
                'description': 'Basketball',
                'has_positions': True,
                'has_events': False,
                'has_weight_classes': False,
                'positions': [
                    ('PG', 'Point Guard', 'PG', 'Guard', 1),
                    ('SG', 'Shooting Guard', 'SG', 'Guard', 2),
                    ('SF', 'Small Forward', 'SF', 'Forward', 3),
                    ('PF', 'Power Forward', 'PF', 'Forward', 4),
                    ('C', 'Center', 'C', 'Center', 5),
                ]
            },
            'SOCCER': {
                'name': 'Soccer',
                'description': 'Soccer / Football',
                'has_positions': True,
                'has_events': False,
                'has_weight_classes': False,
                'positions': [
                    ('GK', 'Goalkeeper', 'GK', 'Goalkeeper', 1),
                    ('CB', 'Center Back', 'CB', 'Defense', 2),
                    ('LB', 'Left Back', 'LB', 'Defense', 3),
                    ('RB', 'Right Back', 'RB', 'Defense', 4),
                    ('CDM', 'Defensive Midfielder', 'CDM', 'Midfield', 5),
                    ('CM', 'Central Midfielder', 'CM', 'Midfield', 6),
                    ('CAM', 'Attacking Midfielder', 'CAM', 'Midfield', 7),
                    ('LW', 'Left Wing', 'LW', 'Forward', 8),
                    ('RW', 'Right Wing', 'RW', 'Forward', 9),
                    ('ST', 'Striker', 'ST', 'Forward', 10),
                    ('CF', 'Center Forward', 'CF', 'Forward', 11),
                ]
            },
            'TRACK_FIELD': {
                'name': 'Track & Field',
                'description': 'Track and Field / Athletics',
                'has_positions': False,
                'has_events': True,
                'has_weight_classes': False,
                'positions': [
                    # Sprints
                    ('100M', '100 Meters', '100m', 'Sprint', 1),
                    ('200M', '200 Meters', '200m', 'Sprint', 2),
                    ('400M', '400 Meters', '400m', 'Sprint', 3),
                    # Middle Distance
                    ('800M', '800 Meters', '800m', 'Middle Distance', 4),
                    ('1600M', '1600 Meters (Mile)', '1600m', 'Middle Distance', 5),
                    # Distance
                    ('3200M', '3200 Meters (2 Mile)', '3200m', 'Distance', 6),
                    ('5K', '5000 Meters', '5K', 'Distance', 7),
                    ('10K', '10000 Meters', '10K', 'Distance', 8),
                    # Hurdles
                    ('110MH', '110m Hurdles', '110mH', 'Hurdles', 9),
                    ('100MH', '100m Hurdles', '100mH', 'Hurdles', 10),
                    ('300MH', '300m Hurdles', '300mH', 'Hurdles', 11),
                    ('400MH', '400m Hurdles', '400mH', 'Hurdles', 12),
                    # Jumps
                    ('HIGH_JUMP', 'High Jump', 'HJ', 'Jumps', 13),
                    ('LONG_JUMP', 'Long Jump', 'LJ', 'Jumps', 14),
                    ('TRIPLE_JUMP', 'Triple Jump', 'TJ', 'Jumps', 15),
                    ('POLE_VAULT', 'Pole Vault', 'PV', 'Jumps', 16),
                    # Throws
                    ('SHOT_PUT', 'Shot Put', 'SP', 'Throws', 17),
                    ('DISCUS', 'Discus', 'DT', 'Throws', 18),
                    ('JAVELIN', 'Javelin', 'JT', 'Throws', 19),
                    ('HAMMER', 'Hammer Throw', 'HT', 'Throws', 20),
                    # Multi-Events
                    ('DECATHLON', 'Decathlon', 'DEC', 'Multi-Event', 21),
                    ('HEPTATHLON', 'Heptathlon', 'HEP', 'Multi-Event', 22),
                ]
            },
            'SWIMMING': {
                'name': 'Swimming',
                'description': 'Competitive Swimming',
                'has_positions': False,
                'has_events': True,
                'has_weight_classes': False,
                'positions': [
                    # Freestyle
                    ('50_FREE', '50 Freestyle', '50 Free', 'Freestyle', 1),
                    ('100_FREE', '100 Freestyle', '100 Free', 'Freestyle', 2),
                    ('200_FREE', '200 Freestyle', '200 Free', 'Freestyle', 3),
                    ('500_FREE', '500 Freestyle', '500 Free', 'Freestyle', 4),
                    ('1000_FREE', '1000 Freestyle', '1000 Free', 'Freestyle', 5),
                    ('1650_FREE', '1650 Freestyle', '1650 Free', 'Freestyle', 6),
                    # Backstroke
                    ('100_BACK', '100 Backstroke', '100 Back', 'Backstroke', 7),
                    ('200_BACK', '200 Backstroke', '200 Back', 'Backstroke', 8),
                    # Breaststroke
                    ('100_BREAST', '100 Breaststroke', '100 Breast', 'Breaststroke', 9),
                    ('200_BREAST', '200 Breaststroke', '200 Breast', 'Breaststroke', 10),
                    # Butterfly
                    ('100_FLY', '100 Butterfly', '100 Fly', 'Butterfly', 11),
                    ('200_FLY', '200 Butterfly', '200 Fly', 'Butterfly', 12),
                    # Individual Medley
                    ('200_IM', '200 Individual Medley', '200 IM', 'IM', 13),
                    ('400_IM', '400 Individual Medley', '400 IM', 'IM', 14),
                ]
            },
            'DIVING': {
                'name': 'Diving',
                'description': 'Springboard and Platform Diving',
                'has_positions': True,
                'has_events': False,
                'has_weight_classes': False,
                'positions': [
                    ('1M', '1-Meter Springboard', '1m', 'Springboard', 1),
                    ('3M', '3-Meter Springboard', '3m', 'Springboard', 2),
                    ('PLATFORM', '10-Meter Platform', '10m', 'Platform', 3),
                ]
            },
            'LACROSSE': {
                'name': 'Lacrosse',
                'description': 'Lacrosse',
                'has_positions': True,
                'has_events': False,
                'has_weight_classes': False,
                'positions': [
                    ('ATTACK', 'Attack', 'A', 'Offense', 1),
                    ('MIDFIELD', 'Midfield', 'M', 'Midfield', 2),
                    ('DEFENSE', 'Defense', 'D', 'Defense', 3),
                    ('GOALIE', 'Goalie', 'G', 'Goalie', 4),
                    ('FOGO', 'Face-Off Get Off', 'FOGO', 'Specialist', 5),
                ]
            },
            'VOLLEYBALL': {
                'name': 'Volleyball',
                'description': 'Volleyball',
                'has_positions': True,
                'has_events': False,
                'has_weight_classes': False,
                'positions': [
                    ('OH', 'Outside Hitter', 'OH', 'Hitter', 1),
                    ('OPP', 'Opposite Hitter', 'OPP', 'Hitter', 2),
                    ('MB', 'Middle Blocker', 'MB', 'Blocker', 3),
                    ('S', 'Setter', 'S', 'Setter', 4),
                    ('L', 'Libero', 'L', 'Defense', 5),
                    ('DS', 'Defensive Specialist', 'DS', 'Defense', 6),
                ]
            },
            'WRESTLING': {
                'name': 'Wrestling',
                'description': 'Wrestling',
                'has_positions': False,
                'has_events': False,
                'has_weight_classes': True,
                'positions': [
                    ('106', '106 lbs', '106', 'Weight Class', 1),
                    ('113', '113 lbs', '113', 'Weight Class', 2),
                    ('120', '120 lbs', '120', 'Weight Class', 3),
                    ('126', '126 lbs', '126', 'Weight Class', 4),
                    ('132', '132 lbs', '132', 'Weight Class', 5),
                    ('138', '138 lbs', '138', 'Weight Class', 6),
                    ('144', '144 lbs', '144', 'Weight Class', 7),
                    ('150', '150 lbs', '150', 'Weight Class', 8),
                    ('157', '157 lbs', '157', 'Weight Class', 9),
                    ('165', '165 lbs', '165', 'Weight Class', 10),
                    ('175', '175 lbs', '175', 'Weight Class', 11),
                    ('190', '190 lbs', '190', 'Weight Class', 12),
                    ('215', '215 lbs', '215', 'Weight Class', 13),
                    ('285', '285 lbs (Heavyweight)', '285', 'Weight Class', 14),
                ]
            },
            'TENNIS': {
                'name': 'Tennis',
                'description': 'Tennis',
                'has_positions': True,
                'has_events': False,
                'has_weight_classes': False,
                'positions': [
                    ('SINGLES', 'Singles Player', 'Singles', 'Singles', 1),
                    ('DOUBLES', 'Doubles Player', 'Doubles', 'Doubles', 2),
                ]
            },
            'GOLF': {
                'name': 'Golf',
                'description': 'Golf',
                'has_positions': False,
                'has_events': False,
                'has_weight_classes': False,
                'positions': [
                    ('GOLFER', 'Golfer', 'Golfer', 'Individual', 1),
                ]
            },
            'ROWING': {
                'name': 'Rowing',
                'description': 'Rowing / Crew',
                'has_positions': True,
                'has_events': False,
                'has_weight_classes': False,
                'positions': [
                    # By Boat Type
                    ('EIGHT', '8+ (Eight)', '8+', 'Sweep', 1),
                    ('FOUR', '4+ (Four)', '4+', 'Sweep', 2),
                    ('PAIR', '2- (Pair)', '2-', 'Sweep', 3),
                    ('SINGLE', '1x (Single Scull)', '1x', 'Sculling', 4),
                    ('DOUBLE', '2x (Double Scull)', '2x', 'Sculling', 5),
                    ('QUAD', '4x (Quad Scull)', '4x', 'Sculling', 6),
                    # Weight Categories
                    ('HEAVYWEIGHT', 'Heavyweight', 'HWT', 'Weight', 7),
                    ('LIGHTWEIGHT', 'Lightweight', 'LWT', 'Weight', 8),
                ]
            },
            'ICE_HOCKEY': {
                'name': 'Ice Hockey',
                'description': 'Ice Hockey',
                'has_positions': True,
                'has_events': False,
                'has_weight_classes': False,
                'positions': [
                    ('C', 'Center', 'C', 'Forward', 1),
                    ('LW', 'Left Wing', 'LW', 'Forward', 2),
                    ('RW', 'Right Wing', 'RW', 'Forward', 3),
                    ('D', 'Defenseman', 'D', 'Defense', 4),
                    ('G', 'Goalie', 'G', 'Goalie', 5),
                ]
            },
            'FIELD_HOCKEY': {
                'name': 'Field Hockey',
                'description': 'Field Hockey',
                'has_positions': True,
                'has_events': False,
                'has_weight_classes': False,
                'positions': [
                    ('GK', 'Goalkeeper', 'GK', 'Goalkeeper', 1),
                    ('DEF', 'Defender', 'DEF', 'Defense', 2),
                    ('MID', 'Midfielder', 'MID', 'Midfield', 3),
                    ('FWD', 'Forward', 'FWD', 'Forward', 4),
                ]
            },
            'GYMNASTICS': {
                'name': 'Gymnastics',
                'description': 'Artistic Gymnastics',
                'has_positions': False,
                'has_events': True,
                'has_weight_classes': False,
                'positions': [
                    ('VAULT', 'Vault', 'VT', 'Event', 1),
                    ('BARS', 'Uneven Bars', 'UB', 'Event', 2),
                    ('BEAM', 'Balance Beam', 'BB', 'Event', 3),
                    ('FLOOR', 'Floor Exercise', 'FX', 'Event', 4),
                    ('ALL_AROUND', 'All-Around', 'AA', 'All-Around', 5),
                ]
            },
        }

        created_count = 0
        updated_count = 0
        position_count = 0

        for sport_code, sport_info in sports_data.items():
            # Create or update Sport
            sport, created = Sport.objects.update_or_create(
                code=sport_code,
                defaults={
                    'name': sport_info['name'],
                    'description': sport_info['description'],
                    'is_active': True,
                    'has_positions': sport_info['has_positions'],
                    'has_events': sport_info['has_events'],
                    'has_weight_classes': sport_info['has_weight_classes'],
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'[+] Created sport: {sport.name}'))
            else:
                updated_count += 1
                self.stdout.write(f'  Updated sport: {sport.name}')

            # Create positions for this sport
            for pos_code, pos_name, pos_abbr, pos_category, display_order in sport_info['positions']:
                position, pos_created = Position.objects.update_or_create(
                    sport=sport,
                    code=pos_code,
                    defaults={
                        'name': pos_name,
                        'abbreviation': pos_abbr,
                        'category': pos_category,
                        'display_order': display_order,
                        'description': f'{pos_name} in {sport.name}',
                    }
                )
                if pos_created:
                    position_count += 1

        self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] Seeding complete!'))
        self.stdout.write(self.style.SUCCESS(f'   Sports created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'   Sports updated: {updated_count}'))
        self.stdout.write(self.style.SUCCESS(f'   Positions created: {position_count}'))
        self.stdout.write(self.style.SUCCESS(f'\nRecruitApp is ready to track athletes across all 16 sports!'))
