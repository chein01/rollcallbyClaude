import { Event } from '@/types/event';
import { isToday } from 'date-fns';
import './CheckInBadge.css';

interface CheckInBadgeProps {
  events: Event[];
}

export function CheckInBadge({ events }: CheckInBadgeProps) {
  // Count events that need check-in today
  const pendingCount = events.filter(event => 
    isToday(new Date(event.startDate)) && 
    !event.isCheckedIn
  ).length;

  if (pendingCount === 0) {
    return null;
  }

  return (
    <span className="checkin-badge" title={`${pendingCount} events need check-in`}>
      {pendingCount}
    </span>
  );
} 