from datetime import datetime, timedelta
from typing import List, Tuple

class InterviewActivity:
    """Represents an interview activity with start and end times"""
    def __init__(self, candidate_id: str, candidate_name: str, start_time: datetime, 
                 duration_minutes: int = 45):
        self.candidate_id = candidate_id
        self.candidate_name = candidate_name
        self.start_time = start_time
        self.duration_minutes = duration_minutes
        self.end_time = start_time + timedelta(minutes=duration_minutes)
    
    def conflicts_with(self, other: "InterviewActivity") -> bool:
        """Check if this interview conflicts with another"""
        # No conflict if this ends before or at the time other starts,
        # or if other ends before or at the time this starts
        return not (self.end_time <= other.start_time or other.end_time <= self.start_time)
    
    def __repr__(self):
        return f"Interview({self.candidate_name}, {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"


def schedule_non_conflicting_interviews(activities: List[InterviewActivity]) -> List[InterviewActivity]:
    """
    Schedule maximum non-conflicting interviews using Activity Selection Problem (Greedy).
    
    Greedy Strategy:
    1. Sort all activities by their finish time (earliest finish first)
    2. Select the first activity with earliest finish time
    3. Iterate through remaining activities:
       - If an activity's start time >= the last selected activity's end time, select it
    4. This guarantees maximum non-overlapping interviews in the available time
    
    Args:
        activities: List of InterviewActivity objects
    
    Returns:
        List of scheduled (non-conflicting) InterviewActivity objects
    
    Time Complexity: O(n log n) due to sorting
    Space Complexity: O(n) for the result list
    """
    if not activities:
        return []
    
    # Step 1: Sort by finish time (earliest finish first)
    sorted_activities = sorted(activities, key=lambda x: x.end_time)
    
    # Step 2: Select the first activity
    selected_schedule = [sorted_activities[0]]
    last_end_time = sorted_activities[0].end_time
    
    # Step 3 & 4: Greedily select remaining non-conflicting activities
    for activity in sorted_activities[1:]:
        if activity.start_time >= last_end_time:
            selected_schedule.append(activity)
            last_end_time = activity.end_time
    
    return selected_schedule


def generate_schedule_slots(start_date: datetime, end_date: datetime, 
                           slot_duration_minutes: int = 45,
                           break_minutes: int = 0) -> List[Tuple[datetime, datetime]]:
    """
    Generate available interview time slots for a given date range.
    
    Args:
        start_date: Start datetime of the day
        end_date: End datetime of the day
        slot_duration_minutes: Duration of each interview slot
        break_minutes: Minutes between interviews (buffer time)
    
    Returns:
        List of tuples: (start_time, end_time) for each available slot
    """
    slots = []
    current_time = start_date
    slot_interval = timedelta(minutes=slot_duration_minutes + break_minutes)
    
    while current_time + timedelta(minutes=slot_duration_minutes) <= end_date:
        slot_start = current_time
        slot_end = current_time + timedelta(minutes=slot_duration_minutes)
        slots.append((slot_start, slot_end))
        current_time += slot_interval
    
    return slots


def match_candidates_to_slots(candidate_ids: List[str], 
                              candidate_names: List[str],
                              available_slots: List[Tuple[datetime, datetime]],
                              slot_duration_minutes: int = 45) -> List[InterviewActivity]:
    """
    Assign candidates to available slots and return scheduled interviews.
    
    Args:
        candidate_ids: List of candidate IDs
        candidate_names: List of candidate names (must match length of IDs)
        available_slots: List of available time slots
        slot_duration_minutes: Duration of each interview
    
    Returns:
        List of InterviewActivity objects assigned to slots
    """
    activities = []
    
    for idx, (candidate_id, candidate_name) in enumerate(zip(candidate_ids, candidate_names)):
        if idx < len(available_slots):
            slot_start, slot_end = available_slots[idx]
            activity = InterviewActivity(
                candidate_id=candidate_id,
                candidate_name=candidate_name,
                start_time=slot_start,
                duration_minutes=slot_duration_minutes
            )
            activities.append(activity)
    
    return activities


def optimize_schedule(candidates: List[Tuple[str, str]], 
                     available_hours: Tuple[int, int] = (9, 17),
                     interview_duration: int = 45,
                     date: datetime = None) -> dict:
    """
    Create an optimized interview schedule for given candidates.
    
    Args:
        candidates: List of tuples (candidate_id, candidate_name)
        available_hours: Tuple of (start_hour, end_hour) in 24-hour format
        interview_duration: Duration of each interview in minutes
        date: The date to schedule interviews (default: today)
    
    Returns:
        Dictionary with scheduled interviews and statistics
    """
    if date is None:
        date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Generate available slots
    start_time = date.replace(hour=available_hours[0])
    end_time = date.replace(hour=available_hours[1])
    slots = generate_schedule_slots(start_time, end_time, interview_duration)
    
    # Create activities for each candidate
    activities = []
    for idx, (candidate_id, candidate_name) in enumerate(candidates):
        if idx < len(slots):
            slot_start, _ = slots[idx]
            activity = InterviewActivity(
                candidate_id=candidate_id,
                candidate_name=candidate_name,
                start_time=slot_start,
                duration_minutes=interview_duration
            )
            activities.append(activity)
    
    # Optimize schedule
    optimized_schedule = schedule_non_conflicting_interviews(activities)
    
    return {
        'total_candidates': len(candidates),
        'scheduled_interviews': len(optimized_schedule),
        'available_slots': len(slots),
        'schedule': [
            {
                'rank': idx + 1,
                'candidate_id': interview.candidate_id,
                'candidate_name': interview.candidate_name,
                'start_time': interview.start_time.isoformat(),
                'end_time': interview.end_time.isoformat()
            }
            for idx, interview in enumerate(optimized_schedule)
        ]
    }
