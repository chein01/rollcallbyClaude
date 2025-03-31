import Link from 'next/link';
import { Star, MapPin, Users, Calendar, CheckCircle2 } from 'lucide-react';
import { Event } from '@/types/event';
import './EventCard.css';
import { format, isToday } from 'date-fns';

interface EventCardProps {
  event: Event;
  onStarClick?: (eventId: string) => void;
  onCheckIn?: (eventId: string) => void;
}

export function EventCard({ event, onStarClick, onCheckIn }: EventCardProps) {
  const needsCheckIn = isToday(new Date(event.startDate)) && !event.isCheckedIn;

  return (
    <div className={`event-card ${needsCheckIn ? 'needs-checkin' : ''}`}>
      <div className="event-header">
        <div className="event-title-row">
          <h3 className="event-title">{event.title}</h3>
          <button
            className="event-stars-badge"
            onClick={() => onStarClick?.(event.id)}
            disabled={event.status === 'ended'}
          >
            <Star className="h-4 w-4" />
            <span>{event.stars}</span>
          </button>
        </div>
        <div className="event-time">
          <Calendar className="h-4 w-4" />
          <span>{format(new Date(event.startDate), 'dd/MM/yyyy HH:mm')}</span>
        </div>
      </div>

      <p className="event-description">{event.description}</p>

      <div className="event-footer">
        <div className="event-meta">
          <div className="event-location">
            <MapPin className="h-4 w-4" />
            <span>{event.location}</span>
          </div>
          <div className="event-participants">
            <Users className="h-4 w-4" />
            <span>{event.participants} participants</span>
          </div>
        </div>

        <div className="event-actions">
          {needsCheckIn && onCheckIn && (
            <button
              className="checkin-button pulse"
              onClick={() => onCheckIn(event.id)}
            >
              Check in now
            </button>
          )}
          {event.isCheckedIn && (
            <div className="checked-in-badge">
              <CheckCircle2 className="h-4 w-4" />
              <span>Checked in</span>
            </div>
          )}
          <Link
            href={`/events/${event.id}`}
            className="view-details-button"
          >
            View details
          </Link>
        </div>
      </div>
    </div>
  );
}

.event - action - button: not([disabled]) {
  @apply w - full text - center py - 2 px - 4 rounded - md bg - primary text - primary - foreground hover: bg - primary / 90 transition - colors relative overflow - hidden;
}

.event - action - button: not([disabled])::before {
  content: '';
  @apply absolute top - 0 left - 0 w - full h - full bg - white opacity - 0;
  transform: translateX(-100 %) skewX(-15deg);
  transition: transform 0.6s ease - out;
}

.event - action - button: not([disabled]): hover::before {
  transform: translateX(100 %) skewX(-15deg);
  @apply opacity - 20;
}

.event - action - button: not([disabled]):active {
  transform: translateY(1px);
}

.event - action - button[disabled] {
  @apply bg - muted text - muted - foreground cursor - not - allowed;
} 