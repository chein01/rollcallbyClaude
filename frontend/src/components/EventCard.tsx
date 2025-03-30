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