import React, { useState, useEffect } from 'react';
import { CheckCircle, X, PartyPopper } from 'lucide-react';
import './CheckInBanner.css';
import { Event } from '@/types/event';

interface CheckInBannerProps {
  pendingEvents: Event[];
  onClose: () => void;
  lastCheckedInEvent?: Event;
}

export function CheckInBanner({
  pendingEvents,
  onClose,
  lastCheckedInEvent
}: CheckInBannerProps) {
  const [showSuccess, setShowSuccess] = useState<boolean>(false);

  // Show success notification when lastCheckedInEvent changes
  useEffect(() => {
    if (lastCheckedInEvent) {
      setShowSuccess(true);
    }
  }, [lastCheckedInEvent]);

  // If there are no pending events or we're showing a success message
  if (pendingEvents.length === 0 && !showSuccess) {
    return null;
  }

  // Show success message if we have a lastCheckedInEvent
  if (showSuccess && lastCheckedInEvent) {
    return (
      <div className="checkin-notification success" style={{ borderColor: '#10b981', backgroundColor: '#ecfdf5' }}>
        <div className="notification-content">
          <PartyPopper className="notification-icon success" style={{ color: '#059669' }} />
          <p className="notification-text success" style={{ color: '#047857' }}>
            Successfully checked in for <span className="event-name success" style={{ color: '#065f46' }}>{lastCheckedInEvent.title}</span>!
          </p>
        </div>
        <button className="notification-close success" onClick={onClose} aria-label="Close notification" style={{ color: '#059669' }}>
          <X size={16} />
        </button>
      </div>
    );
  }

  // Count how many events need check-in
  const eventCount = pendingEvents.length;
  const eventText = eventCount === 1 ? 'event' : 'events';

  return (
    <div className="checkin-notification">
      <div className="notification-content">
        <CheckCircle className="notification-icon" />
        <p className="notification-text">
          {eventCount === 1 ? (
            <>Please check in for <span className="event-name">{pendingEvents[0].title}</span></>
          ) : (
            <>You have {eventCount} {eventText} to check in today</>
          )}
        </p>
        <a href="/dashboard" className="notification-action">Check in now</a>
      </div>
      <button
        className="notification-close"
        onClick={onClose}
        aria-label="Close notification"
      >
        <X size={16} />
      </button>
    </div>
  );
} 