# Sports Profile Database Schema

## Executive Summary

This document defines the comprehensive database schema for tracking athletic performance metrics across 16 high school sports with established college recruiting pipelines. The schema is designed to handle multi-position athletes, role-specific metrics, and the complex relationships between positions, events, and performance statistics.

## Design Philosophy

### Core Principles
1. **Flexibility**: Athletes can have multiple positions/roles within a sport
2. **Specificity**: Each position has unique metrics relevant to college recruiters
3. **Scalability**: Easy to add new sports or metrics without breaking existing data
4. **Normalization**: Avoid data duplication while maintaining query performance
5. **Time-series**: Track performance improvements over time

### Schema Architecture

```
User (Django Auth)
  ↓
UserProfile (Core recruiting info)
  ↓
SportProfile (One per sport the athlete plays)
  ↓
├─ PositionProfile (Multiple positions per sport)
│    ↓
│    └─ PositionMetrics (JSON field for position-specific stats)
│
├─ PerformanceEntry (Time-series performance data)
│
└─ CompetitionResult (Tournament/meet results, honors, accolades)
```

---

## Sport-by-Sport Recruiting Metrics

### 1. FOOTBALL

**Positions**: QB, RB, WR, TE, OL (C, G, T), DL (DE, DT), LB (MLB, OLB), DB (CB, S), K, P

**Common Metrics** (all positions):
- Height (inches)
- Weight (lbs)
- 40-Yard Dash (seconds)
- Vertical Jump (inches)
- Broad Jump (inches)
- Bench Press (reps at 185 lbs for HS/225 lbs for college)
- 20-Yard Shuttle (seconds)
- 3-Cone Drill (seconds)
- Hand Size (inches)
- Arm Length (inches)

**Position-Specific Metrics**:
- **QB**: Completion %, Passing Yards, TDs, INTs, QB Rating
- **RB**: Rushing Yards, YPC, TDs, Receptions, Fumbles
- **WR/TE**: Receptions, Receiving Yards, YPC, TDs, Drops
- **OL**: Pancake Blocks, Sacks Allowed, Games Started
- **DL**: Tackles, Sacks, TFL, QB Hits, Forced Fumbles
- **LB**: Tackles, Solo Tackles, TFL, Sacks, INTs, PBUs
- **DB**: INTs, PBUs, Tackles, Forced Fumbles, Return TDs

---

### 2. BASKETBALL

**Positions**: PG, SG, SF, PF, C (can play multiple)

**Common Metrics**:
- Height (ft/inches)
- Weight (lbs)
- Wingspan (inches)
- Standing Reach (inches)
- Vertical Jump (inches - standing and max)
- Lane Agility Time (seconds)

**Performance Statistics**:
- PPG (Points Per Game)
- RPG (Rebounds Per Game)
- APG (Assists Per Game)
- SPG (Steals Per Game)
- BPG (Blocks Per Game)
- FG% (Field Goal Percentage)
- 3PT% (Three-Point Percentage)
- FT% (Free Throw Percentage)
- TO/G (Turnovers Per Game)
- Minutes Per Game
- +/- (Plus/Minus)

---

### 3. SOCCER

**Positions**: GK, CB, LB, RB, CDM, CM, CAM, LW, RW, ST/CF (can play multiple)

**Field Player Metrics**:
- Games Played
- Minutes Played
- Goals
- Goals Per Game
- Assists
- Shots
- Shots on Goal
- Shot Accuracy %
- Total Points (Goals + Assists)
- Game-Winning Goals

**Goalkeeper Metrics**:
- Games Started
- Minutes Played
- Win/Loss/Tie Record
- Goals Against
- Goals Against Average
- Shots on Goal Faced
- Saves
- Save Percentage
- Shutouts
- Distribution Accuracy %

---

### 4. TRACK & FIELD

**Event Categories**: Sprints, Middle Distance, Distance, Hurdles, Jumps, Throws, Multi-Events

**Sprint Events** (100m, 200m, 400m):
- Personal Record Time (FAT preferred)
- Season Best
- Wind-Adjusted PR

**Middle Distance** (800m, 1600m):
- Personal Record Time
- Split Times (if applicable)

**Distance** (3200m, 5k, 10k):
- Personal Record Time
- Mile splits

**Hurdles** (110mH, 300mH/400mH, 100mH):
- Personal Record Time
- Hurdle height

**Jumps** (High, Long, Triple, Pole Vault):
- Personal Record Distance/Height
- Approach speed (for long/triple)

**Throws** (Shot Put, Discus, Javelin, Hammer):
- Personal Record Distance
- Implement weight

**Multi-Events** (Decathlon, Heptathlon):
- Total Points
- Individual event performances

---

### 5. SWIMMING

**Stroke Types**: Freestyle, Backstroke, Breaststroke, Butterfly, IM (Individual Medley)

**Distance Categories**: 50, 100, 200, 400, 500, 1000, 1650 (yards/meters)

**Metrics** (per event):
- Personal Record Time
- Season Best Time
- Course Type (SCY/SCM/LCM - Short Course Yards/Meters, Long Course Meters)
- Split Times (for 200+ events)
- Relay Splits (50 Free, 100 Free for relay potential)
- Power Index Score (recruiting metric)

**Additional**:
- Underwater Kick Distance
- Turns Speed
- Reaction Time

---

### 6. DIVING

**Boards**: 1-Meter Springboard, 3-Meter Springboard, Platform (10m)

**Metrics**:
- Best Score (per board type)
- Average Score
- Degree of Difficulty Range (1.2-4.1+)
- Dive List (Forward, Back, Reverse, Inward, Twisting groups)
- Number of dives mastered per group

**Technique Evaluation**:
- Approach Quality (1-10)
- Take-off Quality (1-10)
- Execution Quality (1-10)
- Entry Quality (1-10)

---

### 7. LACROSSE

**Positions**: Attack, Midfield, Defense, Goalie, FOGO (Face-Off Get Off)

**Field Player Metrics**:
- Games Played
- Goals
- Goals Per Game
- Assists
- Assists Per Game
- Points (Goals + Assists)
- Points Per Game
- Ground Balls
- Ground Balls Per Game
- Caused Turnovers
- Turnovers
- Shot Percentage
- Face-Off Win Percentage (for FOGO/Midfield)

**Goalie Metrics**:
- Games Played
- Minutes Played
- Saves
- Saves Per Game
- Goals Against
- Goals Against Average
- Save Percentage
- Win/Loss Record

---

### 8. VOLLEYBALL

**Positions**: OH (Outside Hitter), OPP (Opposite), MB (Middle Blocker), S (Setter), L (Libero), DS (Defensive Specialist)

**Common Physical Metrics**:
- Height (ft/inches)
- Standing Reach (inches)
- Block Jump (inches)
- Approach Jump (inches)
- Attack Touch Height (inches)

**Performance Statistics**:
- Kills Per Set
- Kill Percentage
- Hitting Percentage (Kills - Errors) / Total Attempts
- Blocks Per Set
- Solo Blocks
- Block Assists
- Digs Per Set
- Aces Per Set
- Service Errors
- Serving Percentage
- Assists Per Set (for setters)
- Passing Percentage (for liberos/DS)

---

### 9. WRESTLING

**Weight Classes**: 106, 113, 120, 126, 132, 138, 144, 150, 157, 165, 175, 190, 215, 285 (lbs)

**Metrics**:
- Weight Class
- Season Record (Wins-Losses)
- Career Record
- Pins
- Technical Falls
- Major Decisions
- Decisions
- Takedowns Per Match
- Reversals Per Match
- Escapes Per Match
- Near Falls
- Shot Success Rate (%)
- Tournament Placements (State, Regional, National)
- Rankings (State, National)

---

### 10. TENNIS

**Positions**: Singles Player, Doubles Player (can be both)

**Rating Systems**:
- UTR Rating (Universal Tennis Rating - 1-16 scale, most important)
- USTA Ranking (National and Sectional)
- ITF Ranking (if applicable)
- TennisRecruiting.net Star Rating

**Match Statistics**:
- Singles Win/Loss Record
- Doubles Win/Loss Record
- Tournament Results (list of significant tournaments and placements)
- Level of Competition (National, Regional, Sectional)

**Performance Metrics** (if tracked):
- First Serve Percentage
- Aces Per Match
- Double Faults Per Match
- Break Point Conversion Rate
- Winners vs Unforced Errors Ratio

---

### 11. GOLF

**Metrics**:
- 18-Hole Scoring Average
- 9-Hole Scoring Average
- Tournament Handicap (computed from ranked tournaments only)
- Official USGA Handicap Index
- Best 18-Hole Score
- Best Tournament Finish
- Number of Tournaments Played
- Course Yardage (minimum 6,000 yards for consideration)

**Advanced Analytics** (if available):
- Driving Distance Average
- Driving Accuracy %
- Greens in Regulation %
- Scrambling %
- Putts Per Round
- Sand Save %
- Strokes Gained (Off Tee, Approach, Around Green, Putting)

---

### 12. ROWING

**Boat Types**: 8+ (Eight), 4+ (Four), 2- (Pair), 1x (Single)
**Weight Categories**: Heavyweight, Lightweight

**Critical Metrics**:
- 2000m Erg Time (2k) - **MOST IMPORTANT**
- 6000m Erg Time (6k)
- 2k Split (pace per 500m)
- Height (inches)
- Weight (lbs)
- Watts Average (power output)

**On-Water Performance**:
- Boat Type and Position (Stroke, 7-seat, 6-seat, etc.)
- Seat Racing Results
- Regatta Results
- Best 2k On-Water Time

**Physical**:
- Wingspan
- Leg Length

---

### 13. ICE HOCKEY

**Positions**: C (Center), LW/RW (Wing), D (Defense), G (Goalie)

**Forward Metrics**:
- Goals
- Assists
- Points
- Plus/Minus (+/-)
- Penalty Minutes
- Power Play Goals
- Shorthanded Goals
- Game-Winning Goals
- Shots on Goal
- Shooting Percentage
- Face-Off Win Percentage (Centers)

**Defenseman Metrics**:
- Goals
- Assists
- Points
- Plus/Minus (+/-)
- Blocked Shots
- Hits
- Penalty Minutes

**Goalie Metrics**:
- Games Played
- Wins/Losses
- Goals Against Average (GAA)
- Save Percentage
- Shutouts
- Minutes Played

**Skating Speed** (if measured):
- Forward Skating Speed
- Backward Skating Speed
- Lateral Agility

---

### 14. FIELD HOCKEY

**Positions**: GK, Defenders, Midfielders, Forwards

**Field Player Metrics**:
- Goals
- Goals Per Game
- Assists
- Assists Per Game
- Points Per Game
- Penalty Corners Earned
- Defensive Saves
- Games Played

**Goalkeeper Metrics**:
- Saves
- Saves Per Game
- Save Percentage
- Goals Against
- Goals Against Average
- Shutouts
- Defensive Saves (as field player)

---

### 15. GYMNASTICS

**Events**: Vault, Uneven Bars, Balance Beam, Floor Exercise, All-Around

**Scoring** (per event):
- Best Score (out of 10.0)
- Average Score
- Start Value (9.4-10.0)
- Season High
- Competition Level (Level 10, Elite, NCAA)

**Difficulty Composition**:
- Number of A Skills
- Number of B Skills
- Number of C Skills
- Number of D Skills
- Number of E Skills
- Connection Bonuses Earned

**Vault Specific**:
- Vault Type (e.g., Yurchenko Full, Yurchenko 1.5)
- Start Value (varies by vault)

**All-Around**:
- All-Around Best Score
- All-Around Average

---

## Database Schema Design

### Core Tables

#### `UserProfile` (existing - extend)
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    graduation_year = models.IntegerField()
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    sat_score = models.IntegerField(null=True, blank=True)
    act_score = models.IntegerField(null=True, blank=True)
    # ... other profile fields
```

#### `Sport` (lookup table)
```python
class Sport(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)  # e.g., 'FOOTBALL', 'BASKETBALL'
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    # Metadata
    has_positions = models.BooleanField(default=True)
    has_events = models.BooleanField(default=False)  # Track & Field, Swimming
    has_weight_classes = models.BooleanField(default=False)  # Wrestling
```

#### `Position` (lookup table)
```python
class Position(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='positions')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)  # e.g., 'QB', 'PG', 'GK'
    abbreviation = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True)  # e.g., 'Offense', 'Defense', 'Sprint', 'Distance'

    class Meta:
        unique_together = ('sport', 'code')
```

#### `MetricDefinition` (lookup table)
```python
class MetricDefinition(models.Model):
    METRIC_TYPES = [
        ('PHYSICAL', 'Physical Measurement'),
        ('PERFORMANCE', 'Performance Statistic'),
        ('TIME', 'Time-based'),
        ('DISTANCE', 'Distance-based'),
        ('PERCENTAGE', 'Percentage'),
        ('COUNT', 'Count/Number'),
        ('SCORE', 'Score'),
        ('RATING', 'Rating/Ranking'),
    ]

    UNITS = [
        ('SECONDS', 'Seconds'),
        ('MINUTES', 'Minutes'),
        ('INCHES', 'Inches'),
        ('FEET', 'Feet'),
        ('POUNDS', 'Pounds'),
        ('METERS', 'Meters'),
        ('YARDS', 'Yards'),
        ('PERCENT', 'Percentage'),
        ('COUNT', 'Count'),
        ('POINTS', 'Points'),
        ('NONE', 'No Unit'),
    ]

    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='metrics')
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True, related_name='metrics')

    name = models.CharField(max_length=100)  # e.g., '40 Yard Dash', 'Vertical Jump'
    code = models.CharField(max_length=50)  # e.g., 'forty_yard_dash', 'vertical_jump'
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    unit = models.CharField(max_length=20, choices=UNITS)

    description = models.TextField(blank=True)
    is_required = models.BooleanField(default=False)
    is_common = models.BooleanField(default=False)  # Applies to all positions in sport

    # Validation
    min_value = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    max_value = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)

    # Display
    display_order = models.IntegerField(default=0)

    class Meta:
        unique_together = ('sport', 'position', 'code')
```

#### `SportProfile` (main athlete-sport relationship)
```python
class SportProfile(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sport_profiles')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)

    # Core Info
    years_experience = models.IntegerField()
    current_team = models.CharField(max_length=200, blank=True)
    team_level = models.CharField(max_length=100, blank=True)  # e.g., 'Varsity', 'JV', 'Club'
    jersey_number = models.CharField(max_length=10, blank=True)

    # Status
    is_primary_sport = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user_profile', 'sport')
```

#### `PositionProfile` (athlete plays multiple positions)
```python
class PositionProfile(models.Model):
    sport_profile = models.ForeignKey(SportProfile, on_delete=models.CASCADE, related_name='position_profiles')
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    is_primary = models.BooleanField(default=False)
    proficiency_level = models.IntegerField(default=1)  # 1-5 scale

    # Position-specific metrics stored as JSON for flexibility
    metrics = models.JSONField(default=dict, blank=True)
    # Example: {'forty_yard_dash': '4.5', 'vertical_jump': '32', 'bench_press': '15'}

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### `PerformanceEntry` (time-series performance tracking)
```python
class PerformanceEntry(models.Model):
    sport_profile = models.ForeignKey(SportProfile, on_delete=models.CASCADE, related_name='performances')
    position_profile = models.ForeignKey(PositionProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='performances')

    # Context
    date = models.DateField()
    season = models.CharField(max_length=100)  # e.g., '2024 Fall', '2024-2025'
    event_name = models.CharField(max_length=200, blank=True)  # Game, meet, match name
    opponent = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)

    # Performance data (flexible JSON)
    metrics = models.JSONField(default=dict)
    # Example: {'goals': 2, 'assists': 1, 'shots': 5, 'minutes_played': 75}

    # Notes
    notes = models.TextField(blank=True)
    video_url = models.URLField(blank=True)

    # Verification
    is_verified = models.BooleanField(default=False)
    verified_by = models.CharField(max_length=200, blank=True)  # Coach, official timing, etc.

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### `CompetitionResult` (honors, accolades, tournament placements)
```python
class CompetitionResult(models.Model):
    RESULT_TYPES = [
        ('CHAMPIONSHIP', 'Championship'),
        ('TOURNAMENT', 'Tournament Placement'),
        ('AWARD', 'Individual Award'),
        ('HONOR', 'Team/Individual Honor'),
        ('RANKING', 'Ranking Achievement'),
        ('RECORD', 'Record Set'),
    ]

    sport_profile = models.ForeignKey(SportProfile, on_delete=models.CASCADE, related_name='competition_results')

    result_type = models.CharField(max_length=20, choices=RESULT_TYPES)
    competition_name = models.CharField(max_length=200)
    competition_level = models.CharField(max_length=100)  # State, Regional, National, International

    date = models.DateField()
    placement = models.CharField(max_length=100, blank=True)  # '1st Place', 'Finalist', 'All-Conference'

    description = models.TextField()
    significance = models.TextField(blank=True)  # Why this matters for recruiting

    # Supporting Evidence
    certificate_url = models.URLField(blank=True)
    article_url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
```

---

## Sample Queries & Use Cases

### Use Case 1: Get all metrics for a multi-position football player
```python
# John is a RB/WR who also plays special teams
sport_profile = SportProfile.objects.get(user_profile__user=john, sport__code='FOOTBALL')

for position_profile in sport_profile.position_profiles.all():
    print(f"Position: {position_profile.position.name}")
    print(f"Metrics: {position_profile.metrics}")
    # Output might be:
    # Position: Running Back
    # Metrics: {'forty_yard_dash': '4.45', 'vertical_jump': '38', 'rushing_yards': '1200', 'rushing_tds': '15'}
    # Position: Wide Receiver
    # Metrics: {'receptions': '25', 'receiving_yards': '450', 'receiving_tds': '5'}
```

### Use Case 2: Track improvement over time (Track & Field)
```python
# Get all 100m times for Sarah in chronological order
performances = PerformanceEntry.objects.filter(
    sport_profile__user_profile__user=sarah,
    sport_profile__sport__code='TRACK_FIELD',
    position_profile__position__code='100M'
).order_by('date')

for perf in performances:
    print(f"{perf.date}: {perf.metrics['time']} seconds")
```

### Use Case 3: Generate recruiting profile
```python
def generate_recruiting_profile(user):
    profiles = SportProfile.objects.filter(user_profile__user=user, is_active=True)

    for sport_profile in profiles:
        sport_data = {
            'sport': sport_profile.sport.name,
            'positions': [],
            'best_performances': [],
            'honors': []
        }

        # Get all positions and metrics
        for pos_profile in sport_profile.position_profiles.all():
            sport_data['positions'].append({
                'name': pos_profile.position.name,
                'metrics': pos_profile.metrics,
                'is_primary': pos_profile.is_primary
            })

        # Get recent best performances
        recent_performances = sport_profile.performances.filter(
            is_verified=True
        ).order_by('-date')[:5]

        # Get competition results
        honors = sport_profile.competition_results.all().order_by('-date')

        return sport_data
```

---

## Migration Strategy

### Phase 1: Core Schema (Week 1-2)
1. Create `Sport`, `Position`, `MetricDefinition` lookup tables
2. Populate with all 16 sports and their positions
3. Define common and position-specific metrics

### Phase 2: User Integration (Week 3)
1. Create `SportProfile`, `PositionProfile` models
2. Migrate existing simple `SportProfile` data to new schema
3. Build admin interface for managing profiles

### Phase 3: Performance Tracking (Week 4)
1. Create `PerformanceEntry` model
2. Build UI for athletes to log performances
3. Create time-series charts and improvement tracking

### Phase 4: Competition & Honors (Week 5)
1. Create `CompetitionResult` model
2. Build accolades/honors tracking
3. Integrate with recruiting profile generator

### Phase 5: AI Integration (Week 6)
1. Train Coach Alex to ask position-specific questions
2. Build automated metric collection through conversation
3. Create AI-generated recruiting summaries

---

## AI Agent Integration Strategy

### Conversational Metric Collection

Coach Alex should intelligently gather metrics based on:
1. Sport identified
2. Position(s) identified
3. Required vs optional metrics
4. Previous conversation history

**Example Flow**:
```
Coach Alex: "I see you play football. What position do you primarily play?"
User: "I'm a running back, but I also play some receiver."

Coach Alex: "Great! As a running back and receiver, there are some key metrics
that college coaches look at. Let's start with the basics - do you know your
40-yard dash time?"

User: "Yes, I ran a 4.5 at our combine."

Coach Alex: "Excellent 4.5! That's a very competitive time. How about your
vertical jump? This is important for both positions."
```

### Metric Validation

The AI should validate metrics in real-time:
- Check if values are within reasonable ranges
- Flag outliers for verification
- Suggest retesting if times seem too good/bad
- Ask for verification source (coach, official timing, etc.)

### Progress Tracking

Coach Alex should:
- Celebrate improvements ("Your 100m time dropped 0.3 seconds - great progress!")
- Identify areas for improvement
- Compare to recruiting standards
- Suggest action items for metric improvement

---

## Future Enhancements

1. **Video Integration**: Link performance entries to game film
2. **Social Proof**: Connect to official timing services, MaxPreps, Athletic.net
3. **Recruiting Standards**: Add Division I/II/III benchmark data
4. **Coach Verification**: Allow coaches to verify athlete metrics
5. **Team Profiles**: Track team-level statistics
6. **Multi-Sport Athletes**: Compare metrics across sports
7. **Scholarship Calculator**: Estimate scholarship potential based on metrics
8. **Tournament Brackets**: Integrate tournament results automatically

---

## Conclusion

This schema provides a robust, flexible foundation for tracking athletic performance across all major high school sports. The JSON field approach for metrics allows rapid addition of new metrics without schema migrations, while the normalized structure maintains data integrity and query performance.

The multi-position support ensures athletes can showcase their versatility - a critical differentiator in the recruiting process. Time-series performance tracking demonstrates improvement over time, and the competition results table captures the accolades that make recruiting profiles stand out.

Next steps: Review this schema, approve the approach, then begin implementing the Django models and admin interface.
