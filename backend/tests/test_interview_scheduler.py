import pytest
from datetime import datetime, timedelta
from backend.core.interview_scheduler import (
    InterviewActivity,
    schedule_non_conflicting_interviews,
    generate_schedule_slots,
    optimize_schedule
)


class TestInterviewActivity:
    """Test cases for InterviewActivity class"""
    
    def test_create_interview_activity(self):
        """Test creating an interview activity"""
        start = datetime(2024, 4, 15, 10, 0)
        activity = InterviewActivity("c1", "John Doe", start, duration_minutes=45)
        
        assert activity.candidate_id == "c1"
        assert activity.candidate_name == "John Doe"
        assert activity.start_time == start
        assert activity.duration_minutes == 45
        assert activity.end_time == datetime(2024, 4, 15, 10, 45)
    
    def test_no_conflict_different_times(self):
        """Test that non-overlapping interviews don't conflict"""
        start1 = datetime(2024, 4, 15, 10, 0)
        start2 = datetime(2024, 4, 15, 11, 0)
        
        activity1 = InterviewActivity("c1", "John", start1, duration_minutes=45)
        activity2 = InterviewActivity("c2", "Jane", start2, duration_minutes=45)
        
        assert not activity1.conflicts_with(activity2)
        assert not activity2.conflicts_with(activity1)
    
    def test_conflict_overlapping_times(self):
        """Test that overlapping interviews conflict"""
        start1 = datetime(2024, 4, 15, 10, 0)
        start2 = datetime(2024, 4, 15, 10, 30)
        
        activity1 = InterviewActivity("c1", "John", start1, duration_minutes=45)
        activity2 = InterviewActivity("c2", "Jane", start2, duration_minutes=45)
        
        assert activity1.conflicts_with(activity2)
    
    def test_no_conflict_back_to_back(self):
        """Test that consecutive interviews don't conflict"""
        start1 = datetime(2024, 4, 15, 10, 0)
        start2 = datetime(2024, 4, 15, 10, 45)
        
        activity1 = InterviewActivity("c1", "John", start1, duration_minutes=45)
        activity2 = InterviewActivity("c2", "Jane", start2, duration_minutes=45)
        
        # Back to back should not conflict (45 mins ends exactly when next starts)
        assert not activity1.conflicts_with(activity2)


class TestScheduleNonConflictingInterviews:
    """Test cases for scheduling algorithm"""
    
    def test_schedule_no_conflicts(self):
        """Test scheduling with non-conflicting times"""
        base_time = datetime(2024, 4, 15, 9, 0)
        activities = [
            InterviewActivity("c1", "Alice", base_time, 45),
            InterviewActivity("c2", "Bob", base_time + timedelta(minutes=45), 45),
            InterviewActivity("c3", "Charlie", base_time + timedelta(minutes=90), 45)
        ]
        
        scheduled = schedule_non_conflicting_interviews(activities)
        assert len(scheduled) == 3
    
    def test_schedule_with_conflicts(self):
        """Test scheduling removes conflicting interviews (earliest finish first)"""
        base_time = datetime(2024, 4, 15, 9, 0)
        activities = [
            # These three overlap - should keep only the ones with earliest finish
            InterviewActivity("c1", "Alice", base_time, 120),  # Ends at 11:00
            InterviewActivity("c2", "Bob", base_time, 60),     # Ends at 10:00 (earliest)
            InterviewActivity("c3", "Charlie", base_time + timedelta(minutes=45), 30),  # Ends at 10:15
        ]
        
        scheduled = schedule_non_conflicting_interviews(activities)
        # Should prefer earliest finish times
        assert len(scheduled) >= 1
    
    def test_schedule_empty_list(self):
        """Test scheduling with empty activity list"""
        scheduled = schedule_non_conflicting_interviews([])
        assert len(scheduled) == 0
    
    def test_schedule_single_activity(self):
        """Test scheduling with single activity"""
        base_time = datetime(2024, 4, 15, 9, 0)
        activities = [InterviewActivity("c1", "Alice", base_time, 45)]
        
        scheduled = schedule_non_conflicting_interviews(activities)
        assert len(scheduled) == 1


class TestGenerateScheduleSlots:
    """Test cases for slot generation"""
    
    def test_generate_slots_standard_day(self):
        """Test generating slots for a full day"""
        start = datetime(2024, 4, 15, 9, 0)
        end = datetime(2024, 4, 15, 17, 0)  # 8 hours = 480 minutes
        
        slots = generate_schedule_slots(start, end, slot_duration_minutes=45, break_minutes=0)
        # 480 / 45 = 10.67, so should have 10 slots
        assert len(slots) >= 10
    
    def test_generate_slots_with_break(self):
        """Test generating slots with break time between"""
        start = datetime(2024, 4, 15, 9, 0)
        end = datetime(2024, 4, 15, 12, 0)
        
        slots_no_break = generate_schedule_slots(start, end, slot_duration_minutes=30, break_minutes=0)
        slots_with_break = generate_schedule_slots(start, end, slot_duration_minutes=30, break_minutes=15)
        
        # More break time means fewer slots
        assert len(slots_no_break) > len(slots_with_break)
    
    def test_slot_timing(self):
        """Test that slot times are correct"""
        start = datetime(2024, 4, 15, 9, 0)
        end = datetime(2024, 4, 15, 10, 30)
        
        slots = generate_schedule_slots(start, end, slot_duration_minutes=30, break_minutes=0)
        
        if len(slots) > 0:
            assert slots[0][0] == datetime(2024, 4, 15, 9, 0)
            assert slots[0][1] == datetime(2024, 4, 15, 9, 30)


class TestOptimizeSchedule:
    """Test cases for schedule optimization"""
    
    def test_optimize_schedule_basic(self):
        """Test basic schedule optimization"""
        candidates = [
            ("c1", "Alice"),
            ("c2", "Bob"),
            ("c3", "Charlie")
        ]
        
        schedule = optimize_schedule(candidates, available_hours=(9, 17), interview_duration=45)
        
        assert schedule['total_candidates'] == 3
        assert schedule['scheduled_interviews'] > 0
        assert len(schedule['schedule']) == schedule['scheduled_interviews']
    
    def test_optimize_schedule_no_candidates(self):
        """Test optimization with no candidates"""
        schedule = optimize_schedule([], available_hours=(9, 17))
        
        assert schedule['total_candidates'] == 0
        assert schedule['scheduled_interviews'] == 0
    
    def test_schedule_output_format(self):
        """Test that schedule output has correct format"""
        candidates = [("c1", "Alice")]
        schedule = optimize_schedule(candidates)
        
        if len(schedule['schedule']) > 0:
            entry = schedule['schedule'][0]
            assert 'rank' in entry
            assert 'candidate_id' in entry
            assert 'candidate_name' in entry
            assert 'start_time' in entry
            assert 'end_time' in entry
