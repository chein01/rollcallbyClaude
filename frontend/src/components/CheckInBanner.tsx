import { Event } from '@/types/event';
import { AlertCircle, X } from 'lucide-react';
import Link from 'next/link';
import { useState } from 'react';
import './CheckInBanner.css';

interface CheckInBannerProps {
  events: Event[];
}

export function CheckInBanner({ events }: CheckInBannerProps) {
  const [isVisible, setIsVisible] = useState(true);
  
  // Filter events that need check-in today
  const pendingEvents = events.filter(event => 
    new Date(event.startDate).toDateString() === new Date().toDateString() && 
    !event.isCheckedIn
  );

  if (!isVisible || pendingEvents.length === 0) {
    return null;
  }

  return (
    <div className="checkin-notification">
      <div className="notification-content">
        <AlertCircle className="notification-icon" />
        <p className="notification-text">
          {pendingEvents.length === 1 ? (
            <>
              You need to check in for <span className="event-name">{pendingEvents[0].title}</span>
            </>
          ) : (
            <>
              You have <span className="font-semibold">{pendingEvents.length} events</span> to check in today
            </>
          )}
        </p>
        <Link href="/checkin/today" className="notification-action">
          Check in now
        </Link>
      </div>
      <button 
        className="notification-close"
        onClick={() => setIsVisible(false)}
        aria-label="Close notification"
      >
        <X className="h-3 w-3" />
      </button>
    </div>
  );
} 