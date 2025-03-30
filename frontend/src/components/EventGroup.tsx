'use client';

import { Event } from '@/types/event';
import { EventCard } from './EventCard';
import { Clock, CheckCircle2, AlertCircle } from 'lucide-react';
import { isToday, isFuture, isPast, isThisWeek } from 'date-fns';
import './EventGroup.css';

interface EventGroupProps {
  events: Event[];
  onStarClick?: (eventId: string) => void;
  onCheckIn?: (eventId: string) => void;
}

export function EventGroup({ events, onStarClick, onCheckIn }: EventGroupProps) {
  // Phân loại sự kiện
  const categorizeEvents = (events: Event[]) => {
    const now = new Date();
    
    return events.reduce((acc, event) => {
      const startDate = new Date(event.startDate);
      const endDate = new Date(event.endDate);
      
      if (isToday(startDate)) {
        acc.today.push(event);
      } else if (isFuture(startDate) && isThisWeek(startDate)) {
        acc.upcoming.push(event);
      } else if (isPast(endDate)) {
        acc.past.push(event);
      }
      
      return acc;
    }, {
      today: [] as Event[],
      upcoming: [] as Event[],
      past: [] as Event[]
    });
  };

  const { today, upcoming, past } = categorizeEvents(events);

  // Sắp xếp sự kiện theo thời gian
  const sortByStartDate = (a: Event, b: Event) => {
    return new Date(a.startDate).getTime() - new Date(b.startDate).getTime();
  };

  // Xác định trạng thái của sự kiện
  const getEventStatus = (event: Event) => {
    const now = new Date();
    const startDate = new Date(event.startDate);
    const endDate = new Date(event.endDate);

    if (isPast(endDate)) {
      return {
        label: 'Completed',
        icon: CheckCircle2,
        className: 'completed'
      };
    }

    if (isToday(startDate) && !event.isCheckedIn) {
      return {
        label: 'Need Check-in',
        icon: AlertCircle,
        className: 'need-checkin'
      };
    }

    if (isFuture(startDate)) {
      return {
        label: 'Upcoming',
        icon: Clock,
        className: 'upcoming'
      };
    }

    return {
      label: 'Checked in',
      icon: CheckCircle2,
      className: 'checked-in'
    };
  };

  return (
    <div className="event-groups">
      {/* Today's Events */}
      {today.length > 0 && (
        <div className="event-group today-events">
          <h2 className="group-title">
            Today's Events
            <span className="event-count">{today.length}</span>
          </h2>
          <div className="events-grid">
            {today.sort(sortByStartDate).map(event => {
              const status = getEventStatus(event);
              return (
                <div key={event.id} className="event-wrapper">
                  <div className={`event-status ${status.className}`}>
                    <status.icon className="h-4 w-4" />
                    <span>{status.label}</span>
                  </div>
                  <EventCard 
                    event={event}
                    onStarClick={onStarClick}
                    onCheckIn={onCheckIn}
                  />
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Upcoming Events */}
      {upcoming.length > 0 && (
        <div className="event-group">
          <h2 className="group-title">
            Upcoming Events
            <span className="event-count">{upcoming.length}</span>
          </h2>
          <div className="events-grid">
            {upcoming.sort(sortByStartDate).map(event => {
              const status = getEventStatus(event);
              return (
                <div key={event.id} className="event-wrapper">
                  <div className={`event-status ${status.className}`}>
                    <status.icon className="h-4 w-4" />
                    <span>{status.label}</span>
                  </div>
                  <EventCard 
                    event={event}
                    onStarClick={onStarClick}
                    onCheckIn={onCheckIn}
                  />
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Past Events */}
      {past.length > 0 && (
        <div className="event-group">
          <h2 className="group-title">
            Past Events
            <span className="event-count">{past.length}</span>
          </h2>
          <div className="events-grid">
            {past.sort((a, b) => new Date(b.startDate).getTime() - new Date(a.startDate).getTime()).map(event => {
              const status = getEventStatus(event);
              return (
                <div key={event.id} className="event-wrapper">
                  <div className={`event-status ${status.className}`}>
                    <status.icon className="h-4 w-4" />
                    <span>{status.label}</span>
                  </div>
                  <EventCard 
                    event={event}
                    onStarClick={onStarClick}
                    onCheckIn={onCheckIn}
                  />
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
} 